.PHONY: help install install-dev test lint format clean run-server run-frontend run-cli docker-build

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install production dependencies
	pip install -e .

install-dev:  ## Install development dependencies
	pip install -e ".[dev,test]"
	cd frontend && npm install
	pre-commit install

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage report
	pytest --cov=arbfinder --cov-report=html --cov-report=term

lint:  ## Run linters
	flake8 backend/
	mypy backend/
	cd frontend && npm run lint

format:  ## Format code with black
	black backend/

clean:  ## Clean build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run-server:  ## Run the API server
	uvicorn arbfinder.api.main:app --reload --port 8080

run-frontend:  ## Run the frontend dev server
	cd frontend && npm run dev

run-cli:  ## Run the CLI in interactive mode
	python -m arbfinder.cli --interactive

docker-build:  ## Build Docker image
	docker build -t arbfinder-suite .

docker-run:  ## Run Docker container
	docker run -p 8080:8080 -p 3000:3000 arbfinder-suite

setup-db:  ## Initialize database
	python -c "from arbfinder.arb_finder import db_init; db_init('~/.arb_finder.sqlite3')"

build-frontend:  ## Build frontend for production
	cd frontend && npm run build

all: install-dev lint test  ## Install, lint and test

.DEFAULT_GOAL := help
