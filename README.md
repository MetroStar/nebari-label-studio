
# Nebari Plugin Label-Studio Chart

[![PyPI - Version](https://img.shields.io/pypi/v/nebari-plugin-label-studio-chart.svg)](https://pypi.org/project/nebari-plugin-label-studio-chart)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nebari-plugin-label-studio-chart.svg)](https://pypi.org/project/nebari-plugin-label-studio-chart)

-----

## Overview
This plugin integrates Label Studio into the Nebari platform, allowing seamless labeling functionality within Nebari. Utilizing Python, Terraform, Kubernetes, and Helm charts, the plugin provides a configurable deployment and authentication through Keycloak.

## Design and Architecture
The plugin follows a modular design, leveraging Terraform to define the deployment of Label Studio within a Kubernetes cluster. Key components include:
- **Terraform Configuration**: Defines variables, outputs, and resources for deployment, including Helm release, Keycloak authentication, and Kubernetes secrets.
- **Helm Chart Integration**: Deploys Label Studio as a Helm chart within the specified Kubernetes namespace.
- **Authentication**: Utilizes Keycloak for OpenID authentication, including user roles and group memberships.

## Installation Instructions


```console
pip install nebari-plugin-label-studio-chart
```


## Usage Instructions
- **Configurations**: Various configurations are available, including domain, realm ID, client ID, signing key, and namespace settings.
- **Authentication**: Enable or disable authentication and define specific OpenID parameters.

## Configuration Details

### Public
Configuration of the Label Studio plugin is controlled through the `label_studio` section of the `nebari-config.yaml` for the environment.

``` yaml
label_studio:
    # helm release name - default label-studio
    name: label-studio
    # target namespace - default (nebari global namespace)
    namespace: label-studio
    # enable or disable traefik auth proxy and keycloak integration
    auth:
        enabled: true
    # configure default affinity/selector for chart components
    affinity:
        enabled: true # default
        selector: general # default
        # -- or --
        selector:
            default: general
            worker: worker
            db: general
            auth: general
    # helm chart values overrides
    values: {}
```

### Internal
The following configuration values apply to the internally managed terraform module and are indirectly controlled through related values in `nebari-config.yaml`.

- `name`: Chart name for Helm release.
- `domain`: Domain for the plugin's deployment.
- `realm_id`, `client_id`: Keycloak authentication settings.
- `base_url`, `external_url`, `valid_redirect_uris`: OpenID URLs.
- `signing_key_ref`: Signing key reference information.
- `create_namespace`, `namespace`: Kubernetes namespace configuration.
- `overrides`: Map for overriding default configurations.
- `auth_enabled`: Flag to enable/disable authentication.

### Label Studio Version

Label Studio is deployed via its offical Helm chart and will default to using the `develop` image tag if not specified.

To set a Label Studio version, update your `nebari-config.yaml` to override the app image tag used in the helm chart.

``` yaml
label_studio:
  namespace: label-studio
  values:
    # Deploy Label Studio 1.8.1
    global:
      image:
        tag: "1.8.1"
```
See the [Label Studio helm chart documentation](https://labelstud.io/guide/helm_values) for all available configurations.

## Usage
Once the extension is installed, the Label Studio Community Edition will be available at `https://[your-project-domain]/label-studio`.

If authentication is enabled, any user attempting to access Label Studio will be required to login first with valid, active Nebari (Keycloak) credentials.  However, Label Studio accounts are separate from Nebari accounts.  Any user who has passed the authentication step above will then be able to create their own account.

> NOTE: The Community Edition of Label Studio does not include role-based access permissions.  All users have access to the same functionality and can see all projects.

Once a user has created their account, they can join the Label Studio 101 tutorial at the step [Label Studio 101 - Creating Your Project](https://labelstud.io/blog/zero-to-one-getting-started-with-label-studio/#creating-your-project).

For more information on using Label Studio, refer to the [Label Studio documentation](https://labelstud.io/guide/).

## Testing Overview

The plugin includes unit tests to validate its core functionalities:

- **Constructor Test**: Verifies the default name and priority.
- **Input Variables Test**: Validates domain, realm ID, client ID, and external URL settings.
- **Default Namespace Test**: Tests the default namespace configuration.

## License

`nebari-plugin-label-studio-chart` is distributed under the terms of the [Apache](./LICENSE.md) license.