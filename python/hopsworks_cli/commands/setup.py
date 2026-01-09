"""Interactive setup command with OAuth authentication"""

import click
import os
import sys
from pathlib import Path
import hopsworks
from hopsworks_common import client
from hopsworks_cli.token_flow import TokenFlowHandler, TokenFlowError
from hopsworks_cli.config import Config, CONFIG_DIR
from hopsworks_cli.output import print_success, print_error, print_warning
from hopsworks_cli.utils.exceptions import AuthenticationError


@click.command()
@click.option("--host", help="Hopsworks host (defaults to eu-west.cloud.hopsworks.ai)")
@click.option("--port", type=int, default=443, help="Hopsworks port")
@click.option("--profile", default="default", help="Profile name to save credentials to")
@click.pass_context
def setup(ctx, host, port, profile):
    """
    Interactive setup with OAuth authentication

    Opens browser for login/registration and stores credentials locally.

    Example:
        hopsworks setup
        hopsworks setup --host custom.hopsworks.ai
        hopsworks setup --profile production
    """
    try:
        # Use default host from config if not provided
        if not host:
            config = Config()
            config.load()
            default_profile = config.get_profile("default")
            host = default_profile.host

        click.echo(f"Setting up Hopsworks CLI for {host}:{port}")
        click.echo(f"Profile: {profile}")
        click.echo()

        # Start token flow
        token_handler = TokenFlowHandler(host, port)

        try:
            credentials = token_handler.start_flow(timeout=300)
            api_key = credentials["api_key"]
        except TokenFlowError as e:
            print_error(f"Token flow failed: {e}")
            sys.exit(1)

        print_success("Authentication successful!")
        click.echo()

        # Validate API key by trying to connect
        click.echo("Validating API key...")
        try:
            connection = hopsworks.login(
                host=host,
                port=port,
                api_key_value=api_key,
                hostname_verification=False,
            )
        except Exception as e:
            print_error(f"Failed to validate API key: {e}")
            sys.exit(1)

        print_success("API key validated")
        click.echo()

        # Get list of projects
        click.echo("Fetching your projects...")
        try:
            projects_list = connection.get_projects()
        except Exception as e:
            print_error(f"Failed to fetch projects: {e}")
            sys.exit(1)

        # Select project
        selected_project = None
        if not projects_list:
            print_warning("No projects found. You can create one later or specify one manually.")
        elif len(projects_list) == 1:
            selected_project = projects_list[0].name
            print_success(f"Using project: {selected_project}")
        else:
            click.echo("\nAvailable projects:")
            for idx, project in enumerate(projects_list, 1):
                click.echo(f"  {idx}. {project.name}")

            while True:
                choice = click.prompt(
                    "\nSelect a project number (or 0 to skip)",
                    type=int,
                    default=1
                )
                if choice == 0:
                    print_warning("Skipping project selection. You can set it later with: hopsworks project <name>")
                    break
                elif 1 <= choice <= len(projects_list):
                    selected_project = projects_list[choice - 1].name
                    print_success(f"Selected project: {selected_project}")
                    break
                else:
                    print_error(f"Invalid choice. Please select 1-{len(projects_list)} or 0 to skip.")

        click.echo()

        # Create config directory if it doesn't exist
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        os.chmod(CONFIG_DIR, 0o700)

        # Save API key to file
        api_key_file = CONFIG_DIR / f"api_key_{profile}"
        api_key_file.write_text(api_key)
        os.chmod(api_key_file, 0o600)

        # Save configuration
        config = Config()
        config.load()
        config.add_profile(
            name=profile,
            host=host,
            port=port,
            project=selected_project,
            api_key_file=str(api_key_file)
        )
        config.set_default_profile(profile)
        config.save()

        print_success(f"Configuration saved to {CONFIG_DIR / 'config.yaml'}")
        print_success(f"API key saved to {api_key_file}")
        click.echo()

        # Show next steps
        click.echo("Setup complete! Try these commands:")
        click.echo("  hopsworks projects list       - List all your projects")
        if selected_project:
            click.echo("  hopsworks users               - List project members")
            click.echo("  hopsworks feature-groups list - List feature groups")
        else:
            click.echo("  hopsworks project <name>      - Set your active project")
        click.echo()

    except KeyboardInterrupt:
        print_warning("\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Setup failed: {e}")
        if ctx.obj and ctx.obj.get("verbose"):
            raise
        sys.exit(1)
