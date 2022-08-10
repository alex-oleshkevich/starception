import typing
from fastapi import FastAPI, Request

from starception import StarceptionMiddleware

app = FastAPI(debug=False)
app.add_middleware(StarceptionMiddleware)


@app.route('/')
def index_view(request: Request) -> typing.NoReturn:
    request.state.token = 'mytoken'
    request.app.state.app_token = 'app mytoken'
    raise TypeError('Oops, something really went wrong...')
