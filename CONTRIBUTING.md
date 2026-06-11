# Contributing

Use Conventional Commits so Release Please can prepare changelogs and releases.

Before opening a pull request:

```bash
pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy src
pytest --cov=retaildq --cov-report=term-missing
retaildq demo --config configs/ci.yaml
docker build -t retaildq-lakehouse:local .
```

Do not commit generated local lakehouse data under `data/raw`, `data/silver`, `data/gold`, or `data/quarantine`. Sample demo reports under `examples/demo` are allowed when intentionally regenerated from synthetic data.

Never commit secrets, real customer data, PII, tenant IDs, subscription IDs, or production resource names.
