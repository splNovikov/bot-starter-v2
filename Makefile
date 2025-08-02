.PHONY: format check-format install-dev help

# Default target
help:
	@echo "Available commands:"
	@echo "  make format        - Format all Python files with Black and isort"
	@echo "  make check-format  - Check if files need formatting (without changes)"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make help          - Show this help message"

# Format all Python files
format:
	@echo "🎨 Formatting code..."
	python format_code.py

# Check formatting without making changes
check-format:
	@echo "🔍 Checking code formatting..."
	black --check .
	isort --check-only --diff .

# Install development dependencies
install-dev:
	@echo "📦 Installing development dependencies..."
	pip install -r requirements.txt

# Run the bot
run:
	@echo "🤖 Starting the bot..."
	python main.py

# Clean up Python cache files
clean:
	@echo "🧹 Cleaning up cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true 