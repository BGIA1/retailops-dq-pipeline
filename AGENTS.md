# Agent Guardrails

Future agents working in this repository must follow these rules:

- Do not create cloud resources without explicit user permission.
- Do not run Azure, AWS, GCP, Terraform, Pulumi, or similar deployment commands unless the user explicitly asks for a real deployment.
- Do not push to git remotes or create remote repositories.
- Do not use real secrets, real credentials, real PII, or external datasets.
- Do not create `.env` files with real values.
- Do not modify critical workflows without human review.
- Keep the project pipeline-first; do not turn it into a dashboard-focused project.
- Keep V1 batch-oriented. Do not add FastAPI, Streamlit, Spark, dbt, Terraform, auth, or persistent services unless explicitly requested.
- Every feature should include focused tests and documentation updates.
- Keep local and cloud costs controlled and clearly documented.
- Preserve quarantine traceability and data contract behavior.
