# 🔧 Core Framework Documentation

The core framework provides reusable infrastructure components for building type-safe, well-structured Telegram bots using aiogram v3.

## 📁 Core Architecture

```
core/
├── handlers/           # Handler registry system
│   ├── registry.py    # Central handler management
│   ├── decorators.py  # Registration decorators
│   ├── protocols.py   # Type-safe interfaces
│   └── types.py       # Type definitions and enums
├── middleware/         # Infrastructure middleware
│   └── logging_middleware.py
├── utils/             # Core utilities
│   └── logger.py      # Logging system
└── docs/              # Framework documentation
    ├── README.md      # This file
    ├── handlers.md    # Handler registry system
    ├── middleware.md  # Middleware documentation
    └── utils.md       # Utilities documentation
```

## 🎯 Core Principles

### 1. **Reusability**
The core framework is designed to be reused across multiple bot projects. Business logic is kept separate in the business layer.

### 2. **Type Safety** 
Strong typing with Python protocols ensures handlers conform to expected interfaces. Runtime validation prevents common errors.

### 3. **Metadata-Driven**
Rich metadata system enables auto-generated help, introspection, and statistics without manual maintenance.

### 4. **Clean Architecture**
Clear separation between framework (core) and application logic (business) with proper dependency direction.

## 🚀 Key Features

### **Handler Registry System**
- Type-safe handler registration using decorators
- Rich metadata for each handler (description, usage, examples)
- Automatic aiogram router integration
- Command aliasing and categorization
- Runtime statistics and performance monitoring

### **Protocol-Based Type Safety**
- Strict typing for different handler types
- Runtime validation of handler signatures
- Clear contracts for handler implementations
- IDE support with proper type hints

### **Infrastructure Middleware**
- Comprehensive logging with structured output
- Request/response tracking for debugging
- Error handling and monitoring
- Performance metrics collection

### **Core Utilities**
- Professional logging system with multiple levels
- Configuration management
- Common utilities for bot development

## 📊 Handler Categories

The framework supports organized handler categorization:

- **`CORE`**: Essential bot functionality (start, help)
- **`USER`**: User interaction features
- **`ADMIN`**: Administrative commands
- **`UTILITY`**: Helper and utility commands
- **`FUN`**: Entertainment features

## 🔍 Registry Introspection

The registry system provides powerful introspection capabilities:

```python
from core import get_registry

registry = get_registry()

# Get all registered handlers
handlers = registry.get_all_handlers()

# Get commands with aliases
commands = registry.get_commands()

# Generate help automatically
help_text = registry.generate_help_text()

# Get usage statistics
stats = registry.get_stats_summary()
```

## 📚 Detailed Documentation

- **[Handler System](handlers.md)** - Registry, decorators, types, and protocols
- **[Middleware](middleware.md)** - Infrastructure middleware components
- **[Utilities](utils.md)** - Logging and core utilities

## 🔄 Integration with Business Layer

The core framework is consumed by the business layer:

```python
# Business layer imports from core
from core.handlers.decorators import command
from core.handlers.types import HandlerCategory
from core.utils.logger import get_logger

# Core never imports from business
# This keeps the framework reusable
```

## 🎉 Getting Started

1. **Import Core Components**: Use decorators and types from core
2. **Create Handlers**: Use `@command`, `@text_handler`, etc.
3. **Add Metadata**: Provide rich descriptions and examples
4. **Initialize Registry**: Let the business layer handle initialization

The core framework handles all the infrastructure concerns, allowing you to focus on business logic in the business layer. 