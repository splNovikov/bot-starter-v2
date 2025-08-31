"""
Tests for DI container functionality.

Comprehensive test coverage for dependency injection container including
registration, resolution, and lifecycle management.
"""

from typing import Protocol

import pytest

from core.di.protocols import Disposable, Injectable


class TestProtocol(Protocol):
    """Test protocol for DI testing."""

    def test_method(self) -> str:
        """Test method."""
        ...


class TestService(TestProtocol, Injectable):
    """Test service implementation."""

    def test_method(self) -> str:
        return "test_result"


class TestServiceWithDependency(Injectable):
    """Test service with dependency injection."""

    def __init__(self, dependency: TestProtocol):
        self.dependency = dependency

    def get_dependency_result(self) -> str:
        return self.dependency.test_method()


class DisposableService(Injectable, Disposable):
    """Test service that implements Disposable."""

    def __init__(self):
        self.disposed = False

    async def dispose(self):
        self.disposed = True


class TestDIContainer:
    """Test cases for DI container."""

    def test_register_singleton(self, clean_container):
        """Test singleton registration."""
        container = clean_container

        # Register service
        container.register_singleton(TestProtocol, TestService)

        # Should be registered
        assert container.is_registered(TestProtocol)

    def test_register_transient(self, clean_container):
        """Test transient registration."""
        container = clean_container

        # Register service as transient
        container.register_transient(TestProtocol, TestService)

        # Should be registered
        assert container.is_registered(TestProtocol)

    def test_register_instance(self, clean_container):
        """Test instance registration."""
        container = clean_container
        service_instance = TestService()

        # Register instance
        container.register_instance(TestProtocol, service_instance)

        # Should be registered
        assert container.is_registered(TestProtocol)

        # Should return the same instance
        resolved = container.resolve(TestProtocol)
        assert resolved is service_instance

    def test_register_factory(self, clean_container):
        """Test factory registration."""
        container = clean_container

        def test_factory():
            return TestService()

        # Register factory
        container.register_factory(TestProtocol, test_factory)

        # Should be registered
        assert container.is_registered(TestProtocol)

    def test_resolve_singleton(self, clean_container):
        """Test singleton resolution."""
        container = clean_container

        # Register and resolve
        container.register_singleton(TestProtocol, TestService)
        service1 = container.resolve(TestProtocol)
        service2 = container.resolve(TestProtocol)

        # Should be the same instance (singleton)
        assert service1 is service2
        assert isinstance(service1, TestService)

    def test_resolve_transient(self, clean_container):
        """Test transient resolution."""
        container = clean_container

        # Register as transient
        container.register_transient(TestProtocol, TestService)
        service1 = container.resolve(TestProtocol)
        service2 = container.resolve(TestProtocol)

        # Should be different instances
        assert service1 is not service2
        assert isinstance(service1, TestService)
        assert isinstance(service2, TestService)

    def test_resolve_with_dependency_injection(self, clean_container):
        """Test dependency injection during resolution."""
        container = clean_container

        # Register dependencies
        container.register_singleton(TestProtocol, TestService)
        container.register_singleton(
            TestServiceWithDependency, TestServiceWithDependency
        )

        # Resolve service with dependency
        service = container.resolve(TestServiceWithDependency)

        # Should have dependency injected
        assert hasattr(service, "dependency")
        assert isinstance(service.dependency, TestService)
        assert service.get_dependency_result() == "test_result"

    def test_resolve_unregistered_service(self, clean_container):
        """Test resolving unregistered service raises error."""
        container = clean_container

        with pytest.raises(ValueError, match="Service .* is not registered"):
            container.resolve(TestProtocol)

    def test_factory_resolution(self, clean_container):
        """Test factory-based resolution."""
        container = clean_container
        call_count = 0

        def test_factory():
            nonlocal call_count
            call_count += 1
            return TestService()

        # Register factory
        container.register_factory(TestProtocol, test_factory)

        # First resolution should call factory
        service1 = container.resolve(TestProtocol)
        assert call_count == 1
        assert isinstance(service1, TestService)

        # Second resolution should return same instance (cached as singleton)
        service2 = container.resolve(TestProtocol)
        assert call_count == 1  # Factory not called again
        assert service1 is service2

    @pytest.mark.asyncio
    async def test_dispose_cleans_up_disposable_services(self, clean_container):
        """Test that dispose() calls dispose() on Disposable services."""
        container = clean_container

        # Register disposable service
        container.register_singleton(DisposableService, DisposableService)

        # Resolve to create instance
        service = container.resolve(DisposableService)
        assert not service.disposed

        # Dispose container
        await container.dispose()

        # Service should be disposed
        assert service.disposed

    def test_is_registered(self, clean_container):
        """Test is_registered method."""
        container = clean_container

        # Should not be registered initially
        assert not container.is_registered(TestProtocol)

        # Register service
        container.register_singleton(TestProtocol, TestService)

        # Should be registered now
        assert container.is_registered(TestProtocol)


class TestDIContainerEdgeCases:
    """Test edge cases and error conditions."""

    def test_resolve_with_missing_dependency_type_hint(self, clean_container):
        """Test resolving service with missing type hints."""
        container = clean_container

        class ServiceWithoutTypeHints:
            def __init__(self, missing_param):
                self.missing_param = missing_param

        container.register_singleton(ServiceWithoutTypeHints, ServiceWithoutTypeHints)

        # Should create instance without injecting missing dependency
        service = container.resolve(ServiceWithoutTypeHints)
        assert isinstance(service, ServiceWithoutTypeHints)

    def test_resolve_with_default_parameter(self, clean_container):
        """Test resolving service with default parameters."""
        container = clean_container

        class ServiceWithDefaults:
            def __init__(self, required: TestProtocol, optional: str = "default"):
                self.required = required
                self.optional = optional

        # Register dependencies
        container.register_singleton(TestProtocol, TestService)
        container.register_singleton(ServiceWithDefaults, ServiceWithDefaults)

        # Should resolve with dependency injected and default used
        service = container.resolve(ServiceWithDefaults)
        assert isinstance(service.required, TestService)
        assert service.optional == "default"
