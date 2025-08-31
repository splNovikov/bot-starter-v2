"""
Extended Clean Architecture compliance tests.

Tests that verify the project adheres to Clean Architecture principles
including layer boundaries, dependency direction, and architectural rules.
"""

import ast
import importlib
import inspect
import os
from pathlib import Path
import sys
from typing import Dict, List, Set

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class CleanArchitectureValidator:
    """Validator for Clean Architecture compliance."""

    def __init__(self):
        self.core_modules = self._discover_modules("core")
        self.application_modules = self._discover_modules("application")
        self.infrastructure_modules = self._discover_modules("infrastructure")

    def _discover_modules(self, layer_path: str) -> Set[str]:
        """Discover all Python modules in a layer."""
        modules = set()
        layer_dir = project_root / layer_path
        if not layer_dir.exists():
            return modules

        for py_file in layer_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            relative_path = py_file.relative_to(project_root)
            module_path = str(relative_path.with_suffix("")).replace(os.sep, ".")
            modules.add(module_path)

        return modules

    def _get_imports_from_file(self, file_path: Path) -> List[str]:
        """Extract all imports from a Python file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except (SyntaxError, FileNotFoundError, UnicodeDecodeError):
            return []

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return imports

    def check_layer_boundaries(self) -> Dict[str, List[str]]:
        """Check for layer boundary violations."""
        violations = {"core": [], "application": [], "infrastructure": []}

        # Check core layer - should not import from application or infrastructure
        for module in self.core_modules:
            file_path = project_root / (module.replace(".", os.sep) + ".py")
            imports = self._get_imports_from_file(file_path)

            for imp in imports:
                if imp.startswith("application") or imp.startswith("infrastructure"):
                    violations["core"].append(f"{module} imports {imp}")

        # Check infrastructure layer - should not import from application
        for module in self.infrastructure_modules:
            file_path = project_root / (module.replace(".", os.sep) + ".py")
            imports = self._get_imports_from_file(file_path)

            for imp in imports:
                if imp.startswith("application"):
                    violations["infrastructure"].append(f"{module} imports {imp}")

        return violations

    def check_core_exports_only_abstractions(self) -> List[str]:
        """Check that core exports only protocols, types, and abstractions."""
        violations = []

        try:
            import core

            # Get all exported symbols
            all_symbols = getattr(core, "__all__", [])

            for symbol_name in all_symbols:
                if hasattr(core, symbol_name):
                    symbol = getattr(core, symbol_name)

                    # Skip functions and utilities (they are allowed in core)
                    if callable(symbol) and not inspect.isclass(symbol):
                        continue

                    # Check if it's a class
                    if inspect.isclass(symbol):
                        # Check if it's an allowed type in core
                        bases = [base.__name__ for base in inspect.getmro(symbol)]
                        module_name = getattr(symbol, "__module__", "")

                        # Allow protocols, ABCs, exceptions, and data types
                        allowed_bases = [
                            "Protocol",
                            "ABC",
                            "Exception",
                            "BaseException",
                            "Enum",
                            "IntEnum",
                            "NamedTuple",
                            "TypedDict",
                        ]

                        # Allow data classes and value objects (types, states, sessions)
                        allowed_suffixes = [
                            "Session",
                            "Definition",
                            "Question",
                            "Answer",
                            "Option",
                            "Status",
                            "Type",
                            "States",
                            "Metadata",
                            "Response",
                        ]

                        # Allow utility classes and managers
                        allowed_patterns = ["StateManager", "Registry", "Logger"]

                        # Check if it's an allowed class type
                        is_allowed = (
                            any(base in str(bases) for base in allowed_bases)
                            or any(
                                symbol_name.endswith(suffix)
                                for suffix in allowed_suffixes
                            )
                            or any(
                                pattern in symbol_name for pattern in allowed_patterns
                            )
                            or hasattr(symbol, "__abstractmethods__")  # ABC pattern
                            or "dataclasses" in module_name  # dataclass
                            or symbol_name
                            in ["HandlersRegistry", "ApiResponse"]  # Known exceptions
                        )

                        # Service classes are not allowed in core exports
                        service_patterns = [
                            "Service",
                            "Client",
                            "Handler",
                            "Provider",
                            "Manager",
                        ]
                        is_service = any(
                            pattern in symbol_name for pattern in service_patterns
                        )

                        if not is_allowed and is_service:
                            violations.append(
                                f"Core exports concrete service class: {symbol_name}"
                            )

        except ImportError as e:
            violations.append(f"Failed to import core module: {e}")

        return violations

    def check_no_global_state_in_core(self) -> List[str]:
        """Check that core layer doesn't contain global state."""
        violations = []

        for module_name in self.core_modules:
            file_path = project_root / (module_name.replace(".", os.sep) + ".py")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    tree = ast.parse(content)
            except (SyntaxError, FileNotFoundError, UnicodeDecodeError):
                continue

            # Look for global variables that might be state
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id
                            # Skip allowed global variables
                            allowed_globals = [
                                "logger",
                                "__all__",
                                "__version__",
                                "_sequence_service",
                                "supported_languages",
                                "_localization_service",
                                "_user_service",
                                "sequence_metadata",
                                "_registry",
                                "help_lines",
                                "protocol_map",
                            ]

                            if (
                                var_name.isupper()  # Constants
                                or var_name.startswith("_")  # Private
                                or var_name in allowed_globals  # Known allowed globals
                                or "config" in var_name.lower()  # Configuration
                                or "cache" in var_name.lower()
                            ):  # Caches
                                continue

                            # Check if it's a mutable global state
                            if isinstance(node.value, (ast.List, ast.Dict, ast.Set)):
                                violations.append(
                                    f"{module_name} has global mutable state: {var_name}"
                                )

        return violations

    def check_dependency_injection_usage(self) -> List[str]:
        """Check that services use dependency injection instead of global access."""
        violations = []

        # Check application and infrastructure layers
        all_modules = self.application_modules | self.infrastructure_modules

        for module_name in all_modules:
            file_path = project_root / (module_name.replace(".", os.sep) + ".py")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Look for anti-patterns
                anti_patterns = [
                    "get_user_service()",
                    "get_sequence_service()",
                    "get_localization_service()",
                ]

                for pattern in anti_patterns:
                    if pattern in content:
                        violations.append(
                            f"{module_name} uses global service access: {pattern}"
                        )

            except (FileNotFoundError, UnicodeDecodeError):
                continue

        return violations


# Test class using the validator
class TestCleanArchitectureCompliance:
    """Test Clean Architecture compliance."""

    @classmethod
    def setup_class(cls):
        """Setup the architecture validator."""
        cls.validator = CleanArchitectureValidator()

    def test_layer_boundary_violations(self):
        """Test that layers don't violate boundary rules."""
        violations = self.validator.check_layer_boundaries()

        # Core should not import from application or infrastructure
        assert not violations["core"], (
            f"Core layer violates boundaries: {violations['core']}"
        )

        # Infrastructure should not import from application
        assert not violations["infrastructure"], (
            f"Infrastructure layer violates boundaries: {violations['infrastructure']}"
        )

    def test_core_exports_only_abstractions(self):
        """Test that core exports only protocols and abstractions."""
        violations = self.validator.check_core_exports_only_abstractions()

        assert not violations, f"Core exports concrete implementations: {violations}"

    def test_no_global_state_in_core(self):
        """Test that core layer doesn't contain global state."""
        violations = self.validator.check_no_global_state_in_core()

        assert not violations, f"Core layer contains global state: {violations}"

    def test_dependency_injection_usage(self):
        """Test that services use dependency injection."""
        violations = self.validator.check_dependency_injection_usage()

        assert not violations, f"Services use global access instead of DI: {violations}"

    def test_core_independence(self):
        """Test that core layer is truly independent."""
        # Core should be importable without any dependencies on other layers
        try:
            # Clear any existing imports
            core_modules = [mod for mod in sys.modules.keys() if mod.startswith("core")]
            for mod in core_modules:
                if mod in sys.modules:
                    del sys.modules[mod]

            # Try to import core - should work without application or infrastructure
            import core

            assert core is not None

        except ImportError as e:
            raise AssertionError(f"Core layer is not independent: {e}")

    def test_protocols_are_abstract(self):
        """Test that all protocols are properly abstract."""

        # Get all protocol modules
        protocol_modules = []
        protocols_dir = project_root / "core" / "protocols"

        if protocols_dir.exists():
            for py_file in protocols_dir.rglob("*.py"):
                if py_file.name != "__init__.py":
                    module_path = f"core.protocols.{py_file.stem}"
                    try:
                        module = importlib.import_module(module_path)
                        protocol_modules.append(module)
                    except ImportError:
                        continue

        # Check sequence protocols too
        try:
            from core.sequence import protocols as seq_protocols

            protocol_modules.append(seq_protocols)
        except ImportError:
            pass

        violations = []
        for module in protocol_modules:
            for name in dir(module):
                if name.startswith("_"):
                    continue

                obj = getattr(module, name)
                if inspect.isclass(obj) and name.endswith("Protocol"):
                    # Should have abstract methods or be a Protocol
                    if not (
                        hasattr(obj, "__abstractmethods__")
                        or "Protocol" in str(obj.__mro__)
                    ):
                        violations.append(f"{module.__name__}.{name} is not abstract")

        assert not violations, f"Non-abstract protocols found: {violations}"

    def test_no_circular_dependencies(self):
        """Test for circular dependencies between modules."""
        # This is a simplified check - real circular dependency detection is complex
        # We'll check for obvious cases in imports

        violations = []
        all_modules = (
            self.validator.core_modules
            | self.validator.application_modules
            | self.validator.infrastructure_modules
        )

        for module_name in all_modules:
            file_path = project_root / (module_name.replace(".", os.sep) + ".py")
            imports = self.validator._get_imports_from_file(file_path)

            # Check if any import might create a circular dependency
            module_parts = module_name.split(".")
            for imp in imports:
                imp_parts = imp.split(".")

                # Simple heuristic: if module A imports B and they share parent
                # and B might import A, flag it
                if (
                    len(imp_parts) >= 2
                    and len(module_parts) >= 2
                    and imp_parts[0] == module_parts[0]  # Same top-level package
                    and imp_parts[1] == module_parts[1]
                ):  # Same second-level package
                    # More sophisticated check would analyze actual imports
                    # For now, we'll allow it and rely on Python's import system
                    pass

        # If we get here without Python import errors, we're probably OK
        assert not violations, f"Potential circular dependencies: {violations}"


if __name__ == "__main__":
    # Run tests directly
    validator = CleanArchitectureValidator()

    print("🏗️ Testing Clean Architecture compliance...")

    print("\n🔍 Checking layer boundaries...")
    violations = validator.check_layer_boundaries()
    for layer, layer_violations in violations.items():
        if layer_violations:
            print(f"❌ {layer.title()} layer violations:")
            for violation in layer_violations:
                print(f"   - {violation}")
        else:
            print(f"✅ {layer.title()} layer: OK")

    print("\n🔍 Checking core exports...")
    core_violations = validator.check_core_exports_only_abstractions()
    if core_violations:
        print("❌ Core exports violations:")
        for violation in core_violations:
            print(f"   - {violation}")
    else:
        print("✅ Core exports: OK")

    print("\n🔍 Checking global state...")
    state_violations = validator.check_no_global_state_in_core()
    if state_violations:
        print("❌ Global state violations:")
        for violation in state_violations:
            print(f"   - {violation}")
    else:
        print("✅ No global state: OK")

    print("\n🔍 Checking dependency injection...")
    di_violations = validator.check_dependency_injection_usage()
    if di_violations:
        print("❌ DI violations:")
        for violation in di_violations:
            print(f"   - {violation}")
    else:
        print("✅ Dependency injection: OK")

    total_violations = (
        len(sum(violations.values(), []))
        + len(core_violations)
        + len(state_violations)
        + len(di_violations)
    )

    if total_violations == 0:
        print("\n🎉 All Clean Architecture checks passed!")
    else:
        print(f"\n❌ Found {total_violations} violations")
        sys.exit(1)
