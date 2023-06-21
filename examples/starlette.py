import os.path
import typing
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from starlette.templating import Jinja2Templates

from starception import install_error_handler

this_dir = os.path.dirname(__file__)
templates = Jinja2Templates(os.path.join(this_dir, 'templates'))


class WithHintError(Exception):
    solution = (
        'The connection to the database cannot be established. '
        'Either the database server is down or connection credentials are invalid.'
    )


def index_view(request: Request) -> typing.NoReturn:
    class StrError:
        """Value that raises exception during conversion to string."""

        def __str__(self):
            raise ValueError('hahaha crash <b>me</b>')

    token = 'mytoken'  # noqa
    request.state.token = 'mytoken'

    request.app.state.app_token = 'app mytoken'
    request.state.error = StrError()
    request.app.state.error = StrError()
    raise ValueError('This is the first cause')


def raise_level2(base: Exception) -> None:
    raise ValueError('This is the second cause') from base


def raise_level1(exc: Exception) -> None:
    raise_level2(exc)


def chain_view(request: Request) -> None:
    request.state.token = 'mytoken'
    request.app.state.app_token = 'app mytoken'
    try:
        raise WithHintError('This is the first cause')
    except Exception as exc:
        try:
            raise_level1(exc)
        except Exception as exc:
            raise TypeError('Oops, something really went wrong...') from exc


def hint_view(request: Request) -> typing.NoReturn:
    raise WithHintError('Oops, something really went wrong...')


def template_view(request: Request) -> Response:
    return templates.TemplateResponse('index.html', {'request': request})


def javascript_view(request: Request) -> Response:
    return templates.TemplateResponse('jstest.js', {'request': request})


def css_view(request: Request) -> Response:
    return templates.TemplateResponse('csstest.css', {'request': request})


install_error_handler(editor='vscode')
app = Starlette(
    debug=True,
    routes=[
        Route('/', index_view),
        Route('/hint', hint_view),
        Route('/chain', chain_view),
        Route('/css', css_view),
        Route('/template', template_view),
        Route('/javascript', javascript_view),
    ],
)
