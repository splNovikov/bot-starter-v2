#!/usr/bin/env python3
"""
Simple test runner without external dependencies.
Runs basic tests to verify the system functionality.
"""

from pathlib import Path
import sys
import traceback
from typing import Callable, List, Tuple

# Add project root to Python path to allow imports from dev-tools/ subdirectory
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SimpleTestRunner:
    """Simple test runner for basic functionality testing."""

    def __init__(self):
        self.tests: List[Tuple[str, Callable]] = []
        self.passed = 0
        self.failed = 0

    def test(self, name: str):
        """Decorator to register test functions."""

        def decorator(func: Callable) -> Callable:
            self.tests.append((name, func))
            return func

        return decorator

    def run_all(self) -> bool:
        """Run all registered tests."""
        print("🧪 Running simple tests...\n")

        for name, test_func in self.tests:
            try:
                print(f"🔍 {name}... ", end="")
                test_func()
                print("✅ PASSED")
                self.passed += 1
            except Exception as e:
                print(f"❌ FAILED: {e}")
                print(f"   {traceback.format_exc().splitlines()[-1]}")
                self.failed += 1

        print(f"\n📊 Results: {self.passed} passed, {self.failed} failed")

        if self.failed > 0:
            print("❌ Some tests failed!")
            return False
        else:
            print("🎉 All tests passed!")
            return True


# Initialize test runner
runner = SimpleTestRunner()


@runner.test("Core imports")
def test_core_imports():
    """Test that core modules import correctly."""
    from core.di import DIContainer
    from core.protocols.entities import UserEntity
    from core.protocols.services import HttpClientProtocol, UserServiceProtocol

    assert DIContainer is not None
    assert HttpClientProtocol is not None
    assert UserServiceProtocol is not None
    assert UserEntity is not None


@runner.test("Application imports")
def test_application_imports():
    """Test that application modules import correctly."""
    from application.di_config import get_basic_container
    from application.services.user_service import UserService
    from application.types import UserData

    assert get_basic_container is not None
    assert UserService is not None
    assert UserData is not None


@runner.test("Infrastructure imports")
def test_infrastructure_imports():
    """Test that infrastructure modules import correctly."""
    from infrastructure.api.client import HttpClient

    assert HttpClient is not None


@runner.test("DI Container functionality")
def test_di_container_functionality():
    """Test that DI container works."""
    from application.di_config import get_basic_container
    from core.protocols.services import HttpClientProtocol, UserServiceProtocol

    container = get_basic_container()
    assert container is not None

    # Test service resolution
    http_client = container.resolve(HttpClientProtocol)
    user_service = container.resolve(UserServiceProtocol)

    assert http_client is not None
    assert user_service is not None

    # Test that services are singletons
    http_client2 = container.resolve(HttpClientProtocol)
    assert http_client is http_client2


@runner.test("Protocol implementation")
def test_protocol_implementation():
    """Test that services implement their protocols correctly."""
    from application.services.user_service import UserService
    from infrastructure.api.client import HttpClient

    # Test that classes exist and can be instantiated
    user_service = UserService(None)  # type: ignore
    http_client = HttpClient()

    # Test that they have expected methods (duck typing)
    assert hasattr(user_service, "get_user")
    assert hasattr(user_service, "create_user")
    assert hasattr(user_service, "update_user")
    assert hasattr(http_client, "get")
    assert hasattr(http_client, "post")
    assert hasattr(http_client, "close")


@runner.test("Clean Architecture compliance")
def test_clean_architecture_compliance():
    """Test that Clean Architecture principles are followed."""
    import subprocess

    # Check that Core doesn't import from Application
    result = subprocess.run(
        ["grep", "-r", "--exclude-dir=__pycache__", "from application", "core/"],
        capture_output=True,
        text=True,
    )
    core_to_app_violations = [
        line
        for line in result.stdout.split("\n")
        if line
        and "# comment" not in line
        and "implementation details" not in line
        and ".pyc" not in line
    ]
    assert len(core_to_app_violations) == 0, (
        f"Core imports from Application: {core_to_app_violations}"
    )

    # Check that Core doesn't import from Infrastructure
    result = subprocess.run(
        ["grep", "-r", "--exclude-dir=__pycache__", "from infrastructure", "core/"],
        capture_output=True,
        text=True,
    )
    core_to_infra_violations = [
        line
        for line in result.stdout.split("\n")
        if line and "# comment" not in line and ".pyc" not in line
    ]
    assert len(core_to_infra_violations) == 0, (
        f"Core imports from Infrastructure: {core_to_infra_violations}"
    )

    # Check that Infrastructure doesn't import from Application
    result = subprocess.run(
        [
            "grep",
            "-r",
            "--exclude-dir=__pycache__",
            "from application",
            "infrastructure/",
        ],
        capture_output=True,
        text=True,
    )
    infra_to_app_violations = [
        line
        for line in result.stdout.split("\n")
        if line and "# comment" not in line and ".pyc" not in line
    ]
    assert len(infra_to_app_violations) == 0, (
        f"Infrastructure imports from Application: {infra_to_app_violations}"
    )


@runner.test("Main module loading")
def test_main_module_loading():
    """Test that main module can be imported without errors."""
    import main

    assert main is not None

    # Test that lifespan context exists
    assert hasattr(main, "lifespan_context")

    # Test that main function exists (entry point)
    assert hasattr(main, "main")


@runner.test("Sequence services")
def test_sequence_services():
    """Test that sequence services can be imported and instantiated."""
    from infrastructure.sequence.services import (
        SequenceCompletionService,
        SequenceOrchestrator,
        SequenceProgressService,
        SequenceQuestionService,
        SequenceSessionService,
    )

    assert SequenceSessionService is not None
    assert SequenceQuestionService is not None
    assert SequenceProgressService is not None
    assert SequenceCompletionService is not None
    assert SequenceOrchestrator is not None


@runner.test("Architectural refactoring")
def test_architectural_refactoring():
    """Test architectural refactoring changes."""
    # Test 1: Global state elimination
    from application.services import user_service

    assert not hasattr(user_service, "get_user_service"), (
        "get_user_service should be removed"
    )
    assert not hasattr(user_service, "set_user_service"), (
        "set_user_service should be removed"
    )

    # Test 2: DI container functionality
    from application.services.user_service import UserService
    from core.di.container import DIContainer
    from core.protocols.services import HttpClientProtocol, UserServiceProtocol
    from infrastructure.api.client import HttpClient

    container = DIContainer()
    container.register_singleton(HttpClientProtocol, HttpClient)
    container.register_singleton(UserServiceProtocol, UserService)

    http_client = container.resolve(HttpClientProtocol)
    user_service = container.resolve(UserServiceProtocol)

    assert isinstance(http_client, HttpClient)
    assert isinstance(user_service, UserService)

    # Test 3: ApplicationFacade infrastructure methods
    from application.facade.application_facade import ApplicationFacade

    facade = ApplicationFacade()

    assert hasattr(facade, "initialize_infrastructure")
    assert hasattr(facade, "cleanup_infrastructure")
    assert callable(facade.initialize_infrastructure)
    assert callable(facade.cleanup_infrastructure)


@runner.test("Test layer structure")
def test_layer_structure():
    """Test that tests are properly organized by architectural layers."""
    from pathlib import Path

    tests_dir = Path(__file__).parent.parent / "tests"

    # Check that layer directories exist
    assert (tests_dir / "core").is_dir(), "tests/core directory should exist"
    assert (tests_dir / "application").is_dir(), (
        "tests/application directory should exist"
    )
    assert (tests_dir / "infrastructure").is_dir(), (
        "tests/infrastructure directory should exist"
    )
    assert (tests_dir / "integration").is_dir(), (
        "tests/integration directory should exist"
    )
    assert (tests_dir / "architecture").is_dir(), (
        "tests/architecture directory should exist"
    )

    # Check specific test files are in correct layers
    assert (tests_dir / "core" / "test_di_container.py").exists(), (
        "DI container tests should be in core layer"
    )
    assert (tests_dir / "application" / "test_user_service.py").exists(), (
        "User service tests should be in application layer"
    )
    assert (tests_dir / "infrastructure" / "test_sequence_services.py").exists(), (
        "Sequence services tests should be in infrastructure layer"
    )
    assert (tests_dir / "integration" / "test_integration.py").exists(), (
        "Integration tests should be in integration layer"
    )
    assert (
        tests_dir / "architecture" / "test_clean_architecture_compliance.py"
    ).exists(), "Architectural tests should be in architecture layer"


@runner.test("Layer tests content structure")
def test_layer_tests_content_structure():
    """Test that test files contain expected content structure."""
    from pathlib import Path

    tests_dir = Path(__file__).parent.parent / "tests"

    # Check core layer test has DI container classes
    core_test = tests_dir / "core" / "test_di_container.py"
    core_content = core_test.read_text()
    assert "TestDIContainer" in core_content, (
        "Core tests should contain TestDIContainer"
    )
    assert "DIContainer" in core_content, "Core tests should test DIContainer"

    # Check application layer test has UserService classes
    app_test = tests_dir / "application" / "test_user_service.py"
    app_content = app_test.read_text()
    assert "TestUserService" in app_content, (
        "Application tests should contain TestUserService"
    )
    assert "UserService" in app_content, "Application tests should test UserService"

    # Check infrastructure layer test has sequence service classes
    infra_test = tests_dir / "infrastructure" / "test_sequence_services.py"
    infra_content = infra_test.read_text()
    assert "TestSequence" in infra_content, (
        "Infrastructure tests should contain TestSequence classes"
    )
    assert "infrastructure.sequence" in infra_content, (
        "Infrastructure tests should test sequence services from infrastructure layer"
    )

    # Check architecture test has compliance checks
    arch_test = tests_dir / "architecture" / "test_clean_architecture_compliance.py"
    arch_content = arch_test.read_text()
    assert "CleanArchitectureValidator" in arch_content, (
        "Architecture tests should contain CleanArchitectureValidator"
    )
    assert "layer_boundaries" in arch_content, (
        "Architecture tests should check layer boundaries"
    )


def main():
    """Run all tests."""
    success = runner.run_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
