#!/usr/bin/env python3
"""
Code formatting script using Black and isort.

This script formats all Python files in the project using Black for code formatting
and isort for import sorting. It provides clear feedback and handles errors gracefully.
"""

import subprocess
import sys
from pathlib import Path


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
    """Check if Black and isort are installed.

    Returns:
        bool: True if both are installed, False otherwise
    """
    try:
        subprocess.run(["black", "--version"], check=True, capture_output=True)
        subprocess.run(["isort", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    """Run both formatters with proper error handling."""
    print("🎨 Starting code formatting with Black and isort...")
    print("=" * 50)

    # Check if formatters are installed
    if not check_formatters_installed():
        print("❌ Black or isort not found!")
        print("Please install them with: pip install black isort")
        return 1

    # Run isort first (import sorting)
    isort_success = run_formatter("isort .", "Import sorting (isort)")

    # Run Black (code formatting)
    black_success = run_formatter("black .", "Code formatting (Black)")

    print("=" * 50)

    if isort_success and black_success:
        print("🎉 All formatting completed successfully!")
        print("💡 Your code is now properly formatted and ready for commit!")
        return 0
    else:
        print("💥 Some formatting failed!")
        print("🔧 Please check the errors above and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
