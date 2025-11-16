.PHONY: help build dev test prod playground clean clean-all poetry-lock shell run-example

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)PAuth Docker Management$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

##@ Building

build: ## Build all Docker images
	@echo "$(BLUE)Building all Docker images...$(NC)"
	docker-compose build

build-dev: ## Build development image
	@echo "$(BLUE)Building development image...$(NC)"
	docker-compose build pauth-dev

build-prod: ## Build production image
	@echo "$(BLUE)Building production image...$(NC)"
	docker-compose build pauth-prod

build-test: ## Build testing image
	@echo "$(BLUE)Building testing image...$(NC)"
	docker-compose build pauth-test

build-no-cache: ## Build all images without cache
	@echo "$(BLUE)Building all images without cache...$(NC)"
	docker-compose build --no-cache

##@ Development

dev: ## Start development environment (interactive shell)
	@echo "$(BLUE)Starting development environment...$(NC)"
	docker-compose run --rm pauth-dev bash

shell: ## Open Python shell with PAuth loaded
	@echo "$(BLUE)Starting Python shell...$(NC)"
	docker-compose run --rm pauth-dev python

poetry-shell: ## Open Poetry shell
	@echo "$(BLUE)Starting Poetry shell...$(NC)"
	docker-compose run --rm pauth-dev poetry shell

poetry-lock: ## Update Poetry lock file
	@echo "$(BLUE)Updating Poetry lock file...$(NC)"
	docker-compose run --rm pauth-dev poetry lock

poetry-install: ## Install dependencies with Poetry
	@echo "$(BLUE)Installing dependencies...$(NC)"
	docker-compose run --rm pauth-dev poetry install

poetry-update: ## Update dependencies with Poetry
	@echo "$(BLUE)Updating dependencies...$(NC)"
	docker-compose run --rm pauth-dev poetry update

##@ Testing

test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	docker-compose run --rm pauth-test

test-verbose: ## Run tests with verbose output
	@echo "$(BLUE)Running tests (verbose)...$(NC)"
	docker-compose run --rm pauth-test poetry run pytest -vv

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	docker-compose run --rm pauth-test poetry run pytest --cov=src --cov-report=term-missing --cov-report=html

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	docker-compose run --rm pauth-test poetry run pytest-watch

##@ Running Services

prod: ## Run production container
	@echo "$(BLUE)Starting production container...$(NC)"
	docker-compose up pauth-prod

prod-daemon: ## Run production container in background
	@echo "$(BLUE)Starting production container (daemon)...$(NC)"
	docker-compose up -d pauth-prod

playground: ## Start OAuth playground
	@echo "$(BLUE)Starting OAuth playground...$(NC)"
	@echo "$(GREEN)Access at: http://localhost:5000$(NC)"
	docker-compose up pauth-playground

flask-example: ## Run Flask example application
	@echo "$(BLUE)Starting Flask example...$(NC)"
	@echo "$(GREEN)Access at: http://localhost:5001$(NC)"
	docker-compose up pauth-flask-example

security-scan: ## Run security scanner
	@echo "$(BLUE)Running security scanner...$(NC)"
	docker-compose run --rm pauth-security

analytics: ## Run analytics service
	@echo "$(BLUE)Running analytics service...$(NC)"
	docker-compose run --rm pauth-analytics

##@ Examples

run-basic: ## Run basic OAuth example
	@echo "$(BLUE)Running basic example...$(NC)"
	docker-compose run --rm pauth-dev python -m src.examples.basic_example

run-async: ## Run async OAuth example
	@echo "$(BLUE)Running async example...$(NC)"
	docker-compose run --rm pauth-dev python -m src.examples.async_example

run-flask: ## Run Flask integration example
	@echo "$(BLUE)Running Flask example...$(NC)"
	docker-compose run --rm pauth-dev python -m src.examples.flask_example

run-playground-example: ## Run playground example
	@echo "$(BLUE)Running playground example...$(NC)"
	docker-compose run --rm pauth-dev python -m src.examples.playground_example

##@ Code Quality

lint: ## Run code linting
	@echo "$(BLUE)Running linting...$(NC)"
	docker-compose run --rm pauth-dev poetry run flake8 src/

format: ## Format code with Black
	@echo "$(BLUE)Formatting code...$(NC)"
	docker-compose run --rm pauth-dev poetry run black src/

format-check: ## Check code formatting without changes
	@echo "$(BLUE)Checking code formatting...$(NC)"
	docker-compose run --rm pauth-dev poetry run black --check src/

isort: ## Sort imports
	@echo "$(BLUE)Sorting imports...$(NC)"
	docker-compose run --rm pauth-dev poetry run isort src/

isort-check: ## Check import sorting
	@echo "$(BLUE)Checking import sorting...$(NC)"
	docker-compose run --rm pauth-dev poetry run isort --check src/

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checking...$(NC)"
	docker-compose run --rm pauth-dev poetry run mypy src/

quality: format isort lint type-check ## Run all code quality checks

##@ Logs and Monitoring

logs: ## View logs from all services
	docker-compose logs -f

logs-dev: ## View development logs
	docker-compose logs -f pauth-dev

logs-prod: ## View production logs
	docker-compose logs -f pauth-prod

logs-playground: ## View playground logs
	docker-compose logs -f pauth-playground

ps: ## Show running containers
	docker-compose ps

stats: ## Show container resource usage
	docker stats

##@ Cleanup

stop: ## Stop all running containers
	@echo "$(BLUE)Stopping all containers...$(NC)"
	docker-compose down

stop-all: ## Stop and remove all containers
	@echo "$(BLUE)Stopping and removing all containers...$(NC)"
	docker-compose down --remove-orphans

clean: ## Remove containers and images
	@echo "$(RED)Removing containers and images...$(NC)"
	docker-compose down --rmi local

clean-volumes: ## Remove containers, images, and volumes
	@echo "$(RED)Removing containers, images, and volumes...$(NC)"
	docker-compose down -v --rmi local

clean-all: ## Remove everything (containers, images, volumes, cache)
	@echo "$(RED)Removing everything...$(NC)"
	docker-compose down -v --rmi all
	docker system prune -af --volumes

clean-cache: ## Clean Docker build cache
	@echo "$(RED)Cleaning build cache...$(NC)"
	docker builder prune -af

##@ Utilities

exec-dev: ## Execute command in dev container (usage: make exec-dev CMD="command")
	docker-compose exec pauth-dev $(CMD)

inspect: ## Inspect production container
	docker inspect pauth-prod

health: ## Check production container health
	@docker inspect --format='{{.State.Health.Status}}' pauth-prod || echo "$(YELLOW)Container not running$(NC)"

rebuild: clean-cache build ## Clean cache and rebuild all images

version: ## Show versions
	@echo "$(BLUE)Versions:$(NC)"
	@echo "Docker: $$(docker --version)"
	@echo "Docker Compose: $$(docker-compose --version)"
	@docker-compose run --rm pauth-dev python --version
	@docker-compose run --rm pauth-dev poetry --version

##@ CI/CD

ci-test: build-test test ## Run CI test pipeline
	@echo "$(GREEN)CI tests completed!$(NC)"

ci-build: build-prod ## Build production image for CI
	@echo "$(GREEN)CI build completed!$(NC)"

ci-full: ci-build ci-test ## Run full CI pipeline
	@echo "$(GREEN)Full CI pipeline completed!$(NC)"
