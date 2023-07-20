from typing import Any, Dict, List

from nebari.hookspecs import NebariStage, hookimpl
from nebari_helm_stage import NebariHelmStage, helm

label_studio = helm.Chart(
    name="label-studio",
    repo="heartex",
    url="https://charts.heartex.com/",
    version="1.1.4",
)


class LabelStudioHelmStage(NebariHelmStage):
    name = "my-label-studio"
    base_dependency_charts = [label_studio]

    def required_inputs(self, stage_outputs: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        try:
            domain = stage_outputs["04-kubernetes-ingress"]["domain"]
        except KeyError:
            raise Exception("04-kubernetes-ingress stage must be run before this stage")

        return {
            "label-studio.global.extraEnvironmentVars.LABEL_STUDIO_HOST": f"https://{domain}/label-studio",
            "ingress.host": f"{domain}",
            "startup_greeting": f"Hello from {self.name}!",
        }


@hookimpl
def nebari_stage() -> List[NebariStage]:
    return [LabelStudioHelmStage]
