# Bot Starter v2 - Clean Architecture

## 🏗️ Architecture Overview

This project follows **Clean Architecture** and **SOLID** principles, ensuring clear separation of concerns across architectural layers.

## 📁 Project Structure

```
bot-starter-v2/
├── 🚀 main.py                    # Entry Point - application bootstrap
├── 🎯 application/               # Application Layer - business logic
│   ├── di_config/               # Dependency injection configuration
│   ├── handlers/                # Command handlers
│   ├── services/                # Business services (UserService)
│   └── types/                   # Data types (UserData)
├── 🏗️ core/                     # Core Layer - framework
│   ├── di/                      # Dependency injection system
│   ├── protocols/               # Interfaces and contracts
│   ├── sequence/                # Sequence engine (protocols only)
│   ├── middleware/              # Middleware components
│   └── utils/                   # Utilities
├── 🌐 infrastructure/           # Infrastructure Layer - external systems
│   ├── api/                     # HTTP client
│   ├── sequence/                # Sequence implementations
│   └── ui/                      # UI components
├── 🧪 tests/                    # Test Suite - organized by layers
│   ├── core/                    # Core layer tests
│   ├── application/             # Application layer tests
│   ├── infrastructure/          # Infrastructure layer tests
│   ├── integration/             # Integration tests
│   └── architecture/            # Architectural compliance tests
└── 📚 docs/                     # Documentation
    ├── architecture.puml        # PlantUML diagram
    └── ARCHITECTURE.md         # This file
```

## 🎯 Clean Architecture Principles

### Layers and Responsibilities:

1. **🚀 Entry Point (main.py)**
   - Application initialization
   - DI container setup  
   - Middleware configuration

2. **🎯 Application Layer**
   - Business logic implementation
   - Bot command handlers
   - Services (UserService)
   - DI configuration

3. **🏗️ Core Layer**
   - Protocols and interfaces
   - DI container system
   - Sequence engine
   - Middleware and utilities

4. **🌐 Infrastructure Layer**
   - HTTP client for external APIs
   - Sequence system implementations
   - UI components and renderers

### Dependency Rules:
- ✅ **Core** does not depend on **Application** or **Infrastructure**
- ✅ **Infrastructure** does not depend on **Application**
- ✅ Dependencies flow inward only

## 🔧 SOLID Principles

### ✅ Single Responsibility Principle (SRP)
- `SessionService` - session management only
- `QuestionService` - question handling only
- `ProgressService` - progress tracking only
- `CompletionService` - sequence completion only

### ✅ Open/Closed Principle (OCP)
- Protocol-based design
- Easy extension without modifying existing code

### ✅ Liskov Substitution Principle (LSP)
- `UserData` implements `UserEntity` protocol
- All implementations are interchangeable

### ✅ Interface Segregation Principle (ISP)
- Specialized protocols for each service type
- Clients depend only on interfaces they need

### ✅ Dependency Inversion Principle (DIP)
- All services depend on abstractions (protocols)
- DI container manages dependencies

## 🧪 Testing

### Test Structure by Architectural Layers:

```
tests/
├── 🏗️ core/                     # Core Layer Tests
│   └── test_di_container.py     # DI system, protocols, utilities
├── 🎯 application/              # Application Layer Tests  
│   └── test_user_service.py     # Business services and handlers
├── 🌐 infrastructure/           # Infrastructure Layer Tests
│   └── test_sequence_services.py # External services and implementations
├── 🔗 integration/              # Integration Tests
│   └── test_integration.py      # Cross-layer interaction tests
└── 🏛️ architecture/             # Architectural Tests
    ├── test_clean_architecture_compliance.py  # Architecture compliance
    └── test_architectural_refactoring.py     # Refactoring validation
```

### Available Commands:
```bash
make test             # Run all tests (simple runner)
make test-simple      # Simple tests without external dependencies
make test-unit        # Unit tests (requires pytest)
make test-integration # Integration tests (requires pytest)
make test-coverage    # Tests with coverage (requires pytest-cov)
```

### What is Tested:
- ✅ Import correctness across all layers
- ✅ DI container functionality  
- ✅ Protocol implementations
- ✅ Clean Architecture compliance
- ✅ Core module loading
- ✅ Sequence services
- ✅ Architectural refactoring compliance
- ✅ Global state anti-pattern elimination
- ✅ Service resolution patterns
- ✅ Layer boundary enforcement
- ✅ **Test layer structure organization**
- ✅ **Proper test-to-layer mapping**

## 📊 Diagrams

### PlantUML Diagram
```bash
# View architectural diagram
cat docs/architecture.puml
```

The diagram shows:
- Layer structure
- Dependency directions  
- SOLID principles application
- Components within each layer

## 🚀 Getting Started

```bash
# Environment setup
make setup

# Code formatting
make format

# Run tests
make test

# Start the bot
make run
```

## 📝 Key Architecture Features

### 1. Dependency Injection
- Centralized service registration
- Singleton and Transient lifetimes
- Automatic dependency resolution
- Graceful cleanup through Disposable protocol

### 2. Protocol-based Design
- Clear contracts between components
- Easy implementation swapping
- Type safety through Python typing

### 3. Sequence Engine Refactoring
- Breaking down monolithic `SequenceService`
- Specialized services
- Orchestrator pattern for coordination

### 4. Clean Architecture Compliance
- Strict adherence to dependency rules
- Automated architecture validation
- Clear layer separation

## 🎉 Refactoring Results

- ✅ **Reduced complexity**: Monolithic class split into specialized services
- ✅ **Improved testability**: DI and protocols simplify unit testing  
- ✅ **Enhanced extensibility**: Protocol-based design eases new feature addition
- ✅ **SOLID compliance**: SOLID and Clean Architecture strictly enforced
- ✅ **Automated validation**: Architectural violations detected automatically

## 🏗️ Recent Architectural Improvements (2025)

### **🧹 Deprecated Function Elimination (Latest)**
- **Problem**: Deprecated global functions (`get_sequence_service`, `set_sequence_service`) still in use
- **Solution**: Complete removal of deprecated functions and migration to pure DI pattern
- **Impact**: Clean codebase with zero deprecated APIs, consistent dependency resolution

### **🗂️ Test Layer Organization**
- **Problem**: All tests in single root folder, violating layered architecture principles
- **Solution**: Reorganized tests by architectural layers with clear separation of concerns
- **Impact**: Better test maintainability, easier navigation, reflects architectural structure

### **📋 Enhanced Architectural Testing**
- **Problem**: Limited architectural compliance validation
- **Solution**: Extended test suite with layer boundary checks, dependency direction validation
- **Impact**: Automated prevention of architectural violations, comprehensive compliance monitoring

### **Global State Anti-Pattern Elimination**
- **Problem**: Multiple services used global singleton instances, violating Dependency Inversion Principle
- **Solution**: All services now resolved through DI container using protocol interfaces
- **Impact**: Improved testability, better resource management, cleaner dependencies

### **Layer Boundary Enforcement**  
- **Problem**: `main.py` directly imported infrastructure components, violating Clean Architecture
- **Solution**: Infrastructure initialization moved to ApplicationFacade with proper abstraction layers
- **Impact**: True layer separation, infrastructure concerns properly isolated

### **Dependency Injection Consistency**
- **Problem**: Mixed patterns of global service access and DI container usage
- **Solution**: Standardized service resolution pattern: `container.resolve(ServiceProtocol)`
- **Impact**: Consistent dependency management, easier testing and mocking

### **Service Resolution Pattern Examples**

#### **Before (Anti-Pattern)**
```python
# ❌ Global service access - violates DIP
user_service = get_user_service()
if not user_service:
    logger.error("User service not available")
    return None
```

#### **After (Clean Architecture)**
```python
# ✅ Proper dependency injection
try:
    container = get_container()
    user_service = container.resolve(UserServiceProtocol)
except Exception as e:
    logger.error(f"Failed to resolve user service: {e}")
    return None
```

### **Infrastructure Management Through Facade**

#### **Before (Layer Violation)**
```python
# ❌ main.py directly importing infrastructure
from infrastructure.api import close_http_client
from infrastructure.sequence import initialize_sequences

# Direct infrastructure calls in main
initialize_sequences(sequence_definitions)
await close_http_client()
```

#### **After (Clean Architecture)**
```python
# ✅ Infrastructure through ApplicationFacade
app_facade = create_application_facade()

# Infrastructure managed by facade
app_facade.initialize_infrastructure()
await app_facade.cleanup_infrastructure()
```

### **Test Organization by Architectural Layer**

#### **Before (Flat Structure)**
```
tests/
├── test_di_container.py          # Mixed layer tests
├── test_user_service.py          
├── test_sequence_services.py     
├── test_integration.py           
└── test_architectural_refactoring.py
```

#### **After (Clean Architecture Aligned)**
```
tests/
├── core/                         # 🏗️ Tests core layer only
│   └── test_di_container.py      # DI container, protocols
├── application/                  # 🎯 Tests business logic
│   └── test_user_service.py      # Services, handlers  
├── infrastructure/               # 🌐 Tests external systems
│   └── test_sequence_services.py # API clients, implementations
├── integration/                  # 🔗 Tests layer interactions
│   └── test_integration.py       # Cross-layer scenarios
└── architecture/                 # 🏛️ Tests architectural rules
    ├── test_clean_architecture_compliance.py
    └── test_architectural_refactoring.py
```

### **Latest Architectural Validation**

#### **Comprehensive Compliance Checking**
```python
# ✅ Layer boundary validation
def check_layer_boundaries() -> Dict[str, List[str]]:
    """Validate no layer imports from forbidden layers."""
    
# ✅ Core abstraction validation  
def check_core_exports_only_abstractions() -> List[str]:
    """Ensure core exports only protocols and interfaces."""
    
# ✅ Global state detection
def check_no_global_state_in_core() -> List[str]:
    """Verify core layer contains no mutable global state."""
    
# ✅ Dependency injection validation
def check_dependency_injection_usage() -> List[str]:
    """Ensure services use DI instead of global access."""
```

## 🛡️ Security & Best Practices

### Security Measures:
- Input validation in all handlers
- Secure API communication
- Error handling without information leakage
- Proper access control through protocols

### Performance Optimization:
- Efficient sequence management
- Proper resource cleanup
- Optimized dependency resolution
- Memory-conscious session handling

### Scalability Considerations:
- Horizontal scaling through stateless design
- Vertical scaling via efficient resource usage
- Modular architecture for independent scaling
- Clean separation for microservice evolution