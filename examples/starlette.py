import os.path
import typing
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from starlette.templating import Jinja2Templates

from starception import install_error_handler, set_theme

this_dir = os.path.dirname(__file__)
templates = Jinja2Templates(os.path.join(this_dir, 'templates'))


class WithHintError(Exception):
    solution = (
        'The connection to the database cannot be established. '
        'Either the database server is down or connection credentials are invalid.'
    )


def index_view(request: Request) -> typing.NoReturn:
    token = 'mytoken'  # noqa
    request.state.token = 'mytoken'
    request.app.state.app_token = 'app mytoken'
    raise ValueError('This is the first cause')


def chain_view(request: Request) -> typing.NoReturn:
    request.state.token = 'mytoken'
    request.app.state.app_token = 'app mytoken'
    try:
        raise WithHintError('This is the first cause')
    except Exception as exc:
        try:
            raise ValueError('This is the second cause') from exc
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


set_theme('dark')
install_error_handler()
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
