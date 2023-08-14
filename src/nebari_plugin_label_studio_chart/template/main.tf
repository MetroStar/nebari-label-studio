locals {
  domain              = var.domain
  realm_id            = var.realm_id
  client_id           = var.client_id
  base_url            = var.base_url
  valid_redirect_uris = var.valid_redirect_uris
  external_url        = var.external_url
  signing_key_ref     = var.signing_key_ref

  create_namespace = var.create_namespace
  namespace        = var.namespace
  overrides        = var.overrides

  signing_key = (local.signing_key_ref == null
    ? random_password.signing_key[0].result
  : one([for e in data.kubernetes_resource.signing_key[0].object.spec.template.spec.containers[0].env : e.value if e.name == "SECRET"]))
}

resource "kubernetes_namespace" "this" {
  count = local.create_namespace ? 1 : 0

  metadata {
    name = local.namespace
  }
}

resource "helm_release" "this" {
  name      = "nebari-label-studio"
  chart     = "./chart"
  namespace = local.create_namespace ? kubernetes_namespace.this[0].metadata[0].name : local.namespace

  dependency_update = true

  values = [
    yamlencode({
      ingress = {
        host = local.domain
      }
      auth = {
        secret = {
          data = {
            client_id     = keycloak_openid_client.this.client_id
            client_secret = keycloak_openid_client.this.client_secret
            signing_key   = local.signing_key

            issuer_url    = "${local.external_url}realms/${local.realm_id}"
            discovery_url = "${local.external_url}realms/${local.realm_id}/.well-known/openid-configuration"
            auth_url      = "${local.external_url}realms/${local.realm_id}/protocol/openid-connect/auth"
            token_url     = "${local.external_url}realms/${local.realm_id}/protocol/openid-connect/token"
            jwks_url      = "${local.external_url}realms/${local.realm_id}/protocol/openid-connect/certs"
            logout_url    = "${local.external_url}realms/${local.realm_id}/protocol/openid-connect/logout"
            userinfo_url  = "${local.external_url}realms/${local.realm_id}/protocol/openid-connect/userinfo"
          }
        }
      }
      label-studio = {
        global = {
          extraEnvironmentVars = {
            LABEL_STUDIO_HOST = local.base_url
          }
        }
      }
    }),
    yamlencode(local.overrides),
  ]
}

resource "keycloak_openid_client" "this" {
  realm_id                     = local.realm_id
  name                         = local.client_id
  client_id                    = local.client_id
  access_type                  = "CONFIDENTIAL"
  base_url                     = local.base_url
  valid_redirect_uris          = local.valid_redirect_uris
  enabled                      = true
  standard_flow_enabled        = true
  direct_access_grants_enabled = false
  web_origins                  = ["+"]
}

resource "keycloak_openid_user_client_role_protocol_mapper" "this" {
  realm_id   = local.realm_id
  client_id  = keycloak_openid_client.this.id
  name       = "user-client-role-mapper"
  claim_name = "roles"

  claim_value_type    = "String"
  multivalued         = true
  add_to_id_token     = true
  add_to_access_token = true
  add_to_userinfo     = true
}

resource "keycloak_openid_group_membership_protocol_mapper" "this" {
  realm_id   = local.realm_id
  client_id  = keycloak_openid_client.this.id
  name       = "group-membership-mapper"
  claim_name = "groups"

  full_path           = true
  add_to_id_token     = true
  add_to_access_token = true
  add_to_userinfo     = true
}

data "kubernetes_resource" "signing_key" {
  count = local.signing_key_ref == null ? 0 : 1

  api_version = "apps/v1"
  kind        = local.signing_key_ref.kind == null ? "Deployment" : local.signing_key_ref.kind

  metadata {
    namespace = local.signing_key_ref.namespace
    name      = local.signing_key_ref.name
  }
}

resource "random_password" "signing_key" {
  count = local.signing_key_ref == null ? 1 : 0

  length  = 32
  special = false
}
