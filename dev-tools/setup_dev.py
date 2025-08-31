#!/usr/bin/env python3
"""
Development environment setup script.

This script automates the setup of the development environment by:
1. Creating a virtual environment (if needed)
2. Installing development dependencies
3. Verifying the installation

It provides clear feedback and handles errors gracefully.
"""

import os
from pathlib import Path
import subprocess
import sys


def run_command(command, description, cwd=None):
    """Run a command and handle errors.

    Args:
        command (str): The command to run
        description (str): Human-readable description of what the command does
        cwd (Path, optional): Working directory for the command

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"🔄 {description}...")
        subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd=cwd or Path(__file__).parent.parent,
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


def create_virtual_environment():
    """Create a virtual environment if it doesn't exist.

    Returns:
        bool: True if successful, False otherwise
    """
    venv_path = Path(__file__).parent.parent / "venv"

    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True

    return run_command("python3 -m venv venv", "Creating virtual environment")


def activate_venv_command():
    """Get the command to activate virtual environment.

    Returns:
        str: Command to activate virtual environment
    """
    if os.name == "nt":  # Windows
        return "venv\\Scripts\\activate"
    else:  # Unix/Linux/macOS
        return "source venv/bin/activate"


def check_tools_installed():
    """Check if all required tools are installed.

    Returns:
        bool: True if all tools are installed, False otherwise
    """
    tools = ["isort", "autoflake", "ruff"]
    missing_tools = []

    for tool in tools:
        try:
            # Try to run the tool from the virtual environment
            activate_cmd = activate_venv_command()
            check_cmd = f"{activate_cmd} && {tool} --version"
            subprocess.run(check_cmd, shell=True, check=True, capture_output=True)
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

    # Create virtual environment
    if not create_virtual_environment():
        print("💥 Failed to create virtual environment!")
        return 1

    # Check if tools are already installed
    if check_tools_installed():
        print("✅ All required tools are already installed!")
    else:
        print("⚠️  Some tools are missing. Attempting to install...")
        # Install dependencies in virtual environment
        activate_cmd = activate_venv_command()
        install_cmd = f"{activate_cmd} && python3 -m pip install -r requirements.txt"

        install_success = run_command(
            install_cmd, "Installing development dependencies"
        )

        if not install_success:
            print("⚠️  Failed to install dependencies.")
            print("💡 This might be due to network issues or package conflicts.")
            print("")
            print("🔧 Alternative solutions:")
            print("")
            print("Option 1: Install tools globally (Recommended)")
            print("   brew install pipx")
            print("   pipx install autoflake isort ruff")
            print('   export PATH="$HOME/.local/bin:$PATH"')
            print("")
            print("Option 2: Manual installation in venv")
            print(f"   {activate_cmd}")
            print("   python3 -m pip install ruff isort autoflake")
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
