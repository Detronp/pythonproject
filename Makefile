IMAGE ?= task-api:latest

.PHONY: install test run build up down logs

install:
	pip install -r requirements-dev.txt

test:
	pytest -q

run:
	DATABASE_PATH=./tasks.db python wsgi.py

build:
	docker build -t $(IMAGE) .

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f api
