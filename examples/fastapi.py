import typing
from fastapi import FastAPI, Request, Response

from starception import exception_handler

app = FastAPI()


@app.exception_handler(Exception)
def custom_exception_handler(request: Request, exc: Exception) -> Response:
    return exception_handler(request, exc, debug=True)


@app.route('/')
def index_view(request: Request) -> typing.NoReturn:
    request.state.token = 'mytoken'
    request.app.state.app_token = 'app mytoken'
    raise TypeError('Oops, something really went wrong...')
