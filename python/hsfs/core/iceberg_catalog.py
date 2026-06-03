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

from hopsworks_common import client


_logger = logging.getLogger(__name__)

# Local Spark catalog name for the Hopsworks Iceberg REST catalog.
SPARK_CATALOG_NAME = "hopsworks"
# REST catalog path under the Hopsworks API base.
REST_PATH = "/hopsworks-api/api/iceberg"


def _endpoint_and_credentials() -> tuple[str, str, str]:
    """Resolve (rest_uri, api_key, project) from the active Hopsworks client."""
    instance = client.get_instance()
    host, _port = instance._get_host_port_pair()
    rest_uri = f"https://{host}{REST_PATH}"
    api_key = getattr(getattr(instance, "_auth", None), "_token", None)
    project = getattr(instance, "_project_name", None) or getattr(
        instance, "_project_id", None
    )
    return rest_uri, api_key, str(project).lower() if project else None


def spark_catalog_options(
    project: str | None = None,
    api_key: str | None = None,
    rest_uri: str | None = None,
) -> dict[str, str]:
    """Spark configuration to register the Hopsworks Iceberg REST catalog.

    The warehouse is the project name (the REST `/config` endpoint resolves the catalog prefix from
    it); authentication reuses the Hopsworks API key via the `ApiKey` Authorization header.
    """
    resolved_uri, resolved_key, resolved_project = _endpoint_and_credentials()
    rest_uri = rest_uri or resolved_uri
    api_key = api_key or resolved_key
    project = project or resolved_project
    prefix = f"spark.sql.catalog.{SPARK_CATALOG_NAME}"
    options = {
        prefix: "org.apache.iceberg.spark.SparkCatalog",
        f"{prefix}.type": "rest",
        f"{prefix}.uri": rest_uri,
    }
    if project:
        options[f"{prefix}.warehouse"] = project
    if api_key:
        options[f"{prefix}.header.Authorization"] = f"ApiKey {api_key}"
    return options


def configure_spark_catalog(spark_session) -> str:
    """Register the Hopsworks Iceberg REST catalog on a live Spark session; return the catalog name.

    No-op-safe if the session already has it configured (classic Spark only — Spark Connect needs the
    catalog set at builder time).
    """
    if spark_session is not None:
        try:
            for key, value in spark_catalog_options().items():
                spark_session.conf.set(key, value)
        except Exception as e:  # noqa: BLE001
            _logger.warning(
                "Could not set Iceberg REST catalog config at runtime (Spark Connect requires it at "
                "builder time): %s",
                e,
            )
    return SPARK_CATALOG_NAME


def get_iceberg_rest_catalog(
    project: str | None = None,
    api_key: str | None = None,
    rest_uri: str | None = None,
    **properties: Any,
):
    """Return a configured PyIceberg `RestCatalog` pointing at the Hopsworks Iceberg REST catalog.

    Intended for reading Iceberg feature groups from external engines.
    Requires the `pyiceberg` package.
    """
    try:
        from pyiceberg.catalog.rest import RestCatalog
    except ImportError as e:
        raise ImportError(
            "get_iceberg_rest_catalog requires pyiceberg; install it with `pip install pyiceberg`."
        ) from e

    resolved_uri, resolved_key, resolved_project = _endpoint_and_credentials()
    rest_uri = rest_uri or resolved_uri
    api_key = api_key or resolved_key
    project = project or resolved_project

    config = {
        "uri": rest_uri,
        "header.Authorization": f"ApiKey {api_key}",
        **properties,
    }
    if project:
        config["warehouse"] = project
    return RestCatalog(name=SPARK_CATALOG_NAME, **config)
