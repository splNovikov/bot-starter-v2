# Black Compatibility Issue Resolution

## Issue
Black is currently disabled due to a compatibility issue with Click 8.2.2 and Python 3.13.

## Error Message
```
ImportError: cannot import name 'echo' from 'click'
```

## Solutions

### Option 1: Downgrade Click (Recommended)
```bash
pip install 'click<8.2.0'
```

### Option 2: Use a Different Python Version
If possible, use Python 3.11 or 3.12 instead of 3.13.

### Option 3: Wait for Black Update
This is a known issue that will be fixed in future Black releases.

## Pre-commit Compatibility Issue

### Problem
If you encounter this error with pre-commit:
```
ImportError: cannot import name 'sysconfig' from 'distlib.compat'
```

### Solution (Recommended)
Install tools globally using pipx:

```bash
# Install pipx if not already installed
brew install pipx

# Install required tools globally
pipx install autoflake isort pre-commit

# Add to PATH (add this to your shell profile)
export PATH="$HOME/.local/bin:$PATH"

# Install pre-commit hooks
pre-commit install
```

### Alternative Solution
If pipx doesn't work, you can use the virtual environment approach:
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pre-commit install
```

## Current Status
- ✅ autoflake (unused import removal) - Working
- ✅ isort (import sorting) - Working
- ✅ pre-commit hooks - Working (with global tools)
- ❌ Black (code formatting) - Temporarily disabled

## Manual Black Usage
Once the compatibility issue is resolved, you can:

1. Re-enable Black in `.pre-commit-config.yaml` by uncommenting the Black section
2. Run `pre-commit install` to reinstall hooks
3. Use `black .` to format code manually

## Alternative Formatting
For now, the project uses:
- `autoflake` for removing unused imports
- `isort` for sorting imports
- Manual formatting following PEP 8 guidelines

## Commands Available
```bash
# Remove unused imports only
make clean-imports

# Format imports and remove unused ones
make format

# Check formatting
make check-format

# Setup development environment
make setup
```

## Environment Setup
To ensure everything works properly:

1. **Add to your shell profile** (`~/.zshrc` or `~/.bashrc`):
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

2. **Restart your terminal** or run:
   ```bash
   source ~/.zshrc
   ```

3. **Test the setup**:
   ```bash
   autoflake --version
   isort --version
   pre-commit --version
   ```
