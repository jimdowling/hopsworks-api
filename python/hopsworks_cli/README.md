# Hopsworks CLI

Command-line interface for managing Hopsworks resources including projects, models, deployments, feature groups, secrets, and more.

## Installation

Install the Hopsworks CLI with the CLI extra dependencies:

```bash
pip install "hopsworks[cli]"
```

### Installation Options

**Option 1: Virtual Environment (Recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install "hopsworks[cli]"
hopsworks setup  # Ready to use!
```

**Option 2: User Install**
```bash
pip install --user "hopsworks[cli]"
hopsworks setup  # Ready to use if ~/.local/bin is in PATH
```

> **Note**: If using `--user` install and the `hopsworks` command is not found, add `~/.local/bin` to your PATH:
> ```bash
> echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
> source ~/.bashrc
> ```

**Option 3: Development Mode**
```bash
cd python
uv sync --extra cli
source .venv/bin/activate
```

## Quick Start

Run the interactive setup to authenticate with OAuth:

```bash
hopsworks setup
```

This will:
1. Open your browser for authentication
2. Create or login to your Hopsworks account
3. Automatically store your credentials securely
4. Let you select your default project

That's it! You're ready to use the CLI.

## Commands Overview

```bash
# Setup and authentication
hopsworks setup                          # Interactive OAuth setup

# Project management
hopsworks project my_project             # Switch to a project
hopsworks projects list                  # List all projects
hopsworks users                          # List project members

# Secrets management (account-level)
hopsworks secret create my_key --value "secret123"
hopsworks secret list
hopsworks secret get my_key --show-value

# Feature Store
hopsworks feature-groups list
hopsworks feature-groups get my_fg

# Model Registry
hopsworks models list --name my_model
hopsworks models get my_model --version 1
hopsworks models download my_model --version 1

# Model Serving
hopsworks deployments list
hopsworks deployments start my_deployment
hopsworks deployments status my_deployment

# Jobs
hopsworks jobs list
hopsworks jobs run my_job
```

## Authentication

### OAuth Setup (Recommended)

The easiest way to get started:

```bash
hopsworks setup
```

This opens your browser for authentication and securely stores your credentials in `~/.hopsworks/config.yaml`.

### Using Profiles

The setup command creates a default profile. You can create multiple profiles for different environments:

```yaml
# ~/.hopsworks/config.yaml
default_profile: production

profiles:
  production:
    host: eu-west.cloud.hopsworks.ai
    port: 443
    project: prod_project
    api_key_file: ~/.hopsworks/api_key_production

  staging:
    host: staging.hopsworks.ai
    port: 443
    project: staging_project
    api_key_file: ~/.hopsworks/api_key_staging
```

Switch between profiles:

```bash
hopsworks --profile production models list
hopsworks --profile staging deployments list
```

### Manual Authentication (Advanced)

If you prefer to use API keys directly:

1. Get your API key from the Hopsworks UI
2. Save it to a file:
   ```bash
   mkdir -p ~/.hopsworks
   echo "your-api-key-here" > ~/.hopsworks/api_key
   chmod 600 ~/.hopsworks/api_key
   ```

3. Use with the CLI:
   ```bash
   hopsworks --api-key-file ~/.hopsworks/api_key projects list
   ```

Or set environment variables:

```bash
export HOPSWORKS_HOST="eu-west.cloud.hopsworks.ai"
export HOPSWORKS_PROJECT="my_project"
export HOPSWORKS_API_KEY_FILE=~/.hopsworks/api_key

hopsworks models list
```

## Detailed Command Reference

### Setup and Configuration

#### Interactive Setup

```bash
hopsworks setup
```

Configure authentication with a specific host:

```bash
hopsworks setup --host custom.hopsworks.ai
hopsworks setup --profile production
```

### Project Management

#### Switch Projects

```bash
# Quick way
hopsworks project my_project

# Full command
hopsworks projects switch my_project
```

#### List Projects

```bash
hopsworks projects list

# JSON output
hopsworks --output json projects list
```

#### Get Project Details

```bash
hopsworks projects get my_project
```

#### List Project Members

```bash
hopsworks users

# For a specific project
hopsworks users --project other_project
```

### Secrets Management

Secrets are **account-level** and accessible across all your projects.

#### Create a Secret

```bash
# Prompt for value (recommended - hidden input)
hopsworks secret create my_api_key

# Provide value directly (not recommended for sensitive data)
hopsworks secret create my_api_key --value "secret123"

# From file
hopsworks secret create my_token --value-file /path/to/token.txt
```

#### List Secrets

```bash
hopsworks secret list
```

#### Get Secret

```bash
# Get metadata only
hopsworks secret get my_api_key

# Show the actual value (use with caution)
hopsworks secret get my_api_key --show-value
```

#### Update Secret

```bash
hopsworks secret update my_api_key
```

#### Delete Secret

```bash
hopsworks secret delete my_api_key

# Skip confirmation
hopsworks secret delete my_api_key --yes
```

### Feature Groups

#### List Feature Groups

```bash
hopsworks feature-groups list

# Filter by name
hopsworks feature-groups list --name transactions
```

#### Get Feature Group Details

```bash
hopsworks feature-groups get transactions
hopsworks feature-groups get transactions --version 2
```

#### Show Feature Group Schema

```bash
hopsworks feature-groups schema transactions
hopsworks feature-groups schema transactions --version 2
```

### Models

#### List Models

```bash
# List all versions of a specific model
hopsworks models list --name my_model

# Output as JSON
hopsworks --output json models list --name my_model
```

#### Get Model Details

```bash
hopsworks models get my_model --version 1

# With JSON output
hopsworks --output json models get my_model --version 1
```

#### Get Best Model by Metric

```bash
# Get model with highest accuracy
hopsworks models best my_model --metric accuracy --direction max

# Get model with lowest loss
hopsworks models best my_model --metric loss --direction min
```

#### Download Model

```bash
# Download to current directory
hopsworks models download my_model --version 1

# Download to specific directory
hopsworks models download my_model --version 1 --output-dir ./models
```

#### Get Comprehensive Model Info

```bash
hopsworks models info my_model --version 1
```

### Deployments

#### List Deployments

```bash
hopsworks deployments list

# With JSON output
hopsworks --output json deployments list
```

#### Get Deployment Details

```bash
hopsworks deployments get my_deployment
```

#### Start Deployment

```bash
# Start and return immediately
hopsworks deployments start my_deployment

# Start and wait for it to be running (with 5-minute timeout)
hopsworks deployments start my_deployment --wait --timeout 300
```

#### Stop Deployment

```bash
# Stop and return immediately
hopsworks deployments stop my_deployment

# Stop and wait for it to be stopped
hopsworks deployments stop my_deployment --wait
```

#### Check Deployment Status

```bash
hopsworks deployments status my_deployment
```

### Jobs

#### List Jobs

```bash
hopsworks jobs list
```

#### Get Job Details

```bash
hopsworks jobs get my_job
```

#### Run a Job

```bash
# Start job and return immediately
hopsworks jobs run my_job

# Start and wait for completion
hopsworks jobs run my_job --wait
```

#### List Job Executions

```bash
hopsworks jobs executions my_job
```

#### Check Job Status

```bash
hopsworks jobs status my_job
```

## Global Options

All commands support these global options:

```bash
hopsworks [OPTIONS] COMMAND [ARGS]...

Global Options:
  --host TEXT                  Hopsworks hostname [default: eu-west.cloud.hopsworks.ai]
  --port INTEGER               Hopsworks port [default: 443]
  --project TEXT               Project name
  --api-key TEXT               API key value
  --api-key-file PATH          Path to API key file
  --profile TEXT               Configuration profile name
  --output FORMAT              Output format: json|table|yaml [default: table]
  --verbose                    Enable verbose output
  --no-verify                  Disable SSL verification
  --help                       Show help message
  --version                    Show version
```

## Output Formats

The CLI supports three output formats:

### Table (default)

```bash
hopsworks models list --name my_model
```

Output:
```
+------------+---------+------------+---------------------+
| Name       | Version | Framework  | Created             |
+------------+---------+------------+---------------------+
| my_model   | 1       | tensorflow | 2024-01-15 10:30:00 |
+------------+---------+------------+---------------------+
```

### JSON

Perfect for scripting and automation:

```bash
hopsworks --output json models list --name my_model
```

Output:
```json
[
  {
    "name": "my_model",
    "version": 1,
    "framework": "tensorflow",
    "created": "2024-01-15T10:30:00"
  }
]
```

### YAML

```bash
hopsworks --output yaml models list --name my_model
```

Output:
```yaml
- name: my_model
  version: 1
  framework: tensorflow
  created: '2024-01-15T10:30:00'
```

## Examples

### Complete ML Workflow

```bash
# Setup (first time only)
hopsworks setup

# Switch to your project
hopsworks project ml_pipeline

# List team members
hopsworks users

# Create a secret for external API
hopsworks secret create openai_api_key --value "sk-..."

# List feature groups
hopsworks feature-groups list

# List all versions of a model
hopsworks models list --name fraud_detection

# Get the best performing model
hopsworks models best fraud_detection --metric f1_score --direction max

# Download the best model
hopsworks models download fraud_detection --version 3 --output-dir ./models

# Check deployments
hopsworks deployments list

# Start a deployment
hopsworks deployments start fraud_detection_v3 --wait

# Check deployment status
hopsworks deployments status fraud_detection_v3
```

### CI/CD Integration

```bash
#!/bin/bash
# deploy.sh - Deploy best model to production

set -e

# Authenticate using stored credentials
hopsworks project production

# Get best model version
BEST_MODEL=$(hopsworks --output json models best my_model \
  --metric accuracy --direction max | jq -r '.[0].version')

echo "Best model version: $BEST_MODEL"

# Check if deployment exists and start it
if hopsworks deployments get my_model_prod &> /dev/null; then
  echo "Starting existing deployment..."
  hopsworks deployments start my_model_prod --wait
else
  echo "Deployment not found, please create it first"
  exit 1
fi

echo "Deployment successful!"
```

### Multi-Environment Setup

```bash
# Setup production environment
hopsworks setup --profile production --host eu-west.cloud.hopsworks.ai

# Setup staging environment
hopsworks setup --profile staging --host staging.hopsworks.ai

# Use different environments
hopsworks --profile production models list
hopsworks --profile staging deployments list
```

### Secret Management for CI/CD

```bash
# Store CI/CD secrets at account level
hopsworks secret create docker_registry_password --value-file ~/.docker/token
hopsworks secret create github_token --value-file ~/.github/token
hopsworks secret create aws_access_key --value "AKIA..."

# List all secrets (values hidden)
hopsworks secret list

# Use in scripts
DB_PASSWORD=$(hopsworks --output json secret get db_password --show-value | jq -r '.value')
```

## Configuration Files

### Config File Location

`~/.hopsworks/config.yaml`

### Example Configuration

```yaml
default_profile: production

profiles:
  production:
    host: eu-west.cloud.hopsworks.ai
    port: 443
    project: prod_ml_pipeline
    api_key_file: /home/user/.hopsworks/api_key_production
    engine: python

  staging:
    host: staging.hopsworks.ai
    port: 443
    project: staging_ml_pipeline
    api_key_file: /home/user/.hopsworks/api_key_staging
    engine: python

  local:
    host: localhost
    port: 8080
    project: test_project
    api_key_file: /home/user/.hopsworks/api_key_local
    engine: python
```

## Error Handling

The CLI provides clear error messages:

```bash
# Not authenticated
$ hopsworks models list
✗ Error: Authentication required. Please run:
  hopsworks setup

Or provide --api-key-file or --api-key

# Project not found
$ hopsworks project nonexistent
✗ Error: Project 'nonexistent' not found or you don't have access.
Run 'hopsworks projects list' to see available projects.

# Model not found
$ hopsworks models get nonexistent --version 1
✗ Error: Model 'nonexistent' version 1 not found

# Enable verbose mode for full stack traces
$ hopsworks --verbose models get my_model --version 1
```

## Troubleshooting

### Command Not Found

If you get `command not found: hopsworks` after installation:

1. **Check if `~/.local/bin` is in your PATH** (for `--user` installs):
   ```bash
   echo $PATH | grep -q "$HOME/.local/bin" && echo "In PATH" || echo "Not in PATH"
   ```

2. **Add to PATH if needed**:
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Or use a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install "hopsworks[cli]"
   ```

### SSL Certificate Errors

If you encounter SSL verification errors:

```bash
hopsworks --no-verify models list
```

Or configure in your profile:
```yaml
profiles:
  myprofile:
    hostname_verification: false
```

### OAuth Browser Not Opening

If the OAuth flow doesn't open your browser automatically:

1. The CLI will print the authorization URL
2. Copy and paste it into your browser manually
3. Complete the authentication
4. The CLI will detect the callback automatically

### Connection Timeouts

Increase timeout or check your network connection:

```bash
hopsworks --verbose models list
```

### Permission Errors

Ensure your API key has the necessary permissions in the Hopsworks UI.

## Development

### Running Tests

```bash
cd python
pytest tests/cli/ -v
```

### Adding New Commands

1. Create a new command module in `hopsworks_cli/commands/`
2. Define Click command group and commands
3. Register the command group in `main.py`
4. Add tests in `tests/cli/`

Example:

```python
# hopsworks_cli/commands/mycommand.py
import click
from hopsworks_cli.auth import get_connection
from hopsworks_cli.output import OutputFormatter

@click.group()
def mycommand():
    """My custom command"""
    pass

@mycommand.command("list")
@click.pass_context
def list_items(ctx):
    """List items"""
    connection = get_connection(ctx)
    # Your logic here
    click.echo("Listing items...")
```

Register in `main.py`:

```python
from hopsworks_cli.commands.mycommand import mycommand

cli.add_command(mycommand)
```

## Migration from Previous Versions

If you were using `hopsworks-cli` (deprecated):

1. The binary is now `hopsworks` (no `-cli` suffix)
2. Run `hopsworks setup` for easier OAuth authentication
3. Secrets are now account-level (not project-scoped)
4. Use `hopsworks project <name>` to switch projects easily
5. Default host is now `eu-west.cloud.hopsworks.ai`

Old commands still work with new binary name:
```bash
# Old way (still works)
hopsworks --project myproj --api-key-file ~/.hopsworks/api_key models list

# New way (recommended)
hopsworks setup  # One-time setup
hopsworks project myproj
hopsworks models list
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

Apache License 2.0 - See [LICENSE](../../LICENSE) for details.
