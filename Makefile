.PHONY: setup format check-format clean-imports install-dev help

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup            - Complete development environment setup"
	@echo "  make format           - Format all Python files with autoflake and isort"
	@echo "  make check-format     - Check if files need formatting (without changes)"
	@echo "  make clean-imports    - Remove unused imports and variables only"
	@echo "  make install-dev      - Install development dependencies"
	@echo "  make run              - Run the bot"
	@echo "  make clean            - Clean up Python cache files"
	@echo "  make help             - Show this help message"

# Format all Python files
format:
	@echo "🎨 Formatting code..."
	python3 format_code.py

# Check formatting without making changes
check-format:
	@echo "🔍 Checking code formatting..."
	black --check .
	isort --check-only --diff .
	autoflake --remove-all-unused-imports --remove-unused-variables --check .

# Remove unused imports and variables only
clean-imports:
	@echo "🧹 Removing unused imports and variables..."
	autoflake --remove-all-unused-imports --remove-unused-variables --remove-duplicate-keys --in-place --recursive .

# Complete development environment setup
setup:
	@echo "🚀 Setting up complete development environment..."
	python3 setup_dev.py

# Install development dependencies
install-dev:
	@echo "📦 Installing development dependencies..."
	pip install -r requirements.txt

# Run the bot
run:
	@echo "🤖 Starting the bot..."
	python3 main.py

# Clean up Python cache files
clean:
	@echo "🧹 Cleaning up cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
