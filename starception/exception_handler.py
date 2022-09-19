import hashlib
import html
import inspect
import jinja2
import os
import sys
import traceback
import typing
from markupsafe import Markup
from pprint import pformat
from starlette.datastructures import URL
from starlette.requests import Request
from starlette.responses import HTMLResponse, PlainTextResponse, Response


def get_relative_filename(path: str) -> str:
    for sys_path in reversed(sorted(sys.path)):
        if sys_path in path:
            path = path.replace(sys_path + "/", "")
            break
    return path


def format_qual_name(obj: typing.Any) -> str:
    if inspect.isclass(obj):
        module_name = obj.__module__
        type_name = obj.__name__
    else:
        module_name = obj.__class__.__module__
        type_name = obj.__class__.__name__

    if module_name == "builtins":
        module_name = ""
    if module_name:
        return f"{module_name}.{type_name}"
    return type_name


def frame_id(frame: inspect.FrameInfo) -> str:
    hash = hashlib.md5()
    hash.update(f"{frame.filename}{frame.lineno}".encode())
    return hash.hexdigest()


def is_vendor(frame: inspect.FrameInfo) -> bool:
    return sys.exec_prefix in frame.filename.replace('./', '')


def get_package_name(frame: inspect.FrameInfo) -> str:
    return typing.cast(str, frame.frame.f_globals.get("__package__", "").split(".")[0])


def get_symbol(frame: inspect.FrameInfo) -> str:
    symbol = ""
    if "self" in frame.frame.f_locals:
        try:
            symbol = type(frame.frame.f_locals["self"]).__name__
        except Exception:
            return 'n/a'

    if "cls" in frame.frame.f_locals and frame.frame.f_locals["cls"]:
        symbol = frame.frame.f_locals["cls"].__name__

    # if we cannot detect class name then just a method name will be rendered
    function = frame.function
    if symbol:
        function = symbol + "." + function
    return function


def get_package_dir(frame: inspect.FrameInfo) -> str:
    return frame.filename.replace(get_relative_filename(frame.filename), "")


def format_variable(var_value: typing.Any) -> str:
    try:
        return pformat(var_value, indent=2)
    except Exception as ex:
        return repr(ex)


def _hide_url_secrets(value: str) -> str:
    url = URL(value)
    if url.password:
        url = url.replace(password='*' * 8)
    return str(url)


def mask_secrets(value: str, key: str) -> str:
    key = key.lower()
    if key.endswith('_url'):
        return _hide_url_secrets(value)

    if any(
        [
            "key" in key,
            "token" in key,
            "password" in key,
            "secret" in key,
        ]
    ):
        return Markup(
            '<span data-reveal="{value}" style="cursor: pointer">{stars} <i>(click to reveal)</i></span> '.format(
                stars="*" * 8, value=value
            )
        )
    return value


jinja = jinja2.Environment(loader=jinja2.PackageLoader(__name__))
jinja.filters.update(
    {
        'symbol': get_symbol,
        'frame_id': frame_id,
        'is_vendor': is_vendor,
        'mask_secrets': mask_secrets,
        'package_dir': get_package_dir,
        'package_name': get_package_name,
        'format_variable': format_variable,
        'relative_filename': get_relative_filename,
    }
)


def exception_handler(request: Request, exc: Exception) -> Response:
    accept = request.headers.get("accept", "")

    if "text/html" in accept:
        content = generate_html(request, exc)
        return HTMLResponse(content, status_code=500)

    content = generate_plain_text(exc)
    return PlainTextResponse(content, status_code=500)


def generate_plain_text(exc: Exception) -> str:
    return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))


def generate_html(request: Request, exc: Exception, limit: int = 7) -> str:
    traceback_obj = traceback.TracebackException.from_exception(exc, capture_locals=True)

    template = jinja.get_template('index.html')
    return template.render(
        {
            'exception_class': format_qual_name(traceback_obj.exc_type),
            'error_message': str(exc) or '""',
            'request_method': request.method,
            'request_path': request.url.path,
            'frames': inspect.getinnerframes(exc.__traceback__, limit) if exc.__traceback__ else [],
            'request_info': {
                "Method": request.method,
                "Path": request.url.path,
                "Path params": Markup(
                    "<br>".join(
                        [
                            f'<span class="text-muted">{k}</span> = {html.escape(mask_secrets(str(v), k))}'
                            for k, v in request.path_params.items()
                        ]
                    )
                ),
                "Query params": Markup(
                    "<br>".join(
                        [
                            f'<span class="text-muted">{k}</span> = {html.escape(mask_secrets(str(v), k))}'
                            for k, v in request.query_params.items()
                        ]
                    )
                ),
                "Content type": request.headers.get("Content-Type", ""),
                "Client": f"{request.client.host}:{request.client.port}" if request.client else 'unknown',
            },
            'request_headers': request.headers,
            'request_state': {k: v for k, v in request.state._state.items()},
            'session': _get_session_info(request),
            'cookies': request.cookies,
            'app_state': {k: v for k, v in request.app.state._state.items()} if 'app' in request.scope else {},
            'platform': {
                "Python version": sys.version,
                "Platform": sys.platform,
                "Python": sys.executable,
                "Paths": Markup("<br>".join(sys.path)),
            },
            'environment': os.environ,
            'solution': getattr(exc, 'solution', None),
        }
    )


def _get_session_info(request: Request) -> typing.Dict[str, typing.Any]:
    try:
        return dict(request.session if 'session' in request.scope else {})
    except Exception:
        return {}
