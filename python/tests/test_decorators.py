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

import pytest
from hopsworks.client.exceptions import RestAPIError
from hsml.decorators import (
    HopsworksConnectionError,
    NoHopsworksConnectionError,
    catch_not_found,
    connected,
    not_connected,
)


class TestDecorators:
    # test not connected

    def test_not_connected_valid(self, mocker):
        # Arrange
        mock_instance = mocker.MagicMock()
        mock_instance._connected = False

        @not_connected
        def assert_not_connected(inst, arg, key_arg):
            assert not inst._connected
            assert arg == "arg"
            assert key_arg == "key_arg"

        # Act
        assert_not_connected(mock_instance, "arg", key_arg="key_arg")

    def test_not_connected_invalid(self, mocker):
        # Arrange
        mock_instance = mocker.MagicMock()
        mock_instance._connected = True

        @not_connected
        def assert_not_connected(inst, arg, key_arg):
            pass

        # Act
        with pytest.raises(HopsworksConnectionError):
            assert_not_connected(mock_instance, "arg", key_arg="key_arg")

    # test connected

    def test_connected_valid(self, mocker):
        # Arrange
        mock_instance = mocker.MagicMock()
        mock_instance._connected = True

        @connected
        def assert_connected(inst, arg, key_arg):
            assert inst._connected
            assert arg == "arg"
            assert key_arg == "key_arg"

        # Act
        assert_connected(mock_instance, "arg", key_arg="key_arg")

    def test_connected_invalid(self, mocker):
        # Arrange
        mock_instance = mocker.MagicMock()
        mock_instance._connected = False

        @connected
        def assert_connected(inst, arg, key_arg):
            pass

        # Act
        with pytest.raises(NoHopsworksConnectionError):
            assert_connected(mock_instance, "arg", key_arg="key_arg")

    # test catch_not_found

    def test_catch_not_found_returns_none_on_404_with_matching_error_code(self, mocker):
        # Arrange
        mock_response = mocker.MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"errorCode": 240000}  # Deployment NOT_FOUND_ERROR_CODE

        @catch_not_found("hsml.deployment.Deployment", fallback_return=None)
        def func_that_raises():
            raise RestAPIError("url", mock_response)

        # Act
        result = func_that_raises()

        # Assert
        assert result is None

    def test_catch_not_found_returns_none_on_400_with_matching_error_code(self, mocker):
        # Arrange
        mock_response = mocker.MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"errorCode": 240000}  # Deployment NOT_FOUND_ERROR_CODE

        @catch_not_found("hsml.deployment.Deployment", fallback_return=None)
        def func_that_raises():
            raise RestAPIError("url", mock_response)

        # Act
        result = func_that_raises()

        # Assert
        assert result is None

    def test_catch_not_found_reraises_on_non_matching_error_code(self, mocker):
        # Arrange
        mock_response = mocker.MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"errorCode": 999999}  # Different error code

        @catch_not_found("hsml.deployment.Deployment", fallback_return=None)
        def func_that_raises():
            raise RestAPIError("url", mock_response)

        # Act & Assert
        with pytest.raises(RestAPIError):
            func_that_raises()

    def test_catch_not_found_reraises_on_non_404_status(self, mocker):
        # Arrange
        mock_response = mocker.MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"errorCode": 240000}

        @catch_not_found("hsml.deployment.Deployment", fallback_return=None)
        def func_that_raises():
            raise RestAPIError("url", mock_response)

        # Act & Assert
        with pytest.raises(RestAPIError):
            func_that_raises()

    def test_catch_not_found_passes_through_successful_call(self, mocker):
        # Arrange
        expected_result = {"id": 1, "name": "test_deployment"}

        @catch_not_found("hsml.deployment.Deployment", fallback_return=None)
        def func_that_succeeds():
            return expected_result

        # Act
        result = func_that_succeeds()

        # Assert
        assert result == expected_result

    def test_catch_not_found_reraises_non_rest_api_error(self, mocker):
        # Arrange
        @catch_not_found("hsml.deployment.Deployment", fallback_return=None)
        def func_that_raises_value_error():
            raise ValueError("Some other error")

        # Act & Assert
        with pytest.raises(ValueError):
            func_that_raises_value_error()

    def test_catch_not_found_with_custom_fallback_return(self, mocker):
        # Arrange
        mock_response = mocker.MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"errorCode": 240000}
        custom_fallback = {"default": "value"}

        @catch_not_found("hsml.deployment.Deployment", fallback_return=custom_fallback)
        def func_that_raises():
            raise RestAPIError("url", mock_response)

        # Act
        result = func_that_raises()

        # Assert
        assert result == custom_fallback
