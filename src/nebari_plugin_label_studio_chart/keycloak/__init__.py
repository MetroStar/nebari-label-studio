import inspect
import pathlib
import sys
import time

from typing import Any, Dict

from _nebari.stages.base import NebariTerraformStage

NUM_ATTEMPTS = 10
TIMEOUT = 10

CLIENT_NAME = "label-studio"

class LabelStudioKeycloakStage(NebariTerraformStage):
    name = "label-studio-keycloak"
    priority = 100

    @property
    def template_directory(self):
        return pathlib.Path(inspect.getfile(self.__class__)).parent / "terraform"

    def input_vars(self, stage_outputs: Dict[str, Dict[str, Any]]):
        keycloak_config = self.get_keycloak_config(stage_outputs)

        return {
            "realm_id": keycloak_config["realm_id"],
            "client_id": CLIENT_NAME,
            "base_url": f"https://{keycloak_config['domain']}/label-studio",
            "external_url": keycloak_config["keycloak_url"],
            "valid_redirect_uris": [f"https://{keycloak_config['domain']}/label-studio/_oauth"],
            "signing_key_ref": {
                "name": "forwardauth-deployment",
                "kind": "Deployment",
                "namespace": self.config.namespace,
            }
        }

    def check(self, stage_outputs: Dict[str, Dict[str, Any]]):
        keycloak_config = self.get_keycloak_config(stage_outputs)

        from keycloak import KeycloakAdmin
        from keycloak.exceptions import KeycloakError

        def _attempt_keycloak_connection(
            keycloak_url,
            username,
            password,
            master_realm_name,
            client_id,
            client_realm_name,
            verify=False,
            num_attempts=NUM_ATTEMPTS,
            timeout=TIMEOUT,
        ):
            for i in range(num_attempts):
                try:
                    realm_admin = KeycloakAdmin(
                        keycloak_url,
                        username=username,
                        password=password,
                        realm_name=master_realm_name,
                        client_id=client_id,
                        verify=verify,
                    )
                    realm_admin.realm_name = client_realm_name # switch to nebari realm
                    c = realm_admin.get_client_id(CLIENT_NAME) # lookup client guid
                    existing_client = realm_admin.get_client(c) # query client info
                    if existing_client != None and existing_client["name"] == CLIENT_NAME:
                        print(
                            f"Attempt {i+1} succeeded connecting to keycloak and nebari client={CLIENT_NAME} exists"
                        )
                        return True
                    else:
                        print(
                            f"Attempt {i+1} succeeded connecting to keycloak but nebari client={CLIENT_NAME} did not exist"
                        )
                except KeycloakError as e:
                    print(f"Attempt {i+1} failed connecting to keycloak {client_realm_name} realm -- {e}")
                time.sleep(timeout)
            return False

        if not _attempt_keycloak_connection(
            keycloak_config["keycloak_url"],
            keycloak_config["username"],
            keycloak_config["password"],
            keycloak_config["master_realm_id"],
            keycloak_config["master_client_id"],
            keycloak_config["realm_id"],
            verify=False,
        ):
            print(
                f"ERROR: unable to connect to keycloak master realm and ensure that nebari client={CLIENT_NAME} exists"
            )
            sys.exit(1)

        print(f"Keycloak successfully configured with {CLIENT_NAME} client")

    def get_keycloak_config(self, stage_outputs: Dict[str, Dict[str, Any]]):
        directory = "stages/05-kubernetes-keycloak"

        return {
            "domain": stage_outputs["stages/04-kubernetes-ingress"]["domain"],
            "keycloak_url": f"{stage_outputs[directory]['keycloak_credentials']['value']['url']}/auth/",
            "username": stage_outputs[directory]["keycloak_credentials"]["value"]["username"],
            "password": stage_outputs[directory]["keycloak_credentials"]["value"]["password"],
            "master_realm_id": stage_outputs[directory]["keycloak_credentials"]["value"]["realm"],
            "master_client_id": stage_outputs[directory]["keycloak_credentials"]["value"]["client_id"],
            "realm_id": stage_outputs["stages/06-kubernetes-keycloak-configuration"]["realm_id"]["value"],
        }
    