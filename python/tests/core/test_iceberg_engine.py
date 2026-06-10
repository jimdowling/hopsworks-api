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

import pytest
from hopsworks_common.client import exceptions
from hsfs import feature_group
from hsfs.core import feature_group_engine, iceberg_catalog, iceberg_engine


class TestIcebergCatalog:
    def test_spark_catalog_options_explicit(self):
        # Fully explicit arguments must not require an active Hopsworks client.
        options = iceberg_catalog.spark_catalog_options(
            project="proj",
            api_key="secret",
            rest_uri="https://host/hopsworks-api/api/iceberg",
        )

        prefix = f"spark.sql.catalog.{iceberg_catalog.SPARK_CATALOG_NAME}"
        assert options[prefix] == "org.apache.iceberg.spark.SparkCatalog"
        assert options[f"{prefix}.type"] == "rest"
        assert options[f"{prefix}.uri"] == "https://host/hopsworks-api/api/iceberg"
        assert options[f"{prefix}.warehouse"] == "proj"
        assert options[f"{prefix}.header.Authorization"] == "ApiKey secret"

    def test_spark_catalog_options_resolves_from_client(self, mocker):
        client = mocker.MagicMock()
        client._get_host_port_pair.return_value = ("hopsworks.cluster", 443)
        client._auth._token = "key123"
        client._project_name = "MyProj"
        mocker.patch(
            "hsfs.core.iceberg_catalog.client._get_instance", return_value=client
        )

        options = iceberg_catalog.spark_catalog_options()

        prefix = f"spark.sql.catalog.{iceberg_catalog.SPARK_CATALOG_NAME}"
        assert (
            options[f"{prefix}.uri"]
            == "https://hopsworks.cluster/hopsworks-api/api/iceberg"
        )
        assert options[f"{prefix}.warehouse"] == "myproj"
        assert options[f"{prefix}.header.Authorization"] == "ApiKey key123"


class TestIcebergEngine:
    def _feature_group(self, mocker):
        fg = mocker.MagicMock(spec=feature_group.FeatureGroup)
        fg.name = "fg_test"
        fg.version = 2
        return fg

    def test_table_identifier(self, mocker):
        engine = iceberg_engine.IcebergEngine(
            feature_store_id=99,
            feature_store_name="test_featurestore",
            feature_group=self._feature_group(mocker),
            spark_session=None,
            spark_context=None,
        )

        assert engine._table_identifier() == (
            f"{iceberg_catalog.SPARK_CATALOG_NAME}.`test_featurestore`.`fg_test_2`"
        )

    def test_save_iceberg_fg_appends(self, mocker):
        engine = iceberg_engine.IcebergEngine(
            feature_store_id=99,
            feature_store_name="test_featurestore",
            feature_group=self._feature_group(mocker),
            spark_session=None,
            spark_context=None,
        )
        dataframe = mocker.MagicMock()
        writer = dataframe.writeTo.return_value
        writer.option.return_value = writer

        engine.save_iceberg_fg(dataframe, write_options={"opt": "val"})

        dataframe.writeTo.assert_called_once_with(engine._table_identifier())
        writer.option.assert_called_once_with("opt", "val")
        writer.append.assert_called_once()


class TestIcebergCommitDelete:
    def test_commit_delete_rejected(self, mocker):
        fg = mocker.MagicMock(spec=feature_group.FeatureGroup)
        fg.time_travel_format = "ICEBERG"
        mocker.patch(
            "hsfs.core.feature_group_engine.FeatureGroupEngine."
            "_get_spark_session_and_context",
            return_value=(None, None),
        )

        with pytest.raises(exceptions.FeatureStoreException, match="Iceberg"):
            feature_group_engine.FeatureGroupEngine._commit_delete(
                fg, delete_df=None, write_options={}
            )
