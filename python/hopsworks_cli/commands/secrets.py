"""Account-level secrets management commands"""

import click
import hopsworks
from pathlib import Path
from hopsworks_cli.auth import get_connection
from hopsworks_cli.output import OutputFormatter, print_success, print_error, print_warning
from hopsworks_cli.utils.exceptions import ResourceNotFoundError


@click.group()
def secrets():
    """Manage account-level secrets"""
    pass


@secrets.command("list")
@click.pass_context
def list_secrets(ctx):
    """
    List all account-level secrets (does not show values)

    Example:
        hopsworks secret list
    """
    try:
        get_connection(ctx, require_project=False)
        secrets_api = hopsworks.get_secrets_api()
        secrets_list = secrets_api.get_secrets()

        if not secrets_list:
            print("No secrets found")
            return

        # Filter to account-level (PRIVATE visibility) secrets only
        account_secrets = [s for s in secrets_list if getattr(s, "visibility", None) == "PRIVATE"]

        if not account_secrets:
            print("No account-level secrets found")
            return

        # Format secret data (without values for security)
        secrets_data = []
        for secret in account_secrets:
            secret_info = {
                "name": secret.name,
                "scope": "account",
            }
            secrets_data.append(secret_info)

        # Output formatted results
        formatter = OutputFormatter()
        output = formatter.format(secrets_data, ctx.obj["output_format"])
        click.echo(output)

    except Exception as e:
        print_error(f"Failed to list secrets: {e}")
        if ctx.obj.get("verbose"):
            raise
        ctx.exit(1)


@secrets.command("get")
@click.argument("name")
@click.option("--show-value", is_flag=True, help="Show the secret value (use with caution)")
@click.pass_context
def get_secret(ctx, name, show_value):
    """
    Get account-level secret metadata or value

    Example:
        hopsworks secret get my_secret
        hopsworks secret get my_secret --show-value
    """
    try:
        get_connection(ctx, require_project=False)
        secrets_api = hopsworks.get_secrets_api()

        if show_value:
            # Get the secret value
            print_warning("⚠️  Displaying secret value - use with caution!")
            try:
                secret_value = secrets_api.get(name)
            except Exception as e:
                raise ResourceNotFoundError(f"Secret '{name}' not found")

            if not secret_value:
                raise ResourceNotFoundError(f"Secret '{name}' not found")

            # Output the secret value
            if ctx.obj["output_format"] == "json":
                import json
                click.echo(json.dumps({"name": name, "value": secret_value}))
            else:
                click.echo(f"Secret value for '{name}':")
                click.echo(secret_value)
        else:
            # Get secret metadata only
            try:
                secret = secrets_api.get_secret(name)
            except Exception as e:
                raise ResourceNotFoundError(f"Secret '{name}' not found")

            if not secret:
                raise ResourceNotFoundError(f"Secret '{name}' not found")

            # Build secret information (no value)
            secret_data = {
                "name": secret.name,
                "scope": "account",
            }

            # Output formatted results
            formatter = OutputFormatter()
            output = formatter.format(secret_data, ctx.obj["output_format"])
            click.echo(output)

    except ResourceNotFoundError as e:
        print_error(str(e))
        ctx.exit(1)
    except Exception as e:
        print_error(f"Failed to get secret: {e}")
        if ctx.obj.get("verbose"):
            raise
        ctx.exit(1)


@secrets.command("create")
@click.argument("name")
@click.option("--value", help="Secret value (not recommended, use --value-file instead)")
@click.option("--value-file", type=click.Path(exists=True), help="Path to file containing secret value")
@click.pass_context
def create_secret(ctx, name, value, value_file):
    """
    Create a new account-level secret

    Account-level secrets are accessible across all your projects and are useful
    for storing credentials, API keys, and other sensitive configuration.

    Example:
        hopsworks secret create my_api_key --value "secret123"
        hopsworks secret create my_token --value-file /path/to/token.txt
        hopsworks secret create my_password   # Prompts for value
    """
    try:
        # Validate inputs
        if not value and not value_file:
            # Prompt for value if not provided
            secret_value = click.prompt("Enter secret value", hide_input=True, confirmation_prompt=True)
        elif value and value_file:
            print_error("Cannot provide both --value and --value-file")
            ctx.exit(1)
        else:
            # Get secret value
            if value_file:
                secret_value = Path(value_file).read_text().strip()
            else:
                secret_value = value

        get_connection(ctx, require_project=False)
        secrets_api = hopsworks.get_secrets_api()

        click.echo(f"Creating account-level secret '{name}'...")

        # Create the secret with PRIVATE visibility (account-level)
        # The API should default to PRIVATE but we can try to enforce it
        secrets_api.create_secret(name, secret_value)

        print_success(f"Secret '{name}' created successfully")

        # Show confirmation (no value)
        secret_data = {
            "name": name,
            "scope": "account",
            "status": "created",
        }

        formatter = OutputFormatter()
        output = formatter.format(secret_data, ctx.obj["output_format"])
        click.echo(output)

    except Exception as e:
        print_error(f"Failed to create secret: {e}")
        if ctx.obj.get("verbose"):
            raise
        ctx.exit(1)


@secrets.command("delete")
@click.argument("name")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def delete_secret(ctx, name, yes):
    """
    Delete an account-level secret

    Example:
        hopsworks secret delete my_secret
        hopsworks secret delete my_secret --yes   # Skip confirmation
    """
    try:
        get_connection(ctx, require_project=False)
        secrets_api = hopsworks.get_secrets_api()

        # Verify secret exists
        try:
            secret = secrets_api.get_secret(name)
        except Exception as e:
            raise ResourceNotFoundError(f"Secret '{name}' not found")

        if not secret:
            raise ResourceNotFoundError(f"Secret '{name}' not found")

        # Confirm deletion
        if not yes:
            if not click.confirm(f"Are you sure you want to delete secret '{name}'?"):
                click.echo("Deletion cancelled")
                return

        # Delete the secret
        secrets_api.delete(name)

        print_success(f"Secret '{name}' deleted successfully")

    except ResourceNotFoundError as e:
        print_error(str(e))
        ctx.exit(1)
    except Exception as e:
        print_error(f"Failed to delete secret: {e}")
        if ctx.obj.get("verbose"):
            raise
        ctx.exit(1)


@secrets.command("update")
@click.argument("name")
@click.option("--value", help="New secret value (not recommended, use --value-file instead)")
@click.option("--value-file", type=click.Path(exists=True), help="Path to file containing new secret value")
@click.pass_context
def update_secret(ctx, name, value, value_file):
    """
    Update an existing account-level secret

    Example:
        hopsworks secret update my_secret --value "new_value"
        hopsworks secret update my_secret --value-file /path/to/new_token.txt
        hopsworks secret update my_secret   # Prompts for new value
    """
    try:
        # Validate inputs
        if not value and not value_file:
            # Prompt for value if not provided
            secret_value = click.prompt("Enter new secret value", hide_input=True, confirmation_prompt=True)
        elif value and value_file:
            print_error("Cannot provide both --value and --value-file")
            ctx.exit(1)
        else:
            # Get secret value
            if value_file:
                secret_value = Path(value_file).read_text().strip()
            else:
                secret_value = value

        get_connection(ctx, require_project=False)
        secrets_api = hopsworks.get_secrets_api()

        # Verify secret exists
        try:
            secret = secrets_api.get_secret(name)
        except Exception as e:
            raise ResourceNotFoundError(f"Secret '{name}' not found")

        if not secret:
            raise ResourceNotFoundError(f"Secret '{name}' not found")

        click.echo(f"Updating secret '{name}'...")

        # Delete and recreate (Hopsworks API pattern)
        secrets_api.delete(name)
        secrets_api.create_secret(name, secret_value)

        print_success(f"Secret '{name}' updated successfully")

    except ResourceNotFoundError as e:
        print_error(str(e))
        ctx.exit(1)
    except Exception as e:
        print_error(f"Failed to update secret: {e}")
        if ctx.obj.get("verbose"):
            raise
        ctx.exit(1)
