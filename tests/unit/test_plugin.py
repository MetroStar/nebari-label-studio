from src.nebari_plugin_label_studio_chart.plugin import LabelStudioStage, LabelStudioConfig, InputSchema

class TestConfig(InputSchema):
    namespace: str
    domain: str

def test_ctor():
    sut = LabelStudioStage(output_directory = None, config = None)
    assert sut.name == "label-studio"
    assert sut.priority == 100

def test_input_vars():
    config = TestConfig(namespace = "nebari-ns", domain = "my-test-domain.com")
    sut = LabelStudioStage(output_directory = None, config = config)

    stage_outputs = get_stage_outputs()
    result = sut.input_vars(stage_outputs)
    assert result["domain"] == "my-test-domain.com"
    assert result["realm_id"] == "test-realm"
    assert result["client_id"] == "label-studio"
    assert result["external_url"] == "https://my-test-domain.com/auth/"

def test_default_namespace():
    config = TestConfig(namespace = "nebari-ns", domain = "my-test-domain.com")
    sut = LabelStudioStage(output_directory = None, config = config)

    stage_outputs = get_stage_outputs()
    result = sut.input_vars(stage_outputs)
    assert result["create_namespace"] == False
    assert result["namespace"] == "nebari-ns"

def test_chart_namespace():
    config = TestConfig(namespace = "nebari-ns", domain = "my-test-domain.com", label_studio = LabelStudioConfig(namespace = "label-studio-ns"))
    sut = LabelStudioStage(output_directory = None, config = config)

    stage_outputs = get_stage_outputs()
    result = sut.input_vars(stage_outputs)
    assert result["create_namespace"] == True
    assert result["namespace"] == "label-studio-ns"

def test_chart_overrides():
    config = TestConfig(namespace = "nebari-ns", domain = "my-test-domain.com", label_studio = LabelStudioConfig(values = { "foo": "bar" }))
    sut = LabelStudioStage(output_directory = None, config = config)

    stage_outputs = get_stage_outputs()
    result = sut.input_vars(stage_outputs)
    assert result["overrides"] == { "foo": "bar" }

def get_stage_outputs():
    return {
        "stages/04-kubernetes-ingress": {
            "domain": "my-test-domain.com"
        },
        "stages/05-kubernetes-keycloak": {
            "keycloak_credentials": {
                "value": {
                    "url": "https://my-test-domain.com"
                }
            }
        },
        "stages/06-kubernetes-keycloak-configuration": {
            "realm_id": {
                "value": "test-realm"
            }
        }
    }