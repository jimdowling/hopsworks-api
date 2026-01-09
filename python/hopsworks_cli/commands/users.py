"""Project users/members management commands"""

import click
from hopsworks_common import client
from hopsworks_cli.auth import get_connection
from hopsworks_cli.output import OutputFormatter, print_error
from hopsworks_cli.utils.exceptions import ResourceNotFoundError


@click.command()
@click.option("--project", help="Project name (uses default if not specified)")
@click.pass_context
def users(ctx, project):
    """
    List users in the current project

    Shows email addresses and roles of all project members.

    Example:
        hopsworks users
        hopsworks users --project my_project
    """
    try:
        # Get connection with project context
        connection = get_connection(ctx, project=project, require_project=True)

        # Get the current project name
        project_name = project or ctx.obj.get("project")

        if not project_name:
            print_error("No project specified. Use --project or set a default project with: hopsworks project <name>")
            ctx.exit(1)

        click.echo(f"Fetching members of project '{project_name}'...")

        # Get project information which includes team members
        # The connection.get_project() method returns a Project object
        try:
            project_obj = connection.get_project(project_name)
        except Exception as e:
            raise ResourceNotFoundError(
                f"Project '{project_name}' not found or you don't have access. "
                f"Run 'hopsworks projects list' to see available projects."
            )

        if not project_obj:
            raise ResourceNotFoundError(f"Project '{project_name}' not found")

        # Extract team members from project
        # The project object should have a team attribute or we need to fetch it separately
        try:
            # Try to get team members via the client API
            # The project endpoint returns team information
            conn = client.get_connection()
            projects_list = conn.get_projects()

            # Find our project in the list
            target_project = None
            for proj in projects_list:
                if proj.name == project_name:
                    target_project = proj
                    break

            if not target_project:
                raise ResourceNotFoundError(f"Project '{project_name}' not found")

            # Get team members - check if the project has a project_team attribute
            team_members = []
            if hasattr(target_project, "project_team") and target_project.project_team:
                for member in target_project.project_team:
                    user_info = {
                        "email": member.user.email if hasattr(member, "user") else "N/A",
                        "role": member.team_role if hasattr(member, "team_role") else "N/A",
                        "added": str(member.timestamp) if hasattr(member, "timestamp") else "N/A",
                    }
                    team_members.append(user_info)
            elif hasattr(target_project, "team") and target_project.team:
                # Alternative structure
                for member in target_project.team:
                    user_info = {
                        "email": getattr(member, "email", "N/A"),
                        "role": getattr(member, "role", "N/A"),
                    }
                    team_members.append(user_info)

            if not team_members:
                print(f"No team members found for project '{project_name}' or team information is not accessible")
                return

            # Output formatted results
            formatter = OutputFormatter()
            output = formatter.format(team_members, ctx.obj["output_format"])
            click.echo(output)

        except AttributeError as e:
            # Project object doesn't have team information
            print_error(
                f"Unable to retrieve team members for project '{project_name}'. "
                f"Team information may not be accessible through this API."
            )
            if ctx.obj.get("verbose"):
                print_error(f"Error details: {e}")
            ctx.exit(1)

    except ResourceNotFoundError as e:
        print_error(str(e))
        ctx.exit(1)
    except Exception as e:
        print_error(f"Failed to list users: {e}")
        if ctx.obj.get("verbose"):
            raise
        ctx.exit(1)
