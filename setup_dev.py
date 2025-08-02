#!/usr/bin/env python3
"""
Development environment setup script.

This script automates the setup of the development environment by:
1. Installing development dependencies (if needed)
2. Verifying the installation

It provides clear feedback and handles errors gracefully.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors.

    Args:
        command (str): The command to run
        description (str): Human-readable description of what the command does

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"🔄 {description}...")
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


def check_tools_installed():
    """Check if all required tools are installed.

    Returns:
        bool: True if all tools are installed, False otherwise
    """
    tools = ["black", "isort", "autoflake"]
    missing_tools = []
    
    for tool in tools:
        try:
            subprocess.run([tool, "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"❌ Missing tools: {', '.join(missing_tools)}")
        return False
    
    return True


def main():
    """Set up the development environment."""
    print("🚀 Setting up development environment...")
    print("=" * 50)

    # Check if tools are already installed
    if check_tools_installed():
        print("✅ All required tools are already installed!")
    else:
        print("⚠️  Some tools are missing. Attempting to install...")
        # Try to install dependencies, but don't fail if it doesn't work
        install_success = run_command(
            "pip install -r requirements.txt",
            "Installing development dependencies"
        )

        if not install_success:
            print("⚠️  Failed to install dependencies via pip.")
            print("💡 This might be due to Python 3.13 compatibility issues.")
            print("")
            print("🔧 Alternative solutions:")
            print("")
            print("Option 1: Install tools globally (Recommended)")
            print("   brew install pipx")
            print("   pipx install autoflake isort black")
            print("   export PATH=\"$HOME/.local/bin:$PATH\"")
            print("")
            print("Option 2: Manual installation")
            print("   pip install black isort autoflake")
            print("   Or try: python -m pip install -r requirements.txt")
            print("")
            print("Option 3: Use different Python version")
            print("   Consider using Python 3.11 or 3.12 instead of 3.13")
            print("")
            
            # Check again after the attempt
            if not check_tools_installed():
                print("💥 Critical tools are still missing!")
                print("🔧 Please try one of the alternative solutions above.")
                return 1

    print("=" * 50)
    print("🎉 Development environment setup completed successfully!")
    print("")
    print("📋 Available commands:")
    print("  make format           - Format all code")
    print("  make check-format     - Check formatting")
    print("  make clean-imports    - Remove unused imports")
    print("  make run              - Run the bot")
    print("  make help             - Show all commands")
    print("")
    print("💡 Manual formatting workflow:")
    print("   1. Run 'make clean-imports' to remove unused imports")
    print("   2. Run 'make format' to sort imports and format code")
    print("   3. Commit your changes")
    print("")
    print("📖 For troubleshooting, see: BLACK_COMPATIBILITY.md")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
