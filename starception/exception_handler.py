import dataclasses
import hashlib
import html
import inspect
import jinja2
import markupsafe
import os
import sys
import traceback
import typing
from markupsafe import Markup
from pprint import pformat
from starlette.datastructures import URL
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, PlainTextResponse, Response
from urllib.parse import quote, quote_plus

_editor: str = "none"
open_link_templates: typing.Dict[str, str] = {
    "none": "file://{path}",
    "vscode": "vscode://file/{path}:{lineno}",
}


def set_editor(name: str) -> None:
    """
    Set code editor.

    We will use it to generate file open links. Built-in editors: vscode.
    """
    global _editor
    _editor = name


def add_link_template(editor: str, template: str) -> None:
    """
    Add open file link template. The template accepts two format keys: path and
    lineno.

    Example:
        add_link_template('vscode', 'vscode://file/{path}:{lineno}')
    """
    open_link_templates[editor] = template


def to_ide_link(path: str, lineno: int) -> str:
    """Generate open file link for current editor."""
    template = open_link_templates.get(_editor, open_link_templates["none"])
    return template.format(path=quote(path, safe="/"), lineno=lineno)


def install_error_handler(editor: str = "") -> None:
    """
    Replace Starlette debug exception handler in-place.

    May be, someday, we won't need it. See
    https://github.com/encode/starlette/discussions/1867
    """
    set_editor(editor)

    def bound_handler(self: ServerErrorMiddleware, request: Request, exc: Exception) -> Response:
        return exception_handler(request, exc)

    setattr(ServerErrorMiddleware, "debug_response", bound_handler)


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
    return sys.exec_prefix in frame.filename.replace("./", "")


def get_package_name(frame: inspect.FrameInfo) -> str:
    return typing.cast(str, frame.frame.f_globals.get("__package__", "").split(".")[0])


def get_symbol(frame: inspect.FrameInfo) -> str:
    symbol = ""
    if "self" in frame.frame.f_locals:
        try:
            symbol = type(frame.frame.f_locals["self"]).__name__
        except Exception:
            return "n/a"

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
        url = url.replace(password="*" * 8)
    return str(url)


def _masked_secret_markup(display: str, reveal: str) -> Markup:
    return Markup(
        '<span class="masked-secret">{display} <button class="btn-reveal" data-reveal="{reveal}">reveal</button></span>'.format(
            display=html.escape(display), reveal=html.escape(reveal)
        )
    )


def mask_secrets(value: str, key: str) -> str:
    key = key.lower()
    if key.endswith("_url"):
        masked = _hide_url_secrets(value)
        if masked != value:
            return _masked_secret_markup(masked, value)
        return masked

    if any(
        [
            "key" in key,
            "token" in key,
            "password" in key,
            "secret" in key,
        ]
    ):
        return _masked_secret_markup("*" * 8, str(value))
    return value


def highlight(value: str, filename: str) -> str:
    try:
        from pygments import highlight as pygments_highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import CssLexer, HtmlLexer, JavascriptLexer, PythonLexer

        *_, extension = os.path.splitext(filename)
        mapping = {
            ".py": PythonLexer(),
            ".htm": HtmlLexer(),
            ".html": HtmlLexer(),
            ".css": CssLexer(),
            ".js": JavascriptLexer(),
        }
        lexer = mapping.get(extension)
        if lexer:
            return Markup(pygments_highlight(value, lexer, HtmlFormatter(nowrap=True)))
        return value
    except ImportError:
        return markupsafe.escape(value)


def save_str(value: typing.Any) -> str:
    try:
        return str(value)
    except Exception as ex:
        return Markup(f'<span class="text-error">ERROR</span>: {html.escape(str(ex))}')


jinja = jinja2.Environment(loader=jinja2.PackageLoader(__name__), autoescape=True)
jinja.filters.update(
    {
        "symbol": get_symbol,
        "save_str": save_str,
        "frame_id": frame_id,
        "is_vendor": is_vendor,
        "highlight": highlight,
        "to_ide_link": to_ide_link,
        "mask_secrets": mask_secrets,
        "package_dir": get_package_dir,
        "package_name": get_package_name,
        "format_variable": format_variable,
        "relative_filename": get_relative_filename,
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


@dataclasses.dataclass
class StackItem:
    exc: BaseException
    frames: typing.List[inspect.FrameInfo]
    has_vendor_frames: bool
    solution: str
    notes: typing.List[str]


def _get_chained_exception(exc: BaseException) -> typing.Optional[BaseException]:
    if exc.__cause__ is not None:
        return exc.__cause__
    if not exc.__suppress_context__ and exc.__context__ is not None:
        return exc.__context__
    return None


def generate_html(request: Request, exc: Exception, limit: int = 15) -> str:
    frames = inspect.getinnerframes(exc.__traceback__, limit) if exc.__traceback__ else []
    stack = [
        StackItem(
            exc=exc,
            solution=getattr(exc, "solution", ""),
            notes=getattr(exc, "__notes__", []),
            frames=frames,
            has_vendor_frames=any(is_vendor(f) for f in frames),
        )
    ]
    cause: typing.Optional[BaseException] = _get_chained_exception(exc)
    while cause:
        frames = inspect.getinnerframes(cause.__traceback__, limit) if cause.__traceback__ else []
        stack.append(
            StackItem(
                exc=cause,
                solution=getattr(cause, "solution", ""),
                notes=getattr(cause, "__notes__", []),
                frames=frames,
                has_vendor_frames=any(is_vendor(f) for f in frames),
            )
        )
        cause = _get_chained_exception(cause)

    template = jinja.get_template("index.html")
    return template.render(
        {
            "search_query": quote_plus(f"{format_qual_name(type(exc))} {str(exc)}"),
            "exception_class": format_qual_name(type(exc)),
            "error_message": str(exc) or '""',
            "stack": stack,
            "request_method": request.method,
            "request_path": request.url.path,
            "request_info": {
                "Method": request.method,
                "Path": request.url.path,
                "Path params": Markup(
                    "<br>".join(
                        [
                            f'<span class="text-muted">{markupsafe.escape(k)}</span> = {markupsafe.escape(mask_secrets(str(v), k))}'
                            for k, v in request.path_params.items()
                        ]
                    )
                ),
                "Query params": Markup(
                    "<br>".join(
                        [
                            f'<span class="text-muted">{markupsafe.escape(k)}</span> = {markupsafe.escape(mask_secrets(str(v), k))}'
                            for k, v in request.query_params.items()
                        ]
                    )
                ),
                "Content type": request.headers.get("Content-Type", ""),
                "Client": f"{request.client.host}:{request.client.port}" if request.client else "unknown",
            },
            "request_headers": request.headers,
            "request_state": {k: v for k, v in request.state._state.items()},
            "session": _get_session_info(request),
            "cookies": request.cookies,
            "app_state": {k: v for k, v in request.app.state._state.items()} if "app" in request.scope else {},
            "platform": {
                "Python version": sys.version,
                "Platform": sys.platform,
                "Python": sys.executable,
                "Paths": Markup("<br>".join(markupsafe.escape(p) for p in sys.path)),
            },
            "environment": os.environ,
            "solution": getattr(exc, "solution", None),
            "notes": getattr(exc, "__notes__", []),
        }
    )


def _get_session_info(request: Request) -> typing.Dict[str, typing.Any]:
    try:
        return dict(request.session if "session" in request.scope else {})
    except Exception:
        return {}
