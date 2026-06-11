.PHONY: install demo validate report site test lint format-check typecheck docker-build docker-demo clean

install:
	python -m pip install -e ".[dev]"

demo:
	retaildq demo --config configs/local.yaml

validate:
	retaildq validate --config configs/local.yaml

report:
	retaildq report --config configs/local.yaml --format all

site:
	retaildq site-build --config configs/local.yaml

test:
	pytest -q

lint:
	ruff check .

format-check:
	ruff format --check .

typecheck:
	mypy src

docker-build:
	docker build -t retaildq-lakehouse .

docker-demo:
	docker compose run --rm retaildq retaildq demo --config configs/docker.yaml

clean:
	retaildq clean --config configs/local.yaml --yes
