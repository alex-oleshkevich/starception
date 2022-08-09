import typing
from fastapi import FastAPI
from starlette.requests import Request

from starception.middleware import StarceptionMiddleware

app = FastAPI()

app.add_middleware(StarceptionMiddleware, debug=True)


@app.route('/')
def index_view(request: Request) -> typing.NoReturn:
    request.state.token = 'mytoken'
    request.app.state.app_token = 'app mytoken'
    raise TypeError('Oops, something really went wrong...')
