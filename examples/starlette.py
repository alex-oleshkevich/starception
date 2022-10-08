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


app = Starlette(
    debug=True,
    routes=[
        Route('/', index_view),
        Route('/chain', chain_view),
        Route('/hint', hint_view),
    ],
    middleware=[Middleware(StarceptionMiddleware)],
)
