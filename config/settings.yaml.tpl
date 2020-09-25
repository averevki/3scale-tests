# vim: filetype=yaml

# default section/environment of globally applicable values
# all the values can be repeated/overwritten in other environments
default:
  skip_cleanup: false  # should we delete all the 3scale objects created during test?
  ssl_verify: true  # use secure connection checks, this requires all the stack (e.g. trusted CA)
  http2: false # enables http/2 requests to apicast
  threescale:  # now configure threescale details
    version: "{DEFAULT_THREESCALE_VERSION}"  # tested version used for example is some tests needs to be skipped
    superdomain: "{DEFAULT_THREESCALE_SUPERDOMAIN}"  # Threescale superdomain/wildcard_domain
    service:
      backends:  # list of backend services for testing
        httpbin: https://httpbin.org:443
        echo_api: https://echo-api.3scale.net:443
        httpbin_nossl: http://httpbin.org:80
    gateway:
      template: "{DEFAULT_APICAST_TEMPLATE}"
      image: "{DEFAULT_APICAST_IMAGE}"
      type: "apicast"
      configuration:
        staging_deployment: "apicast-staging"
        production_deployment: "apicast-production"
  openshift:
    servers:
      default:
        server_url: "{DEFAULT_OPENSHIFT_URL}"
    projects:
      threescale:
        name: "{DEFAULT_OPENSHIFT_THREESCALE_PROJECT}"
  rhsso:
    test_user:
      username: testUser
      password: testUser
  proxy:
    http: http://tinyproxy-service.tiny-proxy.svc:8888
    https: http://tinyproxy-service.tiny-proxy.svc:8888
  reporting:
    testsuite_properties:
      polarion_project_id: PROJECTID
      polarion_response_myteamsname: teamname


# dynaconf uses development environment by default
development:
  threescale:
    admin:
      url: https://3scale-admin.{DEVELOPMENT_THREESCALE_SUPERDOMAIN}
      token: "{DEVELOPMENT_ADMIN_ACCESS_TOKEN}"
      username: admin
      password: "{DEVELOPMENT_ADMIN_PASSWORD}"
    master:
      url: https://master.{DEVELOPMENT_THREESCALE_SUPERDOMAIN}
      token: "{DEVELOPMENT_MASTER_ACCESS_TOKEN}"
      username: master
      password: "{DEVELOPMENT_MASTER_PASSWORD}"
    service:
      backends:
        primary: https://httpbin.{DEVELOPMENT_TESTENV_DOMAIN}:443
        httpbin_go: https://httpbingo.{DEVELOPMENT_TESTENV_DOMAIN}:443
        httpbin_go_mtls: https://httpbingo-mtls.{DEVELOPMENT_TESTENV_DOMAIN}:443
      projects:
        # Project which the secrets containing the certificates for mtls resides in.
        # Usually the secrets are created in httpbin project because htttpbin go with mtls is deployed in there.
        mtls-certificates:
          name: httpbin

  rhsso:
    # admin credentials
    username: "{DEFAULT_RHSSO_ADMIN_USERNAME}"
    password: "{DEFAULT_RHSSO_ADMIN_PASSWORD}"
    url: http://sso-testing-sso.{DEVELOPMENT_TESTENV_DOMAIN}
  openshift:
    projects:
      threescale:
        name: "{DEVELOPMENT_OPENSHIFT_THREESCALE_PROJECT}"
    servers:
      default:
        server_url: "{DEVELOPMENT_OPENSHIFT_URL}"
  redis:
    url: redis://apicast-testing-redis:6379/1
  prometheus:
    url: "{PROMETHEUS_URL}"
  toolbox:
    # rpm/gem/podman; rpm = command from rpm package, gem = command from gem
    # 'ruby_version' should be defined for "gem" option
    # 'podman_image' should be defined for "podman" option
    # 'podman_cert_dir' should be defined for "podman" option
    # cmd: "rpm"
    # cmd: "gem"
    # ruby_version: "rh-ruby24"
    cmd: "podman"
    podman_cert_dir: "/var/data"
    podman_cert_name: "ca-bundle.crt"
