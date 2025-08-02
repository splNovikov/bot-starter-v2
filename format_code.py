#!/usr/bin/env python3
"""
Code formatting script using autoflake, isort, and ruff.

This script formats all Python files in the project using:
- autoflake for removing unused imports and variables
- isort for import sorting
- ruff for code formatting and linting

All formatters are compatible with Python 3.13.
"""

from pathlib import Path
import subprocess
import sys


def run_formatter(command, description):
    """Run a formatter and handle errors.

    Args:
        command (str): The command to run
        description (str): Human-readable description of what the command does

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"🔄 Running {description}...")
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def check_formatters_installed():
    """Check if autoflake, isort, and ruff are installed.

    Returns:
        bool: True if all are installed, False otherwise
    """
    try:
        subprocess.run(["autoflake", "--version"], check=True, capture_output=True)
        subprocess.run(["isort", "--version"], check=True, capture_output=True)
        subprocess.run(["ruff", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    """Run formatters with proper error handling."""
    print("🎨 Starting code formatting with autoflake, isort, and ruff...")
    print("=" * 60)

    # Check if formatters are installed
    if not check_formatters_installed():
        print("❌ autoflake, isort, or ruff not found!")
        print("Please install them with: pip install -r requirements.txt")
        return 1

    # Run autoflake first (remove unused imports and variables)
    autoflake_success = run_formatter(
        "autoflake --remove-all-unused-imports --remove-unused-variables --remove-duplicate-keys --in-place --recursive .",
        "Unused import removal (autoflake)",
    )

    # Run isort (import sorting)
    isort_success = run_formatter("isort .", "Import sorting (isort)")

    # Run ruff (code formatting and linting)
    ruff_success = run_formatter("ruff format .", "Code formatting (ruff)")

    print("=" * 60)

    if autoflake_success and isort_success and ruff_success:
        print("🎉 All formatting completed successfully!")
        print("💡 Your code is now clean, properly sorted, and formatted!")
        return 0
    else:
        print("💥 Some formatting failed!")
        print("🔧 Please check the errors above and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
