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

import logging
from typing import Any

from hsfs.core import iceberg_catalog


_logger = logging.getLogger(__name__)


class IcebergEngine:
    """Spark read/write path for Iceberg time-travel feature groups.

    Iceberg feature groups are backed by the Hopsworks Iceberg REST catalog (state in RonDB).
    Reads and writes go through a Spark `SparkCatalog` of `type=rest` pointing at the Hopsworks
    catalog endpoint, so the catalog — not the Hive metastore — tracks the table's metadata pointer
    and snapshots. The table is addressed as `<catalog>.<namespace>.<table>`, where the namespace is
    the offline feature store database and the table is `<name>_<version>`.
    """

    ICEBERG_SPARK_FORMAT = "iceberg"
    APPEND = "append"

    def __init__(
        self,
        feature_store_id: int,
        feature_store_name: str,
        feature_group,
        spark_session,
        spark_context,
    ):
        _logger.debug(
            f"Initializing IcebergEngine {feature_group.name} v{feature_group.version}"
        )
        self._feature_group = feature_group
        self._feature_store_id = feature_store_id
        self._feature_store_name = feature_store_name
        self._spark_session = spark_session
        self._spark_context = spark_context
        self._catalog_name = iceberg_catalog.configure_spark_catalog(spark_session)

    def _table_identifier(self) -> str:
        # <catalog>.<namespace=feature_store_db>.<table=name_version>
        return (
            f"{self._catalog_name}.`{self._feature_store_name}`."
            f"`{self._feature_group.name}_{self._feature_group.version}`"
        )

    def save_iceberg_fg(
        self,
        dataframe,
        write_options: dict[str, Any] | None,
        validation_id: int | None = None,
        operation: str = "append",
    ):
        """Append a Spark dataframe to the Iceberg feature group through the REST catalog.

        The table already exists (Hopsworks creates it server-side at feature-group creation), so the
        first write is an append that adds the initial snapshot. The commit is applied by the catalog
        with optimistic concurrency; Hopsworks does not record a separate FeatureGroupCommit for
        Iceberg (snapshot history lives in the table metadata).
        """
        identifier = self._table_identifier()
        _logger.debug(
            f"Writing Iceberg dataset to {identifier} for feature group "
            f"{self._feature_group.name} v{self._feature_group.version}"
        )
        writer = dataframe.writeTo(identifier)
        if write_options:
            for key, value in write_options.items():
                writer = writer.option(key, value)
        writer.append()

    def register_temporary_table(
        self, alias: str, read_options: dict[str, Any] | None = None
    ):
        """Register the current snapshot of the Iceberg feature group as a temp view for reads."""
        reader = self._spark_session.read.format(self.ICEBERG_SPARK_FORMAT)
        if read_options:
            reader = reader.options(**read_options)
        reader.table(self._table_identifier()).createOrReplaceTempView(alias)
