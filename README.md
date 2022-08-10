# Starception

Beautiful exception page for Starlette and FastAPI apps.

![PyPI](https://img.shields.io/pypi/v/starception)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/alex-oleshkevich/starception/Lint)
![GitHub](https://img.shields.io/github/license/alex-oleshkevich/starception)
![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/starception)
![PyPI - Downloads](https://img.shields.io/pypi/dm/starception)
![GitHub Release Date](https://img.shields.io/github/release-date/alex-oleshkevich/starception)
![Lines of code](https://img.shields.io/tokei/lines/github/alex-oleshkevich/starception)

## Installation

Install `starception` using PIP or poetry:

```bash
pip install starception
# or
poetry add starception
```

## Screenshot

![image](screenshot.png)

## Features

* secrets masking
* solution hints
* code snippets
* display request info: query, body, headers, cookies
* session contents
* request and app state
* platform information
* environment variables

The middleware will automatically mask any value which key contains `key`, `secret`, `token`, `password`.

## Quick start

See example application in [examples/](examples/) directory of this repository.

## Usage

To render a beautiful exception page you need to install a `StarceptionMiddleware` middleware to your application.

> The middleware will work only in debug mode so don't forget to set `debug=True` for local development.

> Note, to catch at many exceptions as possible the middleware has to be the first one in the stack.

```python
import typing

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.routing import Route

from starception import StarceptionMiddleware


async def index_view(request: Request) -> typing.NoReturn:
    raise TypeError('Oops, something really went wrong...')


app = Starlette(
    debug=True,
    routes=[Route('/', index_view)],
    middleware=[
        Middleware(StarceptionMiddleware),
        # other middleware go here
    ],
)
```

### Integration with FastAPI

Create a FastAPI exception handler and register it with your app:

```python
import typing

from fastapi import FastAPI, Request

from starception import StarceptionMiddleware

app = FastAPI(debug=True)
app.add_middleware(StarceptionMiddleware)  # must be the first one!


@app.route('/')
async def index_view(request: Request) -> typing.NoReturn:
    raise TypeError('Oops, something really went wrong...')
```

## Solution hints

If exception class has `solution` attribute then its content will be used as a solution hint.

```python
class WithHintError(Exception):
    solution = (
        'The connection to the database cannot be established. '
        'Either the database server is down or connection credentials are invalid.'
    )
```

![image](hints.png)

## Credentials

* Look and feel inspired by [Phoenix Framework](https://www.phoenixframework.org/).
