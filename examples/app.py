import typing
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.routing import Route

from starception.middleware import StarceptionMiddleware


class WithHintError(Exception):
    solution = (
        'The connection to the database cannot be established. '
        'Either the database server is down or connection credentials are invalid.'
    )


def index_view(request: Request) -> typing.NoReturn:
    request.state.token = 'hujokin'
    request.app.state.app_token = 'app hujokin'
    request.session['user_id'] = 1
    request.session['user_password'] = 'password'
    raise TypeError('Oops, something really went wrong...')


def hint_view(request: Request) -> typing.NoReturn:
    request.state.token = 'hujokin'
    request.app.state.app_token = 'app hujokin'
    request.session['user_id'] = 1
    request.session['user_password'] = 'password'
    raise WithHintError('Oops, something really went wrong...')


app = Starlette(
    routes=[Route('/', index_view), Route('/hint', hint_view)],
    middleware=[
        Middleware(StarceptionMiddleware, debug=True),
        Middleware(SessionMiddleware, secret_key=True),
    ],
)
