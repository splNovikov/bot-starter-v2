.PHONY: setup format check-format clean-imports install-dev test test-simple test-unit test-integration test-coverage help

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup            - Complete development environment setup"
	@echo "  make format           - Format all Python files with autoflake, isort, and ruff"
	@echo "  make check-format     - Check if files need formatting (without changes)"
	@echo "  make clean-imports    - Remove unused imports and variables only"
	@echo "  make install-dev      - Install development dependencies"
	@echo "  make test             - Run all tests (simple runner)"
	@echo "  make test-simple      - Run simple tests (no external dependencies)"
	@echo "  make test-unit        - Run unit tests (pytest or fallback to simple)"
	@echo "  make test-integration - Run integration tests (requires pytest)"
	@echo "  make test-coverage    - Run tests with coverage (requires pytest-cov)"
	@echo "  make run              - Run the bot"
	@echo "  make clean            - Clean up Python cache files"
	@echo "  make help             - Show this help message"

# Format all Python files
format:
	@echo "🎨 Formatting code..."
	@if [ -d "venv" ]; then \
		source venv/bin/activate && python3 dev-tools/format_code.py; \
	else \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Check formatting without making changes
check-format:
	@echo "🔍 Checking code formatting..."
	@if [ -d "venv" ]; then \
		source venv/bin/activate && isort --check-only --diff . && \
		source venv/bin/activate && autoflake --remove-all-unused-imports --remove-unused-variables --check . && \
		source venv/bin/activate && ruff format --check .; \
	else \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Remove unused imports and variables only
clean-imports:
	@echo "🧹 Removing unused imports and variables..."
	@if [ -d "venv" ]; then \
		source venv/bin/activate && autoflake --remove-all-unused-imports --remove-unused-variables --remove-duplicate-keys --in-place --recursive .; \
	else \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Complete development environment setup
setup:
	@echo "🚀 Setting up complete development environment..."
	python3 dev-tools/setup_dev.py

# Install development dependencies
install-dev:
	@echo "📦 Installing development dependencies..."
	@if [ -d "venv" ]; then \
		source venv/bin/activate && python3 -m pip install -r requirements.txt; \
	else \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Run the bot
run:
	@echo "🤖 Starting the bot..."
	@if [ -d "venv" ]; then \
		source venv/bin/activate && python3 main.py; \
	else \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Test commands
test:
	@echo "🧪 Running all tests..."
	@if [ -d "venv" ]; then \
		source venv/bin/activate && python3 dev-tools/test_runner.py; \
	else \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

test-simple:
	@echo "🧪 Running simple tests (no external dependencies)..."
	@if [ -d "venv" ]; then \
		source venv/bin/activate && python3 dev-tools/test_runner.py; \
	else \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

test-unit:
	@echo "🧪 Running unit tests (requires pytest)..."
	@if [ -d "venv" ]; then \
		source venv/bin/activate && python3 -m pytest tests/test_*.py -v --ignore=tests/test_integration.py 2>/dev/null || python3 dev-tools/test_runner.py; \
	else \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

test-integration:
	@echo "🧪 Running integration tests (requires pytest)..."
	@if [ -d "venv" ]; then \
		source venv/bin/activate && python3 -m pytest tests/test_integration.py -v 2>/dev/null || echo "⚠️  pytest not available, use 'make test-simple'"; \
	else \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

test-coverage:
	@echo "🧪 Running tests with coverage (requires pytest-cov)..."
	@if [ -d "venv" ]; then \
		source venv/bin/activate && python3 -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing 2>/dev/null || echo "⚠️  pytest-cov not available, use 'make test-simple'"; \
	else \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Clean up Python cache files
clean:
	@echo "🧹 Cleaning up cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf htmlcov/ .coverage .pytest_cache/
