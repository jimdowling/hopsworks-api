#
#   Copyright 2024 Hopsworks AB
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

from hsml import model_serving


class TestModelServing:
    # get_deployment

    def test_get_deployment_not_found(self, mocker):
        # Arrange
        mocker.patch("hopsworks_common.client.get_instance")
        mocker.patch("hsml.core.serving_api.ServingApi.get", return_value=None)
        ms = model_serving.ModelServing(project_name="test", project_id=1)

        # Act
        result = ms.get_deployment("nonexistent")

        # Assert
        assert result is None

    def test_get_deployment_found(self, mocker, backend_fixtures):
        # Arrange
        mocker.patch("hopsworks_common.client.get_instance")
        mock_deployment = mocker.MagicMock()
        mock_deployment.name = "test_deployment"
        mocker.patch(
            "hsml.core.serving_api.ServingApi.get", return_value=mock_deployment
        )
        ms = model_serving.ModelServing(project_name="test", project_id=1)

        # Act
        result = ms.get_deployment("test_deployment")

        # Assert
        assert result is not None
        assert result.name == "test_deployment"

    # get_deployment_by_id

    def test_get_deployment_by_id_not_found(self, mocker):
        # Arrange
        mocker.patch("hopsworks_common.client.get_instance")
        mocker.patch("hsml.core.serving_api.ServingApi.get_by_id", return_value=None)
        ms = model_serving.ModelServing(project_name="test", project_id=1)

        # Act
        result = ms.get_deployment_by_id(999)

        # Assert
        assert result is None

    def test_get_deployment_by_id_found(self, mocker, backend_fixtures):
        # Arrange
        mocker.patch("hopsworks_common.client.get_instance")
        mock_deployment = mocker.MagicMock()
        mock_deployment.id = 1
        mock_deployment.name = "test_deployment"
        mocker.patch(
            "hsml.core.serving_api.ServingApi.get_by_id", return_value=mock_deployment
        )
        ms = model_serving.ModelServing(project_name="test", project_id=1)

        # Act
        result = ms.get_deployment_by_id(1)

        # Assert
        assert result is not None
        assert result.id == 1
        assert result.name == "test_deployment"
