#
#   Copyright 2022 Logical Clocks AB
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

from typing import Literal, Optional, Union

from hopsworks_common.client import external, hopsworks


_client: Union[hopsworks.Client, external.Client, None] = None


def init(
    client_type: Union[Literal["hopsworks"], Literal["external"]],
    host: Optional[str] = None,
    port: Optional[int] = None,
    project: Optional[str] = None,
    engine: Optional[str] = None,
    region_name: Optional[str] = None,
    secrets_store=None,
    hostname_verification: Optional[bool] = None,
    trust_store_path: Optional[str] = None,
    cert_folder: Optional[str] = None,
    api_key_file: Optional[str] = None,
    api_key_value: Optional[str] = None,
) -> None:
    global _client
    if not _client:
        if client_type == "hopsworks":
            _client = hopsworks.Client()
        elif client_type == "external":
            _client = external.Client(
                host,
                port,
                project,
                engine,
                region_name,
                secrets_store,
                hostname_verification,
                trust_store_path,
                cert_folder,
                api_key_file,
                api_key_value,
            )


def get_instance() -> Union[hopsworks.Client, external.Client]:
    global _client
    if _client:
        return _client
    raise Exception("Couldn't find client. Try reconnecting to Hopsworks.")


def stop() -> None:
    global _client
    if _client:
        _client._close()
    _client = None
