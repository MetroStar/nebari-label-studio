import pytest

from kubernetes import client, config

from src.nebari_plugin_label_studio_chart.label_studio import LabelStudioHelmStage

POD_LABEL_SELECTOR = "app.kubernetes.io/name=ls-app"

def test_deploy(sut: LabelStudioHelmStage):
    sut.config.nebari_plugin_label_studio_chart.overrides = {
        "auth": {
            "enabled": False
        }
    }

    stage_outputs = {
        "04-kubernetes-ingress": {
            "domain": "my-test-domain.com"
        }
    }

    # make sure nothing is deployed already
    assert_clean(sut.config.namespace, POD_LABEL_SELECTOR)

    sut.render()

    print("\nDeploying helm chart, this may take a minute...")
    # execute helm install/upgrade
    with sut.deploy(stage_outputs) as _:
        pass

    # pod(s) should exist in the release namespace
    assert_pod_exists(sut.config.namespace, POD_LABEL_SELECTOR)

def assert_pod_exists(namespace: str, label_selector: str, expected_count: int = None):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace = namespace, label_selector = label_selector)

    if expected_count != None:
        assert expected_count == len(pods.items)
    else:
        assert len(pods.items) > 0

def assert_clean(namespace: str, label_selector: str):
    assert_pod_exists(namespace, label_selector, 0)

@pytest.fixture
def sut(sut: LabelStudioHelmStage):
    sut.debug = False
    sut.wait = True

    yield sut

    print("\nCleaning up...")
    try:
        # cleanup
        with sut.destroy(None, None) as _:
            pass

        # ensure everything is cleaned up
        assert_clean(sut.config.namespace, POD_LABEL_SELECTOR)
    except Exception as e:
        pytest.fail(f"Failed to cleanup helm release - {e}")
