# Contributing to pdftoceditor

Thank you for considering contributing to pdftoceditor! This document provides guidelines and instructions for setting up your development environment and contributing to the project.

## Development Environment Setup

### Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Make (optional, for using Makefile commands)
- Git (for version control)
- [direnv](https://direnv.net/) (optional, for environment management)

### Setting Up Your Environment

1. Install dependencies and set up the development environment:
   ```bash
   make setup
   ```

   Or for a stricter development environment with additional checks:
   ```bash
   make setup-strict
   ```

   If you don't have Make available, you can run these commands directly:
   ```bash
   uv sync
   uv run pre-commit install
   ```

2. Configure direnv (optional but recommended):
   ```bash
   # After installing direnv
   direnv allow
   ```
   This will:
   - Automatically load environment variables from `.env`
   - Activate the uv virtual environment using the `layout_uv` directive in `.envrc`

### IDE Configuration

When using Visual Studio Code, open the project folder and install the recommended extensions when prompted. These extensions are configured in the `.vscode/extensions.json` file to provide a consistent development experience.



## Development Workflow

### Available Make Commands

This project includes a Makefile with various commands to help with development tasks. To see all available commands:

```bash
make help
```

This will display a list of all available commands with their descriptions.

### Environment Variables

We follow a structured approach to environment variable management:

#### `.env` File - Application Configuration

The `.env` file contains application-specific configuration that can be used in both development and production:
- Database connection strings
- API keys and secrets
- Feature flags
- External service URLs

This file should:
- Have a corresponding `.env.example` template in version control with dummy values
- Be usable in both development and production environments

Example `.env` file:
```
DATABASE_URL=postgresql://user@localhost:5432/dbname
API_KEY=your_api_key_here
FEATURE_FLAG_NEW_UI=true
```

#### `.envrc` File - Development Environment Only

The `.envrc` file (used by direnv) contains development-specific settings:
- PATH adjustments
- Tool configurations
- Development convenience settings
- uv virtual environment activation (via `layout_uv`)

This file should:
- Be committed to version control (without sensitive information)
- NEVER be used in production environments
- Focus only on development workflow optimization

Example `.envrc` file:
```
# Automatically activate uv environment
layout uv

# Development-specific settings
export DEBUG=true
export PYTHONBREAKPOINT=ipdb.set_trace
export PYTHONPATH=$PWD:$PYTHONPATH
```

#### Using Environment Variables

With direnv properly configured:
1. Environment variables from both `.env` and `.envrc` will be automatically loaded when you enter the project directory
2. The uv virtual environment will be automatically activated
3. All settings will be unloaded when you leave the directory

#### Production Environment

For production deployments:
- Use the `.env` file for application-specific configuration
- Load environment variables using a proper environment variable management system for your deployment platform
- Do NOT use direnv or `.envrc` files in production
- Consider using a secrets management service for sensitive credentials

### Running Tests

To run the test suite:

```bash
make test
```

Or without Make:
```bash
uv run pytest
```

### Code Formatting and Linting

To format and lint your code:

```bash
make lint
```

This will run all configured linters and formatters using pre-commit hooks, including both standard and strict rules.



## Working with Private Python Packages

### Adding Python Package Registry Credentials

If you need to use private Python packages, you must add index specific credentials like so:

```bash
echo "UV_INDEX_SUPER_SECRET_REPO_USERNAME=clark" >> .env.build
echo "UV_INDEX_SUPER_SECRET_REPO_PASSWORD=kent" >> .env.build
```

Once the new environment variables are exported, you can add your super secret package like this:

```bash
uv add my-superawesome-package --index super-secret-repo=https://your.super.secret.com/package/repository/pypi/simple
```

> Remember that the name of your index (super-secret-repo) and the name of the environment have to match. When searching for credentials `uv` will automatically search for environment variables which include the index name, but will make it uppercase and replace dashes (-) with underscores (_).

In case this package repository should _only_ be used for specific packages you'll need to add `explicit = true` under the `[[tool.uv.index]]` section of your newly added index.
For a full explanation of configuring custom indexes and other authentication methods have a look at the [astral documentation page](https://docs.astral.sh/uv/concepts/projects/dependencies/#index).

## Release Process

### Versioning

This project follows [Semantic Versioning](https://semver.org/) (SemVer).

To bump the project version:

```bash
make bump
# or specify the version part explicitly
make bump VERSION_PART=minor
```

Valid VERSION_PART values are: major, minor, or patch.

This will:
1. Update the version in the project metadata
2. Create a commit with the version change
3. Create a version tag

After bumping the version, you need to push both the commit and the tag to the remote repository:

```bash
git push  # Push the version bump commit
git push --tags  # Push the new version tag
```

## Submitting Changes

1. Create a new branch for your changes
2. Make your changes and commit them with clear, descriptive messages
3. Push your branch and create a pull/merge request
4. Ensure all CI checks pass on your changes

Thank you for contributing to pdftoceditor!
