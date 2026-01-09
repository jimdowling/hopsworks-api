"""Modal-style token flow with polling for Hopsworks CLI"""

import time
import webbrowser
import requests
from typing import Optional, Dict


class TokenFlowError(Exception):
    """Token flow error"""
    pass


class TokenFlowHandler:
    """Manages token flow with backend polling"""

    def __init__(self, host: str, port: int = 443):
        """
        Initialize token flow handler

        Args:
            host: Hopsworks hostname
            port: Hopsworks port
        """
        self.host = host
        self.port = port
        self.base_url = f"https://{host}:{port}/hopsworks-api/api"

    def start_flow(self, timeout: int = 300) -> Dict[str, str]:
        """
        Start token flow

        Args:
            timeout: Maximum time to wait for completion (seconds)

        Returns:
            Dictionary with 'api_key' and optionally 'workspace'

        Raises:
            TokenFlowError: If token flow fails
        """
        # Step 1: Create token flow session
        print("Initiating token flow...")
        create_url = f"{self.base_url}/token-flow/create"

        try:
            response = requests.post(create_url, verify=False, timeout=10)
            response.raise_for_status()
            data = response.json()

            flow_id = data["flowId"]
            wait_secret = data["waitSecret"]
            web_url = data["webUrl"]

        except requests.exceptions.RequestException as e:
            raise TokenFlowError(f"Failed to create token flow: {e}")

        # Step 2: Open browser
        print(f"\nOpening browser for authentication...")
        print(f"If the browser doesn't open automatically, visit: {web_url}")
        print()

        try:
            webbrowser.open(web_url)
        except Exception:
            pass  # Browser open is optional

        # Step 3: Poll for completion
        print("Waiting for authentication in web browser...")
        wait_url = f"{self.base_url}/token-flow/wait/{flow_id}"
        params = {"wait_secret": wait_secret, "timeout": 40}

        start_time = time.time()
        attempt = 1

        while time.time() - start_time < timeout:
            try:
                print(f"Polling for completion (attempt {attempt})...")
                response = requests.get(
                    wait_url,
                    params=params,
                    verify=False,
                    timeout=45
                )
                response.raise_for_status()
                result = response.json()

                if not result.get("timeout"):
                    # Success!
                    print("\nAuthentication complete!")
                    return {
                        "api_key": result["apiKey"],
                        "workspace": result.get("workspaceUsername")
                    }

                # Backend timeout, retry
                attempt += 1

            except requests.exceptions.RequestException as e:
                raise TokenFlowError(f"Polling failed: {e}")

        raise TokenFlowError(f"Authentication timed out after {timeout} seconds")
