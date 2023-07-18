from typing import List

from nebari.hookspecs import NebariStage, hookimpl
from nebari_helm_stage import NebariHelmStage, helm

label_studio = helm.Chart(
    name="label-studio",
    repo="heartex",
    url="https://charts.heartex.com/",
    version="1.1.4",
)

set_json_template = {
    "label-studio.global.extraEnvironmentVars.LABEL_STUDIO_HOST": "{domain}/label-studio",
    "ingress.host": "{domain}",
}


class LabelStudioHelmStage(NebariHelmStage):
    name = "my-label-studio"
    base_dependency_charts = [label_studio]
    set_json_template = set_json_template


@hookimpl
def nebari_stage() -> List[NebariStage]:
    return [LabelStudioHelmStage]
