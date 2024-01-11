from typing import Any, Dict, Optional, Union


from nebari.schema import Base
from _nebari.stages.base import NebariTerraformStage


class LabelStudioAuthConfig(Base):
    enabled: Optional[bool] = True


class LabelStudioAffinitySelectorConfig(Base):
    default: str
    worker: Optional[str] = ""
    db: Optional[str] = ""
    auth: Optional[str] = ""


class LabelStudioAffinityConfig(Base):
    enabled: Optional[bool] = True
    selector: Union[LabelStudioAffinitySelectorConfig, str] = "general"


class LabelStudioConfig(Base):
    name: Optional[str] = "label-studio"
    namespace: Optional[str] = None
    auth: LabelStudioAuthConfig = LabelStudioAuthConfig()
    affinity: LabelStudioAffinityConfig = LabelStudioAffinityConfig()
    values: Optional[Dict[str, Any]] = {}


class InputSchema(Base):
    label_studio: LabelStudioConfig = LabelStudioConfig()


class LabelStudioStage(NebariTerraformStage):
    name = "label-studio"
    priority = 100

    input_schema = InputSchema

    def input_vars(self, stage_outputs: Dict[str, Dict[str, Any]]):
        domain = stage_outputs["stages/04-kubernetes-ingress"]["domain"]

        keycloak_url = ""
        realm_id = ""
        if self.config.label_studio.auth.enabled:
            keycloak_url = (
                f"{stage_outputs['stages/05-kubernetes-keycloak']['keycloak_credentials']['value']['url']}/auth/"
            )
            realm_id = stage_outputs["stages/06-kubernetes-keycloak-configuration"]["realm_id"]["value"]

        chart_ns = self.config.label_studio.namespace
        create_ns = True
        if chart_ns == None or chart_ns == "" or chart_ns == self.config.namespace:
            chart_ns = self.config.namespace
            create_ns = False

        return {
            "name": self.config.label_studio.name,
            "domain": domain,
            "realm_id": realm_id,
            "client_id": self.name,
            "base_url": f"https://{domain}/label-studio",
            "external_url": keycloak_url,
            "valid_redirect_uris": [f"https://{domain}/label-studio/_oauth"],
            "signing_key_ref": {
                "name": "forwardauth-deployment",
                "kind": "Deployment",
                "namespace": self.config.namespace,
            },
            "create_namespace": create_ns,
            "namespace": chart_ns,
            "overrides": self.config.label_studio.values,
            "affinity": {
                "enabled": self.config.label_studio.affinity.enabled,
                "selector": self.config.label_studio.affinity.selector.__dict__
                if isinstance(self.config.label_studio.affinity.selector, LabelStudioAffinitySelectorConfig)
                else self.config.label_studio.affinity.selector,
            },
            "auth_enabled": self.config.label_studio.auth.enabled,
        }
