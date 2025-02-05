"""
Mocks for the gRPC servers.

@sa @ref scripts/docs/en/userver/tutorial/grpc_service.md
"""

# pylint: disable=no-member
import asyncio
import contextlib
import functools
import socket

import grpc
import pytest

from testsuite.utils import callinfo

DEFAULT_PORT = 8091


class GrpcServiceMock:
    def __init__(self, servicer, methods):
        self.servicer = servicer
        self._known_methods = methods
        self._methods = {}

    def get(self, method, default):
        return self._methods.get(method, default)

    def reset_handlers(self):
        self._methods = {}

    @contextlib.contextmanager
    def mock(self):
        try:
            yield self.install_handler
        finally:
            self._methods = {}

    def install_handler(self, method: str):
        def decorator(func):
            if method not in self._known_methods:
                raise RuntimeError(
                    f'Trying to mock unknown grpc method {method}',
                )

            wrapped = callinfo.acallqueue(func)
            self._methods[method] = wrapped
            return wrapped

        return decorator


@pytest.fixture(scope='session')
def _grpc_mockserver_endpoint(pytestconfig):
    port = pytestconfig.option.grpc_mockserver_port
    if pytestconfig.option.service_wait or pytestconfig.option.service_disable:
        port = port or DEFAULT_PORT
    if port == 0:
        port = _find_free_port()
    return f'{pytestconfig.option.grpc_mockserver_host}:{port}'


@pytest.fixture(scope='session')
def grpc_mockserver_endpoint(pytestconfig, _grpc_port) -> str:
    """
    Returns the gRPC endpoint to start the mocking server that is set by
    command line `--grpc-mockserver-host` and `--grpc-mockserver-port` options.

    Override this fixture to change the way the gRPC endpoint
    is detected by the testsuite.

    @snippet samples/grpc_service/tests/conftest.py  Prepare configs
    @ingroup userver_testsuite_fixtures
    """
    return f'{pytestconfig.option.grpc_mockserver_host}:{_grpc_port}'


def _find_free_port() -> int:
    with contextlib.closing(
            socket.socket(socket.AF_INET6, socket.SOCK_STREAM),
    ) as sock:
        sock.bind(('', 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.getsockname()[1]


@pytest.fixture(scope='session')
def _grpc_port(_grpc_mockserver_endpoint):
    _, port = _grpc_mockserver_endpoint.rsplit(':', 1)
    return int(port)


@pytest.fixture(scope='session')
async def grpc_mockserver(_grpc_mockserver_endpoint):
    """
    Returns the gRPC mocking server.

    Override this fixture to change the way the gRPC
    mocking server is started by the testsuite.

    @snippet samples/grpc_service/tests/conftest.py  Prepare server mock
    @ingroup userver_testsuite_fixtures
    """
    server = grpc.aio.server()
    server.add_insecure_port(_grpc_mockserver_endpoint)
    server_task = asyncio.create_task(server.start())

    try:
        yield server
    finally:
        await server.stop(grace=None)
        await server.wait_for_termination()
        await server_task


@pytest.fixture(scope='session')
def create_grpc_mock():
    """
    Creates the gRPC mock server for the provided type.

    @snippet samples/grpc_service/tests/conftest.py  Prepare server mock
    @ingroup userver_testsuite_fixtures
    """
    return _create_servicer_mock


def pytest_addoption(parser):
    group = parser.getgroup('grpc-mockserver')
    group.addoption(
        '--grpc-mockserver-host',
        default='[::]',
        help='gRPC mockserver hostname, default is [::]',
    )
    group.addoption(
        '--grpc-mockserver-port',
        type=int,
        default=0,
        help='gRPC mockserver port, by default random port is used',
    )


def _create_servicer_mock(servicer_class, stream_method_names=None):
    def wrap_grpc_method(name, default_method):
        @functools.wraps(default_method)
        async def run_method(self, *args, **kwargs):
            method = mock.get(name, None)
            if method is not None:
                call = method(*args, **kwargs)
            else:
                call = default_method(self, *args, **kwargs)

            return await call

        @functools.wraps(default_method)
        async def run_stream_method(self, *args, **kwargs):
            method = mock.get(name, None)
            async for response in await method(*args, **kwargs):
                yield response

        if name in (stream_method_names or []):
            return run_stream_method
        else:
            return run_method

    methods = {}
    for attname, value in servicer_class.__dict__.items():
        if callable(value):
            methods[attname] = wrap_grpc_method(attname, value)

    mocked_servicer_class = type(
        f'Mock{servicer_class.__name__}', (servicer_class,), methods,
    )
    servicer = mocked_servicer_class()
    mock = GrpcServiceMock(servicer, frozenset(methods))
    return mock
