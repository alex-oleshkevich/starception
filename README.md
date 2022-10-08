# Starception

Beautiful exception page for Starlette and FastAPI apps.

![PyPI](https://img.shields.io/pypi/v/starception)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/alex-oleshkevich/starception/Lint%20and%20test)
![GitHub](https://img.shields.io/github/license/alex-oleshkevich/starception)
![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/starception)
![PyPI - Downloads](https://img.shields.io/pypi/dm/starception)
![GitHub Release Date](https://img.shields.io/github/release-date/alex-oleshkevich/starception)

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
* syntax highlighing
* open paths in editor (vscode only)
* exception chains

The middleware will automatically mask any value which key contains `key`, `secret`, `token`, `password`.

## Quick start

See example application in [examples/](examples/) directory of this repository.

## Usage

Starception will work only in debug mode so don't forget to set `debug=True` for local development.

### Monkey patching Starlette

To replace built-in debug exception handler call `install_error_handler` before you create Starlette instance.
> Currently, this is a recommended approach.

```python
from starception import install_error_handler
from starlette.applications import Starlette

install_error_handler()
app = Starlette()
```

### Using middleware

To render a beautiful exception page you need to install a `StarceptionMiddleware` middleware to your application.


> Note, to catch as many exceptions as possible the middleware has to be the first one in the stack.

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

Attach `StarceptionMiddleware` middleware to your FastAPI application:

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

### Integration with other frameworks

`starception` exports `starception.exception_handler(request, exc)` function, which you can use in your
framework.
But keep in mind, Starlette will [not call](https://github.com/encode/starlette/issues/1802) any custom exception
handler
in debug mode (it always uses built-in one).

The snipped below will not work as you expect (unfortunately).

```python
from starlette.applications import Starlette

from starception import exception_handler

app = Starlette(
    debug=True,
    exception_handlers={Exception: exception_handler}
)
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

## Opening files in editor

Set your current editor to open paths in your editor/IDE.

```python
from starception import set_editor

set_editor('vscode')
```

![image](link.png)


> Note, currently only VSCode supported. If you know how to integrate other editors - please PR

### Registering link templates

If your editor is not supported, you can add it by calling `add_link_template` and then selecting it with `set_editor`.

```python
from starception import set_editor, add_link_template

add_link_template('vscode', 'vscode://file/{path}:{lineno}')
set_editor('vscode')
```

## Credentials

* Look and feel inspired by [Phoenix Framework](https://www.phoenixframework.org/).
