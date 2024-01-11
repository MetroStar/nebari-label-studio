locals {
  name                = var.name
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
  affinity = var.affinity != null && lookup(var.affinity, "enabled", false) ? {
    enabled = true
    selector = try(
      { for k in ["default", "worker", "db", "auth"] : k => length(var.affinity.selector[k]) > 0 ? var.affinity.selector[k] : var.affinity.selector.default },
      {
        default = var.affinity.selector
        worker  = var.affinity.selector
        db      = var.affinity.selector
        auth    = var.affinity.selector
      },
    )
    } : {
    enabled  = false
    selector = null
  }
  auth_enabled = var.auth_enabled

  chart_namespace = local.create_namespace ? kubernetes_namespace.this[0].metadata[0].name : local.namespace

  signing_key = local.auth_enabled ? (local.signing_key_ref == null
    ? random_password.signing_key[0].result
  : one([for e in data.kubernetes_resource.signing_key[0].object.spec.template.spec.containers[0].env : e.value if e.name == "SECRET"])) : ""
}

resource "kubernetes_namespace" "this" {
  count = local.create_namespace ? 1 : 0

  metadata {
    name = local.namespace
  }
}

resource "helm_release" "this" {
  name      = local.name
  chart     = "./chart"
  namespace = local.chart_namespace

  dependency_update = true

  values = [
    yamlencode({
      ingress = {
        host = local.domain
      }
      auth = {
        enabled        = local.auth_enabled
        existingSecret = local.auth_enabled ? kubernetes_secret.auth[0].metadata[0].name : ""
        affinity = local.affinity.enabled ? {
          nodeAffinity = {
            requiredDuringSchedulingIgnoredDuringExecution = {
              nodeSelectorTerms = [
                {
                  matchExpressions = [
                    {
                      key      = "eks.amazonaws.com/nodegroup"
                      operator = "In"
                      values   = [local.affinity.selector.auth]
                    }
                  ]
                }
              ]
            }
          }
        } : {}
      }
      label-studio = {
        global = {
          extraEnvironmentVars = {
            LABEL_STUDIO_HOST = local.base_url
          }
        }
        app = {
          affinity = local.affinity.enabled ? {
            nodeAffinity = {
              requiredDuringSchedulingIgnoredDuringExecution = {
                nodeSelectorTerms = [
                  {
                    matchExpressions = [
                      {
                        key      = "eks.amazonaws.com/nodegroup"
                        operator = "In"
                        values   = [local.affinity.selector.default]
                      }
                    ]
                  }
                ]
              }
            }
          } : {}
        }
        rqworker = {
          affinity = local.affinity.enabled ? {
            nodeAffinity = {
              requiredDuringSchedulingIgnoredDuringExecution = {
                nodeSelectorTerms = [
                  {
                    matchExpressions = [
                      {
                        key      = "eks.amazonaws.com/nodegroup"
                        operator = "In"
                        values   = [local.affinity.selector.worker]
                      }
                    ]
                  }
                ]
              }
            }
          } : {}
        }
        postgresql = {
          primary = {
            nodeSelector = local.affinity.enabled ? {
              "eks.amazonaws.com/nodegroup" = local.affinity.selector.db
            } : {}
          }
          readReplicas = {
            nodeSelector = local.affinity.enabled ? {
              "eks.amazonaws.com/nodegroup" = local.affinity.selector.db
            } : {}
          }
          backup = local.affinity.enabled ? {
            cronjob = {
              nodeSelector = {
                "eks.amazonaws.com/nodegroup" = local.affinity.selector.db
              }
            }
          } : {}
        }
      }
    }),
    yamlencode(local.overrides),
  ]
}

resource "keycloak_openid_client" "this" {
  count = local.auth_enabled ? 1 : 0

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
  count = local.auth_enabled ? 1 : 0

  realm_id   = local.realm_id
  client_id  = keycloak_openid_client.this[0].id
  name       = "user-client-role-mapper"
  claim_name = "roles"

  claim_value_type    = "String"
  multivalued         = true
  add_to_id_token     = true
  add_to_access_token = true
  add_to_userinfo     = true
}

resource "keycloak_openid_group_membership_protocol_mapper" "this" {
  count = local.auth_enabled ? 1 : 0

  realm_id   = local.realm_id
  client_id  = keycloak_openid_client.this[0].id
  name       = "group-membership-mapper"
  claim_name = "groups"

  full_path           = true
  add_to_id_token     = true
  add_to_access_token = true
  add_to_userinfo     = true
}

resource "kubernetes_secret" "auth" {
  count = local.auth_enabled ? 1 : 0

  metadata {
    name      = "${local.name}-auth"
    namespace = local.chart_namespace
  }

  data = {
    client_id     = keycloak_openid_client.this[0].client_id
    client_secret = keycloak_openid_client.this[0].client_secret
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

data "kubernetes_resource" "signing_key" {
  count = local.auth_enabled && local.signing_key_ref != null ? 1 : 0

  api_version = "apps/v1"
  kind        = local.signing_key_ref.kind == null ? "Deployment" : local.signing_key_ref.kind

  metadata {
    namespace = local.signing_key_ref.namespace
    name      = local.signing_key_ref.name
  }
}

resource "random_password" "signing_key" {
  count = local.auth_enabled && local.signing_key_ref == null ? 1 : 0

  length  = 32
  special = false
}
