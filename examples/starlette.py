import os.path
import typing
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from starlette.templating import Jinja2Templates

from starception import install_error_handler

this_dir = os.path.dirname(__file__)
templates = Jinja2Templates(os.path.join(this_dir, "templates"))


class WithHintError(Exception):
    solution = (
        "The connection to the database cannot be established. "
        "Either the database server is down or connection credentials are invalid."
    )


class StrError:
    """Value that raises exception during conversion to string."""

    def __str__(self) -> str:
        raise ValueError("hahaha crash <b>me</b>")


# /
# Tests: secrets masking (token, password, api_key), StrError in state,
#        app state, request state, query params
def index_view(request: Request) -> typing.NoReturn:
    token = "mytoken"  # noqa: F841 — local var visible in frame locals
    password = "hunter2"  # noqa: F841
    request.state.token = "state_secret_token"
    request.state.error = StrError()
    request.app.state.app_token = "app_secret_token"
    request.app.state.error = StrError()
    raise ValueError("Basic exception — check secrets masking and state display")


# /xss
# Tests: XSS safety — exception message and path params with HTML in them
def xss_view(request: Request) -> typing.NoReturn:
    evil = request.path_params.get("payload", "<script>alert(1)</script>")
    raise ValueError(f"<script>alert('xss')</script> payload={evil}")


# /hint
# Tests: solution hint on exception class
def hint_view(request: Request) -> typing.NoReturn:
    raise WithHintError("Oops, something really went wrong...")


# /chain
# Tests: __cause__ exception chain (explicit chaining with `from`)
def raise_level2(base: Exception) -> None:
    raise ValueError("This is the second cause") from base


def raise_level1(exc: Exception) -> None:
    raise_level2(exc)


def chain_view(request: Request) -> None:
    request.state.token = "mytoken"
    request.app.state.app_token = "app mytoken"
    try:
        raise WithHintError("This is the root cause")
    except Exception as exc:
        try:
            raise_level1(exc)
        except Exception as exc2:
            raise TypeError("Oops, something really went wrong...") from exc2


# /implicit-chain
# Tests: __context__ exception chain (implicit chaining — raise inside except)
def implicit_chain_view(request: Request) -> typing.NoReturn:
    try:
        raise ValueError("Original error (implicit context)")
    except ValueError:
        raise RuntimeError("Secondary error raised inside except block — no `from`")


# /notes
# Tests: exception notes (Python 3.11+ add_note())
def exception_notes_view(request: Request) -> typing.NoReturn:
    exc = ValueError("Exception with notes")
    exc.add_note("Note 1: check your configuration file.")
    exc.add_note("Note 2: ensure the service is running.")
    raise exc


# /notes-chain
# Tests: each exception in chain has its own notes
def notes_chain_view(request: Request) -> typing.NoReturn:
    try:
        root = OSError("Root cause")
        root.add_note("Root note: disk may be full.")
        raise root
    except OSError as exc:
        wrapper = RuntimeError("Wrapped error")
        wrapper.add_note("Wrapper note: retry after a moment.")
        raise wrapper from exc


# /secret-url
# Tests: URL password masking in state/env values
def secret_url_view(request: Request) -> typing.NoReturn:
    request.state.database_url = "postgresql://user:supersecretpassword@localhost/mydb"
    request.state.redis_url = "redis://:redispassword@localhost:6379/0"
    raise RuntimeError("Check that URL passwords are masked in request state")


# /css  /template  /javascript
# Tests: code snippet syntax highlighting for different file types
def template_view(request: Request) -> Response:
    return templates.TemplateResponse("index.html", {"request": request})


def javascript_view(request: Request) -> Response:
    return templates.TemplateResponse("jstest.js", {"request": request})


def css_view(request: Request) -> Response:
    return templates.TemplateResponse("csstest.css", {"request": request})


install_error_handler(editor="vscode")
app = Starlette(
    debug=True,
    routes=[
        Route("/", index_view),
        Route("/xss", xss_view),
        Route("/hint", hint_view),
        Route("/chain", chain_view),
        Route("/implicit-chain", implicit_chain_view),
        Route("/notes", exception_notes_view),
        Route("/notes-chain", notes_chain_view),
        Route("/secret-url", secret_url_view),
        Route("/css", css_view),
        Route("/template", template_view),
        Route("/javascript", javascript_view),
    ],
)
