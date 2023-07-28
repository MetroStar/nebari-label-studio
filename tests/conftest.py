import os
import pytest
import shutil

from nebari import schema
from nebari_helm_stage import InputSchema as HelmStageInputSchema
from nebari_helm_stage.helm import DEFAULT_HELM_VERSION
from src.nebari_plugin_label_studio_chart.label_studio import LabelStudioHelmStage

@pytest.fixture
def sut():
    output_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'out'))

    config = TestInputSchema(
        project_name = "test-project",
        namespace = "test-ns",
        nebari_plugin_label_studio_chart = HelmStageInputSchema()
    )
    sut = LabelStudioHelmStage(output_directory = output_directory, config = config)
    sut.debug = True

    # whatever copies the rendered files into the regular output_directory appears to be external
    # to the stage code itself. everything created by the render method gets left in the /tmp location otherwise
    sut.output_directory = f"/tmp/helm/{DEFAULT_HELM_VERSION}/{sut.config.project_name}-{sut.config.namespace}/{sut.name}"

    yield sut

    _teardown(sut)

def _teardown(sut: LabelStudioHelmStage):
    tmp_path = sut.output_directory
    if not os.path.exists(tmp_path):
        return

    print(f"\nDeleting {tmp_path}...")
    shutil.rmtree(tmp_path, ignore_errors=False, onerror=None)
    
    while True:
        tmp_path = os.path.abspath(os.path.join(tmp_path, os.pardir))
        if tmp_path.endswith('/tmp') or len(os.listdir(tmp_path)) > 0:
            return
        
        print(f"\nDeleting {tmp_path}...")
        shutil.rmtree(tmp_path, ignore_errors=False, onerror=None)

class TestInputSchema(schema.Main):
    nebari_plugin_label_studio_chart: HelmStageInputSchema
