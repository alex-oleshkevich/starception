import typing
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.routing import Route
from starlette.testclient import TestClient

from starception import StarceptionMiddleware
from starception.exception_handler import install_error_handler


def view(request: Request) -> typing.NoReturn:
    raise TypeError('Oops')


debug_app = Starlette(debug=True, routes=[Route('/', view)], middleware=[Middleware(StarceptionMiddleware)])
release_app = Starlette(debug=False, routes=[Route('/', view)], middleware=[Middleware(StarceptionMiddleware)])
no_middleware_debug_app = Starlette(debug=True, routes=[Route('/', view)])
no_middleware_release_app = Starlette(debug=False, routes=[Route('/', view)])


def test_middleware_renders_html_page_in_debug_mode() -> None:
    client = TestClient(debug_app, raise_server_exceptions=False)
    response = client.get('/', headers={'accept': 'text/html'})
    assert '<body>' in response.text
    assert 'Oops' in response.text


def test_middleware_renders_html_page_with_handler_installed_in_debug_mode() -> None:
    install_error_handler()
    client = TestClient(no_middleware_debug_app, raise_server_exceptions=False)
    response = client.get('/', headers={'accept': 'text/html'})
    assert '<body>' in response.text
    assert 'Oops' in response.text


def test_middleware_renders_plain_text_page_with_handler_installed_in_release_mode() -> None:
    install_error_handler()
    client = TestClient(no_middleware_release_app, raise_server_exceptions=False)
    response = client.get('/', headers={'accept': 'text/html'})
    assert 'Internal Server Error' in response.text


def test_middleware_renders_plain_text_page_in_debug_mode_for_non_html() -> None:
    client = TestClient(debug_app, raise_server_exceptions=False)
    response = client.get('/', headers={'accept': 'text/plain'})
    assert '<body>' not in response.text
    assert 'Oops' in response.text


def test_middleware_renders_plain_text_in_release_mode() -> None:
    client = TestClient(release_app, raise_server_exceptions=False)
    response = client.get('/', headers={'accept': 'text/html'})
    assert 'Internal Server Error' in response.text
