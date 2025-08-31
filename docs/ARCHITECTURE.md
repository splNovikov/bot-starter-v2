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
│   ├── sequence/                # Sequence engine
│   ├── middleware/              # Middleware components
│   └── utils/                   # Utilities
├── 🌐 infrastructure/           # Infrastructure Layer - external systems
│   ├── api/                     # HTTP client
│   ├── sequence/                # Sequence implementations
│   └── ui/                      # UI components
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