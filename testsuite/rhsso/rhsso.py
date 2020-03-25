"""
Utility resources for RHSSO manipulation
"""
from keycloak.admin.clients import Client
from keycloak.admin.realm import Realm
from keycloak.admin.users import User
from keycloak.openid_connect import KeycloakOpenidConnect
from keycloak.realm import KeycloakRealm


class RHSSO:
    """Helper class for RHSSO server"""

    def __init__(self, server_url, username, password) -> None:
        self.server_url = server_url
        self.realm = KeycloakRealm(server_url=server_url, realm_name='master')
        self.oidc = KeycloakOpenidConnect(realm=self.realm, client_id="admin-cli", client_secret=None)
        self.admin = self.realm.admin
        self.token = self.oidc.password_credentials(username=username, password=password)
        self.admin.set_token(self.token)

    def create_realm(self, name: str, **kwargs) -> Realm:
        """Creates new realm"""
        return self.admin.realms.create(name=name, enabled=True, sslRequired="None", **kwargs)

    def create_oidc_client(self, realm, client_id, secret):
        """Creates OIDC client"""
        keycloak_realm = KeycloakRealm(server_url=self.server_url, realm_name=realm.realm)
        return KeycloakOpenidConnect(realm=keycloak_realm, client_id=client_id, client_secret=secret)

    # pylint: disable=too-many-arguments
    def password_authorize(self, realm, client_id, secret, username, password):
        """Returns token retrived by password authentication"""
        oidc = self.create_oidc_client(realm, client_id, secret)
        return oidc.password_credentials(username=username, password=password)


# pylint: disable=too-few-public-methods
class RHSSOUser:
    """
    Wrapper for RHSSO user and its username and password combination
    """

    def __init__(self, user: User, username: str, password: str) -> None:
        self.user = user
        self.username = username
        self.password = password


class RHSSOServiceConfiguration:
    """
    Wrapper for all information that tests need to know about RHSSO
    """

    def __init__(self, rhsso: RHSSO, realm: Realm, client: Client, user: RHSSOUser) -> None:
        self.rhsso = rhsso
        self.realm = realm
        self.user = user.user
        self.client = client
        self.username = user.username
        self.password = user.password

    def issuer_url(self) -> str:
        """
        Returns issuer url for 3scale in format
        http(s)://<HOST>:<PORT>/auth/realms/<REALM_NAME>
        :return: url
        """
        secret = self.client.secret["value"]
        client_id = self.client.id
        url = self.rhsso.create_oidc_client(self.realm, client_id, secret).get_url("issuer")
        return url

    def authorization_url(self) -> str:
        """
        Returns authorization url for 3scale in format
        http(s)://<CLIENT_ID>:<CLIENT_SECRET>@<HOST>:<PORT>/auth/realms/<REALM_NAME>
        :return: url
        """
        secret = self.client.secret["value"]
        client_id = self.client.id
        url = self.issuer_url()
        return url.replace("://", "://%s:%s@" % (client_id, secret), 1)

    def password_authorize(self, client_id, secret):
        """Returns token retrived by password authentication"""
        return self.rhsso.password_authorize(self.realm, client_id, secret, self.username, self.password)


# pylint: disable=too-few-public-methods
class OIDCClientAuth:
    """Authentication class for  OIDC based authorization"""

    def __init__(self, service_rhsso_info, location=None) -> None:
        self.rhsso = service_rhsso_info
        self.location = location

    def __call__(self, application):
        location = self.location
        if location is None:
            location = application.service.proxy.list().entity["credentials_location"]
        app_key = application.keys.list()["keys"][0]["key"]["value"]
        token = self.rhsso.password_authorize(application["client_id"], app_key)
        credentials = {"access_token": token}

        def _process_request(request):
            access_token = token()
            credentials = {"access_token": access_token}

            if location == "authorization":
                request.headers.update({'Authorization': 'Bearer ' + access_token})
            elif location == "headers":
                request.prepare_headers(credentials)
            elif location == "query":
                request.prepare_url(request.url, credentials)
            else:
                raise ValueError("Unknown credentials location '%s'" % location)
            return request

        return _process_request


def add_realm_management_role(role_name, client, realm):
    """Add realm management role to the client"""
    user = client.service_account_user
    realm_management = realm.clients.by_client_id('realm-management')
    role = realm_management.roles.by_name(role_name)
    user.role_mappings.client(realm_management).add([role.entity])


def create_rhsso_user(realm, username, password):
    "Creates new user in RHSSO"
    user = realm.users.create(username, enabled=True)
    user.reset_password(password, temporary=False)
    return RHSSOUser(user, username, password)
