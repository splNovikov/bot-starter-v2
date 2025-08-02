#!/usr/bin/env python3
"""
Code formatting script using autoflake and isort.

This script formats all Python files in the project using:
- autoflake for removing unused imports and variables
- isort for import sorting

Note: Black formatting is temporarily disabled due to compatibility issues.
It provides clear feedback and handles errors gracefully.
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
    """Check if autoflake and isort are installed.

    Returns:
        bool: True if both are installed, False otherwise
    """
    try:
        subprocess.run(["autoflake", "--version"], check=True, capture_output=True)
        subprocess.run(["isort", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    """Run formatters with proper error handling."""
    print("🎨 Starting code formatting with autoflake and isort...")
    print("=" * 50)
    print("⚠️  Note: Black formatting is temporarily disabled due to compatibility issues.")
    print("=" * 50)

    # Check if formatters are installed
    if not check_formatters_installed():
        print("❌ autoflake or isort not found!")
        print("Please install them with: pip install autoflake isort")
        return 1

    # Run autoflake first (remove unused imports and variables)
    autoflake_success = run_formatter(
        "autoflake --remove-all-unused-imports --remove-unused-variables --remove-duplicate-keys --in-place --recursive .",
        "Unused import removal (autoflake)"
    )

    # Run isort (import sorting)
    isort_success = run_formatter("isort .", "Import sorting (isort)")

    print("=" * 50)

    if autoflake_success and isort_success:
        print("🎉 Import cleaning and sorting completed successfully!")
        print("💡 Your imports are now clean and properly sorted!")
        print("")
        print("🔧 To enable Black formatting, please fix the Click compatibility issue:")
        print("   pip install 'click<8.2.0'")
        print("   Or use: black --version to test if it works")
        return 0
    else:
        print("💥 Some formatting failed!")
        print("🔧 Please check the errors above and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
