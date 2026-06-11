# Docker

The Docker image packages the CLI and project configs/contracts for batch execution.

```bash
docker build -t retaildq-lakehouse .
docker run --rm retaildq-lakehouse retaildq --help
docker compose run --rm retaildq retaildq demo --config configs/docker.yaml
```

The container runs as a non-root user and avoids copying `.env`, `.venv`, generated lakehouse data, caches, and local databases into the image.
