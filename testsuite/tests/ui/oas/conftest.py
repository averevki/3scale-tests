"""Conftest for active doc tests"""
import pytest

from testsuite.ui.views.admin.audience.developer_portal import ActiveDocsNewView
from testsuite.utils import blame


@pytest.fixture(scope="module")
def ui_active_doc(custom_admin_login, request, navigator, service, oas3_spec):
    """Active doc. bound to service created via UI"""
    custom_admin_login()
    name = blame(request, "active_doc_v3")
    system_name = blame(request, "system_name")
    new_view = navigator.navigate(ActiveDocsNewView)
    new_view.create_spec(
        name=name,
        sys_name=system_name,
        description="Active docs V3",
        service=service,
        oas_spec=oas3_spec,
        publish_option=True,
    )

    return service.active_docs.list()[0]


@pytest.fixture(scope="module")
def prod_client(prod_client):
    """
    Production client so tests can send request to service production endpoint
    """
    client = prod_client()
    response = client.get("/get")
    assert response.status_code == 200
    return client
