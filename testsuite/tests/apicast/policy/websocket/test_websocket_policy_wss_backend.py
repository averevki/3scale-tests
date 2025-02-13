"""
Basic test for websocket policy with wss backend_api

IMPORTANT: At this moment only used go-httbin supports websockets. At the same
moment go-httpbin support HTTP/2 (also only only) and ALPN negotiation. Due to
that this test doesn't work on openshift where
'ingress.operator.openshift.io/default-enable-http2=true' is enabled. In such
case tests ends with 502 error.
https://docs.openshift.com/container-platform/4.9/networking/ingress-operator.html#nw-http2-haproxy_configuring-ingress
"""
from packaging.version import Version  # noqa # pylint: disable=unused-import

import pytest

from testsuite import TESTED_VERSION, rawobj  # noqa # pylint: disable=unused-import
from testsuite.tests.apicast.policy.websocket.conftest import retry_sucessful, retry_failing

# websockets may fail for reason described above
pytestmark = [pytest.mark.sandbag, pytest.mark.skipif("TESTED_VERSION < Version('2.8')")]


@pytest.fixture(scope="module")
def service_proxy_settings(private_base_url):
    """Websocket are only available on httpbin go"""
    url = private_base_url("httpbin_go").replace("https://", "wss://", 1)
    return rawobj.Proxy(url)


@pytest.fixture
def user_key(application):
    """User key for application"""
    name = application.service.proxy.list()["auth_user_key"]
    key = application["user_key"]
    return f"?{name}={key}"


def test_basic_websocket_200(websocket_uri, user_key, websocket_options):
    """Basic test for websockets with valid user_key"""
    websocket_uri = websocket_uri + user_key
    message = "Websocket testing"

    assert message == retry_sucessful(websocket_uri, message, websocket_options)


def test_basic_websocket_403(websocket_uri, websocket_options):
    """Basic test for websocket with invalid user key"""
    websocket_uri = websocket_uri + "?user_key=123456"
    expected_message_error = "Handshake status 403 Forbidden"

    assert "403 Forbidden" in retry_failing(websocket_uri, expected_message_error, websocket_options)


def test_basic_request_200(api_client):
    """Basic test if HTTPS works on product with websocket policy"""
    response = api_client().get("/get")
    assert response.status_code == 200
