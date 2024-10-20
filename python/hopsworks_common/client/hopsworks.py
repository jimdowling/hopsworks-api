#
#   Copyright 2020 Logical Clocks AB
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

import os
from pathlib import Path

import requests
from hopsworks_common.client import auth, base


try:
    import jks
except ImportError:
    pass


class Client(base.Client):
    HOPSWORKS_HOSTNAME_VERIFICATION = "HOPSWORKS_HOSTNAME_VERIFICATION"
    DOMAIN_CA_TRUSTSTORE_PEM = "DOMAIN_CA_TRUSTSTORE_PEM"
    PROJECT_ID = "HOPSWORKS_PROJECT_ID"
    PROJECT_NAME = "HOPSWORKS_PROJECT_NAME"
    HADOOP_USER_NAME = "HADOOP_USER_NAME"
    MATERIAL_DIRECTORY = "MATERIAL_DIRECTORY"
    HDFS_USER = "HDFS_USER"
    T_CERTIFICATE = "t_certificate"
    K_CERTIFICATE = "k_certificate"
    TRUSTSTORE_SUFFIX = "__tstore.jks"
    KEYSTORE_SUFFIX = "__kstore.jks"
    PEM_CA_CHAIN = "ca_chain.pem"
    CERT_KEY_SUFFIX = "__cert.key"
    MATERIAL_PWD = "material_passwd"
    SECRETS_DIR = "SECRETS_DIR"

    def __init__(self, hostname_verification):
        """Initializes a client being run from a job/notebook directly on Hopsworks."""
        self._base_url = self._get_hopsworks_rest_endpoint()
        self._host, self._port = self._get_host_port_pair()
        self._secrets_dir = (
            os.environ[self.SECRETS_DIR] if self.SECRETS_DIR in os.environ else "/tmp"
        )
        self._cert_key = self._get_cert_pw()

        self._hostname_verification = os.environ.get(
            self.HOPSWORKS_HOSTNAME_VERIFICATION, "{}".format(hostname_verification)
        ).lower() in ("true", "1", "y", "yes")
        self._hopsworks_ca_trust_store_path = self._materialize_ca_chain()

        self._project_id = os.environ[self.PROJECT_ID]
        self._project_name = self._project_name()
        try:
            self._auth = auth.BearerAuth(self._read_jwt())
        except FileNotFoundError:
            self._auth = auth.ApiKeyAuth(self._read_apikey())
        self._verify = self._get_verify(
            self._hostname_verification, self._hopsworks_ca_trust_store_path
        )
        self._session = requests.session()

        self._connected = True

        credentials = self._get_credentials(self._project_id)

        self._write_pem_file(credentials["clientCert"], self._get_client_cert_path())
        self._write_pem_file(credentials["clientKey"], self._get_client_key_path())
        os.environ["HOPSWORKS_CERT_DIR"]= self._secrets_dir

    def _materialize_ca_chain(self):
        """Convert truststore from jks to pem and return the location"""
        ca_chain_path = Path(self._get_ca_chain_path())
        if not ca_chain_path.exists():
            keystore_pw = self._cert_key
            ks = jks.KeyStore.load(
                self._get_jks_key_store_path(), keystore_pw, try_decrypt_keys=True
            )
            ts = jks.KeyStore.load(
                self._get_jks_trust_store_path(), keystore_pw, try_decrypt_keys=True
            )
            self._write_ca_chain(ks, ts, ca_chain_path)
        return str(ca_chain_path)

    def _get_hopsworks_rest_endpoint(self):
        """Get the hopsworks REST endpoint for making requests to the REST API."""
        return os.environ[self.REST_ENDPOINT]

    def _get_ca_chain_path(self) -> str:
        return os.path.join(self._secrets_dir, "ca_chain.pem")

    def _get_client_cert_path(self) -> str:
        return os.path.join(self._secrets_dir, "client_cert.pem")

    def _get_client_key_path(self) -> str:
        return os.path.join(self._secrets_dir, "client_key.pem")

    def _get_jks_trust_store_path(self):
        """
        Get truststore location

        Returns:
             truststore location
        """
        t_certificate = Path(self.T_CERTIFICATE)
        if t_certificate.exists():
            return str(t_certificate)
        else:
            username = os.environ[self.HADOOP_USER_NAME]
            material_directory = Path(os.environ[self.MATERIAL_DIRECTORY])
            return str(material_directory.joinpath(username + self.TRUSTSTORE_SUFFIX))

    def _get_jks_key_store_path(self):
        """
        Get keystore location

        Returns:
             keystore location
        """
        k_certificate = Path(self.K_CERTIFICATE)
        if k_certificate.exists():
            return str(k_certificate)
        else:
            username = os.environ[self.HADOOP_USER_NAME]
            material_directory = Path(os.environ[self.MATERIAL_DIRECTORY])
            return str(material_directory.joinpath(username + self.KEYSTORE_SUFFIX))

    def _project_name(self):
        try:
            return os.environ[self.PROJECT_NAME]
        except KeyError:
            pass

        hops_user = self._project_user()
        # project users have username project__user:
        hops_user_split = hops_user.split("__")
        project = hops_user_split[0]
        return project

    def _project_user(self):
        try:
            hops_user = os.environ[self.HADOOP_USER_NAME]
        except KeyError:
            hops_user = os.environ[self.HDFS_USER]
        return hops_user

    def _get_cert_pw(self):
        """
        Get keystore password from local container

        Returns:
            Certificate password
        """
        pwd_path = Path(self.MATERIAL_PWD)
        if not pwd_path.exists():
            username = os.environ[self.HADOOP_USER_NAME]
            material_directory = Path(os.environ[self.MATERIAL_DIRECTORY])
            pwd_path = material_directory.joinpath(username + self.CERT_KEY_SUFFIX)

        with pwd_path.open() as f:
            return f.read()

    def replace_public_host(self, url):
        """replace hostname to public hostname set in HOPSWORKS_PUBLIC_HOST"""
        ui_url = url._replace(netloc=os.environ[self.HOPSWORKS_PUBLIC_HOST])
        return ui_url

    def _is_external(self):
        return False

    @property
    def host(self):
        return self._host
