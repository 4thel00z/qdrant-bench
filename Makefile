.PHONY: all install test lint format clean check help

# Colors
COLOR_RESET = \033[0m
COLOR_CYAN = \033[36m
COLOR_GREEN = \033[32m
COLOR_YELLOW = \033[33m

all: install lint test ## Install dependencies, run linting and tests

install: ## Sync dependencies with uv
	uv sync

test: ## Run tests using pytest
	uv run pytest

lint: ## Run linting and type checking
	uv run ruff check src tests
	uv run pyright src

format: ## Format code using ruff
	uv run ruff format src tests
	uv run ruff check --fix src tests

check: lint test ## Run all checks (lint + test)

clean: ## Clean up cache and temporary files
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf __pycache__
	rm -rf src/**/__pycache__
	rm -rf tests/**/__pycache__

help: ## Show this help message
	@cat banner.txt
	@echo ""
	@echo "$(COLOR_YELLOW)Usage:$(COLOR_RESET)"
	@echo "  make $(COLOR_GREEN)<target>$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_YELLOW)Targets:$(COLOR_RESET)"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_CYAN)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'
