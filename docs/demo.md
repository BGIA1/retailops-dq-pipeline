# Demo

Run:

```bash
retaildq demo --config configs/local.yaml
```

The demo:

1. Cleans only demo-prefixed outputs when configured.
2. Generates deterministic synthetic raw data.
3. Runs raw to silver to gold.
4. Validates data quality and writes quarantine.
5. Generates markdown and JSON reports.
6. Builds a static HTML site under `site/generated`.

Review:

- `data/raw/demo-sample`
- `data/silver/demo-sample`
- `data/gold/demo-sample`
- `data/quarantine/demo-sample`
- `examples/demo`
- `site/generated/index.html`

Expected outputs include DQ summary, invalid record counts, gold metrics, lineage, and run metadata.
