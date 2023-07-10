from typing import List

from nebari.hookspecs import NebariStage, hookimpl

from nebari_helm_stage import InputSchema, NebariHelmStage, helm

label_studio = helm.Chart(
    name="label-studio",
    repo="heartex",
    url="https://charts.heartex.com/",
    version="1.1.4",
    overrides={},
)


class LabelStudioHelmStage(NebariHelmStage):
    name = "my-label-studio"

    input_schema = InputSchema
    output_schema = None

    base_dependency_charts = [label_studio]


@hookimpl
def nebari_stage() -> List[NebariStage]:
    return [LabelStudioHelmStage]
