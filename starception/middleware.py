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
from starlette.requests import Request
from starlette.responses import HTMLResponse, PlainTextResponse, Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send


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
        symbol = frame.frame.f_locals["self"].__class__.__name__

    if "cls" in frame.frame.f_locals:
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


def mask_secrets(value: str, key: str) -> str:
    key = key.lower()
    if any(
        [
            "key" in key,
            "token" in key,
            "password" in key,
            "secret" in key,
        ]
    ):
        return "*" * 8
    return value


EDITORS = {'pycharm': 'pycharm://open?file={path}&line={line}'}


def generate_file_uri(path: str, line: int, editor: str) -> str:
    uri = EDITORS.get(editor, '').format(path=path, line=line)
    if not uri:
        uri = 'file://' + path
    return uri


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


class StarceptionMiddleware:
    """
    Handles returning 500 responses when a server error occurs.

    If 'debug' is set, then traceback responses will be returned,
    otherwise the designated 'handler' will be called.

    This middleware class should generally be used to wrap *everything*
    else up, so that unhandled exceptions anywhere in the stack
    always result in an appropriate 500 response.
    """

    def __init__(
        self,
        app: ASGIApp,
        debug: bool = False,
        editor: typing.Optional[str] = os.environ.get('EDITOR', ''),
    ) -> None:
        self.app = app
        self.debug = debug
        self.editor = editor

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        response_started = False

        async def _send(message: Message) -> None:
            nonlocal response_started, send

            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, receive, _send)
        except Exception as exc:
            if not response_started:
                request = Request(scope)
                if self.debug:
                    # In debug mode, return traceback responses.
                    response = self.debug_response(request, exc)
                else:
                    # Use our default 500 error handler.
                    response = self.error_response(request, exc)

                await response(scope, receive, send)

            # We always continue to raise the exception.
            # This allows servers to log the error, or allows test clients
            # to optionally raise the error within the test case.
            raise exc

    def generate_html(self, request: Request, exc: Exception, limit: int = 7) -> str:
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
                                f'<span class="text-muted">{k}</span> = {html.escape(str(v))}'
                                for k, v in request.path_params.items()
                            ]
                        )
                    ),
                    "Query params": Markup(
                        "<br>".join(
                            [
                                f'<span class="text-muted">{k}</span> = {html.escape(str(v))}'
                                for k, v in request.query_params.items()
                            ]
                        )
                    ),
                    "Content type": request.headers.get("Content-Type", ""),
                    "Client": f"{request.client.host}:{request.client.port}" if request.client else 'unknown',
                },
                'request_headers': request.headers,
                'request_state': {k: v for k, v in request.state._state.items()},
                'session': request.session if 'session' in request.scope else {},
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

    def generate_plain_text(self, exc: Exception) -> str:
        return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

    def debug_response(self, request: Request, exc: Exception) -> Response:
        accept = request.headers.get("accept", "")

        if "text/html" in accept:
            content = self.generate_html(request, exc)
            return HTMLResponse(content, status_code=500)
        content = self.generate_plain_text(exc)
        return PlainTextResponse(content, status_code=500)

    def error_response(self, request: Request, exc: Exception) -> Response:
        return PlainTextResponse("Internal Server Error", status_code=500)
