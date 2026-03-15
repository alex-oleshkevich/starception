# Starception

Beautiful exception page for Starlette and FastAPI apps.

![PyPI](https://img.shields.io/pypi/v/starception)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/alex-oleshkevich/starception/qa.yml?branch=master)
![GitHub](https://img.shields.io/github/license/alex-oleshkevich/starception)
![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/starception)
![PyPI - Downloads](https://img.shields.io/pypi/dm/starception)
![GitHub Release Date](https://img.shields.io/github/release-date/alex-oleshkevich/starception)

## Screenshot

![image](screenshot.png)

<details>
<summary>Dark theme</summary>
<div>
    <img src="./dark.png">
</div>
</details>

## Features

* secrets masking with reveal button
* solution hints
* exception notes (Python 3.11+)
* exception chains
* code snippets with syntax highlighting
* request info: query params, headers, cookies
* session contents
* request and app state
* platform information
* environment variables
* open paths in editor (VSCode; extensible via custom link templates)
* dark theme

## Installation

```bash
pip install starception
# or with uv
uv add starception
```

### With syntax highlighting

Install with the `highlight` extra for syntax-highlighted code snippets:

```bash
pip install starception[highlight]
# or with uv
uv add starception[highlight]
```

## Usage

Starception works only in debug mode — make sure `debug=True` is set on your app.

Call `install_error_handler` before creating your application instance:

**Starlette**

```python
from starception import install_error_handler
from starlette.applications import Starlette

install_error_handler()
app = Starlette(debug=True)
```

**FastAPI**

```python
from starception import install_error_handler
from fastapi import FastAPI

install_error_handler()
app = FastAPI(debug=True)
```

See the example application in the [examples/](examples/) directory for a full demo of all features.

### Integration with other frameworks

Starception exports `starception.exception_handler(request, exc)`, which you can use directly.
Keep in mind that Starlette will [not call](https://github.com/encode/starlette/issues/1802) custom exception
handlers in debug mode — it always uses its built-in one.

The snippet below will **not** work as expected:

```python
from starlette.applications import Starlette
from starception import exception_handler

app = Starlette(
    debug=True,
    exception_handlers={Exception: exception_handler}
)
```

Use `install_error_handler()` instead (shown above).

## Secrets masking

Starception automatically masks values whose key contains `key`, `secret`, `token`, or `password`,
and redacts passwords from URL-valued keys (e.g. `database_url`). Masked values are replaced with
`********` and can be revealed by clicking the **reveal** button next to them.

## Solution hints

If an exception class has a `solution` attribute, its content will be shown as a hint on the error page.

```python
class DatabaseError(Exception):
    solution = (
        'The connection to the database cannot be established. '
        'Either the database server is down or connection credentials are invalid.'
    )
```

![image](hints.png)

## Exception notes

Python 3.11+ supports attaching notes to exceptions via `add_note()`. Starception displays them on the error page.

```python
err = ValueError("something went wrong")
err.add_note("Check that the config file exists and is readable.")
raise err
```

## Exception chains

When exceptions are chained — either explicitly (`raise X from Y`) or implicitly (raising inside an `except` block) —
Starception renders each exception in the chain as a separate block, so you can trace the full error path.

## Opening files in editor

Pass your editor to `install_error_handler` to make file paths in stack frames clickable:

```python
from starception import install_error_handler

install_error_handler(editor='vscode')
```

Supported editors:

| Editor | Value |
|--------|-------|
| VSCode | `vscode` |

![image](link.png)

### Custom link templates

Register any editor with `add_link_template`:

```python
from starception import install_error_handler, add_link_template

add_link_template('zed', 'zed://file/{path}:{lineno}')
install_error_handler(editor='zed')
```

## Dark theme

The error page supports light, dark, and auto (follows system preference) themes. The toggle is in the top-right corner of the page and the chosen theme is persisted across page loads.

## Credits

* Look and feel inspired by [Phoenix Framework](https://www.phoenixframework.org/).
* Icons by [Tabler Icons](https://tabler-icons.io/).
