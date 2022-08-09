# Starception

Beautiful debugging page for Starlette apps implemented as ASGI middleware.

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

Add it as the first middleware in to your app:

```python
app = Starlette(
    middleware=[
        Middleware(StarceptionMiddleware, debug=True),
        # other middleware here
    ],
)
```

Note, the middleware won't handle anything if `debug=False`,
instead it will display plain string "Internal Server Error".
Also, I would recommend to add it only for local development, as such error page,
when enabled on prod by mistake, can expose sensitive data.

### Usage with FastAPI

As this is pure ASGI middleware, you can use it with FastAPI. However, you cannot use `app.middleware` decorator
and add it via `app.add_middleware` instead.

```python
app = FastAPI()

app.add_middleware(StarceptionMiddleware, debug=True)
```

See [FastAPI docs on middleware](https://fastapi.tiangolo.com/advanced/middleware/).

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

See example application in `examples/` directory of this repository.

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
