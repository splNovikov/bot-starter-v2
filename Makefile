.PHONY: setup format check-format clean-imports install-dev help

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup            - Complete development environment setup"
	@echo "  make format           - Format all Python files with autoflake, isort, and ruff"
	@echo "  make check-format     - Check if files need formatting (without changes)"
	@echo "  make clean-imports    - Remove unused imports and variables only"
	@echo "  make install-dev      - Install development dependencies"
	@echo "  make run              - Run the bot"
	@echo "  make clean            - Clean up Python cache files"
	@echo "  make help             - Show this help message"

# Format all Python files
format:
	@echo "🎨 Formatting code..."
	@if [ -d "venv" ]; then \
		source venv/bin/activate && python3 format_code.py; \
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
	python3 setup_dev.py

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

# Clean up Python cache files
clean:
	@echo "🧹 Cleaning up cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
