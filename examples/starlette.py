import typing
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.routing import Route

from starception import StarceptionMiddleware


class WithHintError(Exception):
    solution = (
        'The connection to the database cannot be established. '
        'Either the database server is down or connection credentials are invalid.'
    )


def index_view(request: Request) -> typing.NoReturn:
    request.state.token = 'mytoken'
    request.app.state.app_token = 'app mytoken'
    raise TypeError('Oops, something really went wrong... <b>ahhaha</b> after')


def hint_view(request: Request) -> typing.NoReturn:
    raise WithHintError('Oops, something really went wrong...')


app = Starlette(
    debug=True,
    routes=[Route('/', index_view), Route('/hint', hint_view)],
    middleware=[Middleware(StarceptionMiddleware)],
)
