locals {
  realm_id            = var.realm_id
  client_id           = var.client_id
  base_url            = var.base_url
  valid_redirect_uris = var.valid_redirect_uris
  external_url        = var.external_url
  signing_key_ref     = var.signing_key_ref

  signing_key = (local.signing_key_ref == null
    ? random_password.signing_key[0].result
  : one([for e in data.kubernetes_resource.signing_key[0].object.spec.template.spec.containers[0].env : e.value if e.name == "SECRET"]))
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
