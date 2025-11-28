# GavatCore Development Makefile

.PHONY: help install test lint format clean run health docker

# Default target
help:
	@echo "GavatCore Development Commands:"
	@echo "  install     - Install dependencies and setup development environment"
	@echo "  test        - Run all tests"
	@echo "  test-unit   - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  lint        - Run code linting (flake8, mypy, bandit)"
	@echo "  format      - Format code (black, isort)"
	@echo "  clean       - Clean temporary files and caches"
	@echo "  run         - Start the full GavatCore system"
	@echo "  run-bots    - Start only bots"
	@echo "  run-apis    - Start only APIs"
	@echo "  health      - Perform system health check"
	@echo "  docker      - Build and run with Docker"
	@echo "  pre-commit  - Setup pre-commit hooks"

# Installation and setup
install:
	pip install -r requirements.txt
	pip install pre-commit
	pre-commit install

# Testing
test:
	pytest --cov=. --cov-report=html --cov-report=term-missing

test-unit:
	pytest -m unit --cov=. --cov-report=term-missing

test-integration:
	pytest -m integration

test-performance:
	pytest -m performance

test-security:
	pytest -m security

# Code quality
lint:
	flake8 . --max-line-length=100 --ignore=E203,W503
	mypy . --ignore-missing-imports --no-strict-optional
	bandit -r . -x tests/,venv/,.venv/

format:
	black . --line-length=100
	isort . --profile=black --line-length=100

check: lint test

# Application commands
run:
	python gavatcore.py --components all

run-bots:
	python gavatcore.py --components bots

run-apis:
	python gavatcore.py --components apis

health:
	python gavatcore.py --health-check

# Development utilities
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	rm -rf build/ dist/

pre-commit:
	pre-commit install
	pre-commit run --all-files

# Docker commands
docker-build:
	docker build -t gavatcore:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Database commands
db-migrate:
	cd gavatcore-api && alembic upgrade head

db-reset:
	rm -f data/gavatcore.db
	cd gavatcore-api && alembic upgrade head

# Flutter commands
flutter-setup:
	cd gavatcore_panel && flutter pub get

flutter-build:
	cd gavatcore_panel && flutter build web

flutter-run:
	cd gavatcore_panel && flutter run -d chrome

# Maintenance
update-deps:
	pip-compile requirements.in
	pip install -r requirements.txt

security-scan:
	bandit -r . -f json -o security-report.json
	safety check

backup-sessions:
	tar -czf sessions-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz sessions/

# CI/CD helpers
ci-install:
	pip install -r requirements.txt

ci-test:
	pytest --cov=. --cov-report=xml --junitxml=junit.xml

ci-lint:
	flake8 . --format=junit-xml --output-file=flake8-report.xml
	mypy . --junit-xml=mypy-report.xml
