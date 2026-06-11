# GitHub Actions

## CI

`.github/workflows/ci.yml` runs on push and pull request to `main`:

- Python 3.11 setup.
- Dev dependency install.
- Ruff check.
- Ruff format check.
- Mypy.
- Pytest with coverage.
- `retaildq demo --config configs/ci.yaml`.
- Docker build.

Permissions are limited to `contents: read`.

## CodeQL

`.github/workflows/codeql.yml` analyzes Python and grants only the permissions required for security events.

## Dependabot

`.github/dependabot.yml` covers pip, GitHub Actions, and Docker updates.

## Release Please

`.github/workflows/release-please.yml` prepares release pull requests from Conventional Commits.

## Pages

`.github/workflows/pages.yml` builds a small synthetic demo and publishes `site/generated` to GitHub Pages. It does not require secrets.

## Azure Manual

`.github/workflows/azure-deploy-manual.yml` is manual only and protected by the `azure-demo` environment. It uses OIDC placeholders and must be configured after the repository is created.
