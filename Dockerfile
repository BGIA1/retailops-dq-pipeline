FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system retaildq && adduser --system --ingroup retaildq retaildq

COPY pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs
COPY contracts ./contracts
COPY sql ./sql

RUN python -m pip install --upgrade pip \
    && python -m pip install .

RUN mkdir -p /app/data/raw /app/data/silver /app/data/gold /app/data/quarantine /app/site/generated /app/examples/demo \
    && chown -R retaildq:retaildq /app

USER retaildq

CMD ["retaildq", "--help"]
