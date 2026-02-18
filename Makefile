.PHONY: help install dev prod build up down logs clean test lint

help:
	@echo "Enthalpy Calculator - Available Commands"
	@echo "========================================="
	@echo "install         - Install dependencies"
	@echo "dev             - Run in development mode"
	@echo "prod            - Run in production mode"
	@echo "build           - Build Docker image"
	@echo "up              - Start Docker container"
	@echo "down            - Stop Docker container"
	@echo "logs            - View Docker logs"
	@echo "test            - Run tests"
	@echo "lint            - Run code linter"
	@echo "clean           - Clean up generated files"

install:
	pip install -r requirements.txt

dev:
	FLASK_ENV=development python hello.py

prod:
	gunicorn --bind 0.0.0.0:5010 --workers 4 --timeout 120 wsgi:app

build:
	docker build -t enthalpy-calculator .

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	rm -rf __pycache__ *.pyc *.egg-info dist build .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -f newFile.xlsx

test:
	python -m pytest tests/ -v

lint:
	flake8 . --max-line-length=127 --exclude=venv,__pycache__
	pylint hello.py calculator.py handleSpreadsheet.py || true

docker-build-local:
	docker build -t enthalpy-calc:dev .

docker-run-local:
	docker run -p 5010:5010 -v $(PWD)/uploads:/app/uploads enthalpy-calc:dev
