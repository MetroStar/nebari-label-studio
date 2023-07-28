import os

from src.nebari_plugin_label_studio_chart.label_studio import LabelStudioHelmStage

def test_ctor():
    sut = LabelStudioHelmStage(output_directory = None, config = None)
    assert sut.name == "nebari-plugin-label-studio-chart"
    assert sut.priority == 101

def test_required_inputs(sut: LabelStudioHelmStage):
    result = sut.required_inputs({
        "04-kubernetes-ingress": {
            "domain": "my-test-domain.com"
        }
    })
    assert result["ingress.host"] == "my-test-domain.com"
    assert result["label-studio.global.extraEnvironmentVars.LABEL_STUDIO_HOST"] == "https://my-test-domain.com/label-studio"

def test_check(sut: LabelStudioHelmStage):
    stage_outputs = {
        "04-kubernetes-ingress": {
            "domain": "my-test-domain.com"
        }
    }
    assert sut.check(stage_outputs) == True

def test_render(sut: LabelStudioHelmStage):
    tmp_path = sut.output_directory

    # nothing in the output_directory location to begin with
    assert os.path.exists(tmp_path) == False

    sut.render()

    assert os.path.exists(os.path.join(tmp_path, "values.yaml")) == True

def test_template(sut: LabelStudioHelmStage):
    stage_outputs = {
        "04-kubernetes-ingress": {
            "domain": "my-test-domain.com"
        }
    }

    sut.render()
    result = sut.template(stage_outputs)

    assert result != None
    assert "namespace: test-ns" in result[1]
    assert "Host(`my-test-domain.com`)" in result[1]
