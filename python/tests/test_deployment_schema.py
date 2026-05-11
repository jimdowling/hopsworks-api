#
#   Copyright 2026 Hopsworks AB
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
from __future__ import annotations

from types import SimpleNamespace

import pytest
from hsml.client.exceptions import ModelServingException
from hsml.deployment_schema import DeploymentSchema


SPEC_EXAMPLE_DICT = {
    "columnar_schema": [
        {
            "serving_keys": [
                {"name": "account_id", "type": "string"},
                {"name": "cc_num", "type": "bigint"},
            ]
        },
        {
            "passed_features": [
                {"name": "amount", "type": "double"},
            ]
        },
        {
            "request_parameters": [
                {"name": "dob", "type": "timestamp"},
                {"name": "transaction_time", "type": "timestamp"},
            ]
        },
    ]
}


class TestDeploymentSchema:
    def test_construct_and_sort(self):
        schema = DeploymentSchema(
            serving_keys=[
                {"name": "cc_num", "type": "bigint"},
                {"name": "account_id", "type": "string"},
            ],
            passed_features=[{"name": "amount", "type": "double"}],
            request_parameters=[
                {"name": "transaction_time", "type": "timestamp"},
                {"name": "dob", "type": "timestamp"},
            ],
        )
        assert [c.name for c in schema.serving_keys] == ["account_id", "cc_num"]
        assert [c.name for c in schema.passed_features] == ["amount"]
        assert [c.name for c in schema.request_parameters] == [
            "dob",
            "transaction_time",
        ]
        assert schema.to_dict() == SPEC_EXAMPLE_DICT

    def test_reject_non_ofs_type(self):
        with pytest.raises(ValueError, match="non-OFS type"):
            DeploymentSchema(serving_keys=[{"name": "cc_num", "type": "fancy_type"}])

    def test_reject_cross_category_duplicate(self):
        with pytest.raises(ValueError, match="multiple input categories"):
            DeploymentSchema(
                serving_keys=[{"name": "amount", "type": "double"}],
                passed_features=[{"name": "amount", "type": "double"}],
            )

    def test_reject_within_category_duplicate(self):
        with pytest.raises(ValueError, match="Duplicate name"):
            DeploymentSchema(
                serving_keys=[
                    {"name": "cc_num", "type": "bigint"},
                    {"name": "cc_num", "type": "bigint"},
                ]
            )

    def test_reject_missing_type(self):
        with pytest.raises(ValueError, match="Missing 'type'"):
            DeploymentSchema(request_parameters=[{"name": "dob"}])

    def test_roundtrip_via_dict(self):
        rebuilt = DeploymentSchema.from_dict(SPEC_EXAMPLE_DICT)
        assert rebuilt.to_dict() == SPEC_EXAMPLE_DICT

    def test_input_schema_omits_empty_categories(self):
        schema = DeploymentSchema(serving_keys=[{"name": "cc_num", "type": "bigint"}])
        assert schema.input_schema == {
            "columnar_schema": [
                {"serving_keys": [{"name": "cc_num", "type": "bigint"}]}
            ]
        }


def _fv(
    *,
    features,
    serving_keys,
    inference_helpers=None,
    labels=None,
    request_parameters=None,
):
    return SimpleNamespace(
        features=features,
        serving_keys=serving_keys,
        inference_helper_columns=list(inference_helpers or []),
        labels=list(labels or []),
        request_parameters=list(request_parameters or []),
    )


def _feature(name, type_, online_type=None, fg=None):
    return SimpleNamespace(
        name=name, type=type_, online_type=online_type, feature_group=fg
    )


def _serving_key(feature_name, prefix="", ignore_prefix=False):
    return SimpleNamespace(
        feature_name=feature_name,
        prefix=prefix,
        ignore_prefix=ignore_prefix,
        required_serving_key=(
            feature_name if ignore_prefix else (prefix + feature_name)
        ),
        feature_group=None,
    )


class TestFromFeatureView:
    def test_infers_full_spec_example(self):
        fv = _fv(
            features=[
                _feature("cc_num", "bigint"),
                _feature("account_id", "string"),
                _feature("amount", "double"),
                _feature("fraud_label", "int"),
            ],
            serving_keys=[
                _serving_key("cc_num"),
                _serving_key("account_id"),
            ],
            labels=["fraud_label"],
            request_parameters=[],
        )
        schema = DeploymentSchema.from_feature_view(
            fv,
            passed_features=["amount"],
            request_parameters={"dob": "timestamp", "transaction_time": "timestamp"},
        )
        assert (
            schema.to_dict()["columnar_schema"] == SPEC_EXAMPLE_DICT["columnar_schema"]
        )
        assert schema.output_schema.to_dict() == {
            "columnar_schema": [{"name": "fraud_label", "type": "int"}]
        }

    def test_uses_online_type_when_set(self):
        fv = _fv(
            features=[
                _feature("name", "string", online_type="varchar(64)"),
            ],
            serving_keys=[_serving_key("name")],
        )
        schema = DeploymentSchema.from_feature_view(fv)
        assert schema.serving_keys[0].type == "varchar(64)"

    def test_raises_when_feature_view_missing(self):
        with pytest.raises(ModelServingException, match="feature view"):
            DeploymentSchema.from_feature_view(None)

    def test_passed_features_dict_form(self):
        fv = _fv(
            features=[_feature("cc_num", "bigint")],
            serving_keys=[_serving_key("cc_num")],
        )
        schema = DeploymentSchema.from_feature_view(
            fv, passed_features={"app_signal": "double"}
        )
        assert [c.name for c in schema.passed_features] == ["app_signal"]
        assert schema.passed_features[0].type == "double"


class TestRoundTripIntoPredictor:
    def test_predictor_to_dict_and_back(self, mocker):
        from hsml import predictor

        mocker.patch("hopsworks_common.client.is_kserve_installed", return_value=False)
        mocker.patch(
            "hopsworks_common.client.is_scale_to_zero_required", return_value=False
        )
        mocker.patch("hopsworks_common.client.is_saas_connection", return_value=False)

        schema = DeploymentSchema(
            serving_keys=[{"name": "cc_num", "type": "bigint"}],
            passed_features=[{"name": "amount", "type": "double"}],
        )
        p = predictor.Predictor(
            name="m",
            model_server="PYTHON",
            model_name="m",
            model_version=1,
            deployment_schema=schema,
            passed_features=["amount"],
        )
        out = p.to_dict()
        assert "deploymentSchema" in out
        assert out["passedFeatures"] == ["amount"]
        assert out["deploymentSchema"] == schema.to_dict()
