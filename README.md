# Bot Starter v2 🤖

Clean Architecture Telegram Bot with Enhanced DI and Sequence Management

## ✨ Features

- **🏗️ Clean Architecture**: Proper layer separation following Clean Architecture principles
- **🔧 Dependency Injection**: Full DI container with protocol-based service resolution
- **📝 Sequence Framework**: Interactive conversation flows with state management
- **🌍 Localization**: Multi-language support with context-aware translations
- **🧪 Comprehensive Testing**: Architecture validation and unit tests
- **📊 Logging & Monitoring**: Structured logging with performance tracking

## 🚀 Quick Start

```bash
# Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure bot
cp config.py.example config.py
# Edit config.py with your bot token and API settings

# Run tests
python simple_test_runner.py

# Start bot
python main.py
```

## 🏗️ Architecture

### **Layer Structure**
```
bot-starter-v2/
├── 🚀 main.py                    # Entry Point
├── 🎯 application/               # Business Logic Layer
│   ├── facade/                   # Application Facade
│   ├── handlers/                 # Command & Message Handlers  
│   ├── services/                 # Business Services
│   └── types/                    # Domain Models
├── 🏗️ core/                     # Core Framework Layer
│   ├── di/                      # Dependency Injection
│   ├── protocols/               # Interfaces & Contracts
│   ├── sequence/                # Sequence Framework
│   └── middleware/              # Middleware Components
├── 🌐 infrastructure/           # Infrastructure Layer
│   ├── api/                     # HTTP Client
│   ├── sequence/                # Sequence Implementations
│   └── ui/                      # UI Components
└── 📚 docs/                     # Documentation
```

### **Dependency Flow**
```
Main → Application Facade → Core Protocols → Infrastructure
```

## 🔧 Dependency Injection

### **Service Registration**
```python
# Register services through protocols
container.register_singleton(HttpClientProtocol, HttpClient)
container.register_singleton(UserServiceProtocol, UserService)
```

### **Service Resolution**
```python
# Resolve services via DI container
try:
    container = get_container()
    user_service = container.resolve(UserServiceProtocol)
except Exception as e:
    logger.error(f"Failed to resolve service: {e}")
```

## 📝 Sequence Framework

Create interactive conversation flows:

```python
@sequence_handler("user_info")
async def handle_user_info_sequence(message: Message):
    # Sequence automatically manages state and flow
    sequence_service = container.resolve(SequenceServiceProtocol)
    await sequence_service.start_sequence(user_id, "user_info")
```

## 🧪 Testing

```bash
# Run all tests
python simple_test_runner.py

# Test specific components  
python -c "from tests.test_architectural_refactoring import *"
```

### **Test Coverage**
- ✅ Import correctness across layers
- ✅ DI container functionality
- ✅ Clean Architecture compliance
- ✅ Architectural refactoring validation
- ✅ Service resolution patterns
- ✅ Protocol implementations

## 📊 Recent Improvements (2025)

### **🛡️ Architectural Violations Fixed**
- **Global State Anti-Pattern Elimination**: Removed all global service instances
- **Layer Boundary Enforcement**: Infrastructure properly isolated through facades
- **Dependency Injection Consistency**: Standardized service resolution patterns

### **🎯 SOLID Principles Compliance**
- **Single Responsibility**: Each service has one clear purpose
- **Open/Closed**: Easy extension through protocol interfaces
- **Dependency Inversion**: All dependencies resolved through abstractions

### **🏗️ Clean Architecture Benefits**
- True layer separation with proper dependency direction
- Infrastructure concerns isolated from business logic  
- Easy testing through protocol-based design
- Scalable architecture supporting microservice evolution

## 🌍 Localization

Support for multiple languages with context-aware translations:

```python
# Context-aware translation
message = t("welcome.message", 
           user=user, 
           preferred_name=user_data.preferred_name)
```

## 📚 Documentation

- [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) - Detailed architecture documentation
- [`architecture.puml`](docs/architecture.puml) - PlantUML architecture diagram
- [Test Documentation](tests/) - Comprehensive test suite documentation

## 🛠️ Development

```bash
# Format code
python format_code.py

# Run development setup
python setup_dev.py

# Check architecture compliance
python simple_test_runner.py
```

## 📈 Performance & Scalability

- **Efficient Resource Management**: Proper service lifecycle management
- **Memory Optimization**: No global state, proper cleanup patterns
- **Horizontal Scaling**: Stateless design with external session storage
- **Monitoring**: Comprehensive logging and error tracking

## 🤝 Contributing

1. Follow Clean Architecture principles
2. Write tests for new features  
3. Update documentation
4. Ensure architectural compliance

## 📄 License

MIT License - see LICENSE file for details

---

Built with ❤️ following Clean Architecture and SOLID principles