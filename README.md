
# Nebari Plugin Label-Studio Chart

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

The Nebari Label Studio plugin offers various configuration options for customization:

- `name`: Chart name for Helm release.
- `domain`: Domain for the plugin's deployment.
- `realm_id`, `client_id`: Keycloak authentication settings.
- `base_url`, `external_url`, `valid_redirect_uris`: OpenID URLs.
- `signing_key_ref`: Signing key reference information.
- `create_namespace`, `namespace`: Kubernetes namespace configuration.
- `overrides`: Map for overriding default configurations.
- `auth_enabled`: Flag to enable/disable authentication.

## Testing Overview

The plugin includes unit tests to validate its core functionalities:

- **Constructor Test**: Verifies the default name and priority.
- **Input Variables Test**: Validates domain, realm ID, client ID, and external URL settings.
- **Default Namespace Test**: Tests the default namespace configuration.

## Version Information
- **Plugin Version**: 0.0.5

## License

`nebari-plugin-label-studio-chart` is distributed under the terms of the [Apache](./LICENSE.md) license.