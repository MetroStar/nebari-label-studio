import inspect

from pathlib import Path
from typing import Any, Dict

from nebari_helm_stage import NebariHelmStage, helm

from ..cfg import InputSchema

class LabelStudioHelmStage(NebariHelmStage):
    name = "label-studio-chart"
    priority = 101
    wait = True # wait for install to complete on nebari deploy

    input_schema = InputSchema

    base_dependency_charts = [
        helm.Chart(
            name="label-studio",
            repo="heartex",
            url="https://charts.heartex.com/",
            version="1.1.5",
        )
    ]

    @property
    def template_directory(self) -> Path:
        return Path(inspect.getfile(self.__class__)).parent / "chart"
    
    def check(self, stage_outputs: Dict[str, Dict[str, Any]]) -> bool:
        try:
            _ = stage_outputs["stages/04-kubernetes-ingress"]["domain"]
            _ = stage_outputs["stages/label-studio-keycloak"]["config"]["value"]
        except KeyError:
            print(
                "\nPrerequisite stage output(s) not found: 04-kubernetes-ingress, label-studio-keycloak"
            )
            return False

        return True

    def required_inputs(
        self, stage_outputs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, str]:
        try:
            domain = stage_outputs["stages/04-kubernetes-ingress"]["domain"]
            secret_data = stage_outputs["stages/label-studio-keycloak"]["config"]["value"]
        except KeyError:
            raise Exception("Prerequisite stage output(s) not found: 04-kubernetes-ingress, label-studio-keycloak")

        values = {
            "label-studio.global.extraEnvironmentVars.LABEL_STUDIO_HOST": f"https://{domain}/label-studio",
            "ingress.host": domain,
        }
        values.update({f"auth.secret.data.{k}": v for (k, v) in secret_data.items()})
        return values
