# 🎯 Business Logic Documentation

The business layer contains application-specific logic, handlers, and services that implement the bot's functionality using the core framework.

## 📁 Business Architecture

```
business/
├── handlers/           # Application-specific handlers
│   ├── user_handlers.py        # Basic user interaction handlers
│   └── questionnaire_handlers.py # Questionnaire flow handlers
├── services/           # Business logic services
│   ├── greeting.py             # Greeting business logic
│   ├── help_service.py         # Help system
│   ├── localization.py         # Multi-language support
│   ├── questionnaire_service.py # Questionnaire orchestration
│   ├── session_manager.py      # Session management
│   ├── question_provider.py    # Question logic
│   ├── api_client.py          # External API communication
│   └── interfaces.py          # Service protocols/interfaces
├── states/             # FSM state definitions
│   └── questionnaire_states.py # Questionnaire conversation states
└── docs/              # Business layer documentation
    ├── README.md      # This file
    ├── handlers.md    # How to add handlers
    ├── services.md    # How to create services
    └── examples.md    # Practical examples
```

## 🎯 Core Principles

### 1. **Clean Architecture**
The business layer depends on the core framework but never the reverse. This keeps the core reusable and the business logic focused.

### 2. **SOLID Principles**
- **Single Responsibility**: Each service has one clear purpose
- **Open/Closed**: Services are extensible without modification
- **Liskov Substitution**: Protocol-based interfaces ensure substitutability
- **Interface Segregation**: Small, focused service interfaces
- **Dependency Inversion**: Services depend on interfaces, not concrete classes

### 3. **Separation of Concerns**
- **Handlers**: Thin message processors that handle user interactions
- **Services**: Business logic and external integrations
- **States**: FSM definitions for conversation flows
- **Interfaces**: Protocols defining service contracts

### 4. **Domain-Driven Design**
Business logic is organized around domains (greeting, questionnaire, user management, etc.) rather than technical concerns.

### 5. **Testability**
All business logic is designed to be easily testable in isolation through dependency injection and interface-based design.

## 🚀 Key Features

### **Handler-Service Architecture**
- Handlers process messages and delegate to services
- Services contain reusable business logic coordinated through interfaces
- Clean separation enables easy testing and maintenance

### **FSM-Based Conversations**
- Complex multi-step interactions use Finite State Machines
- States are clearly defined and managed
- Conversation context is properly maintained

### **Dependency Injection**
- Services use interfaces for loose coupling
- Easy to mock dependencies for testing
- Configuration is injected, not hardcoded

### **API Integration**
- External services integrated through protocol-based clients
- Resilient error handling with graceful degradation
- Configurable endpoints and timeouts

### **Session Management**
- Stateful conversations properly managed
- Session lifecycle clearly defined
- Memory-efficient session storage

## 📊 Service Architecture

### **Orchestrating Services**
Services that coordinate multiple specialized services:
- `QuestionnaireService` - Orchestrates the complete questionnaire flow

### **Specialized Services**
Services with single, focused responsibilities:
- `SessionManager` - Session lifecycle management
- `QuestionProvider` - Question logic and sequencing
- `ApiClient` - HTTP communication with external APIs
- `LocalizationService` - Multi-language text management

### **Interface-Driven Design**
All services implement protocols for:
- **Testability** - Easy mocking and unit testing
- **Flexibility** - Easy to swap implementations
- **Type Safety** - Runtime validation of service contracts

## 🎮 Current Features

### **Basic Interactions**
- `/start` - Welcome new users with localized greeting
- `/help` - Show available commands with descriptions
- `/greet` - Send personalized greeting message
- `/language` - Change user language preference

### **Questionnaire System**
- `/questionnaire` - Interactive multi-question survey
  - 3 base questions with conditional 4th question
  - Progress tracking through conversation
  - Answer summaries before completion
  - API integration for data persistence
- `/gender` - Standalone gender collection
  - Simple question with answer summary
  - Direct API submission
- `/cancel` - Cancel active questionnaire session

### **Multi-Language Support**
- Automatic language detection from Telegram locale
- User preference override with `/language` command
- Full localization for English, Spanish, and Russian
- Fallback handling for missing translations

### **Session Management**
- FSM-based conversation state management  
- Session lifecycle with proper cleanup
- Memory-efficient session storage
- Session persistence across bot restarts (configurable)

## 🔧 Configuration

The business layer uses environment-based configuration:

```bash
# API Configuration
API_BASE_URL=https://your-api-endpoint.com
API_TIMEOUT=30

# Localization
DEFAULT_LANGUAGE=en
SUPPORTED_LANGUAGES=en,es,ru
```

## 🧪 Testing Strategy

### **Unit Testing**
- Mock service dependencies using interfaces
- Test business logic in isolation
- Verify service coordination and error handling

### **Integration Testing**  
- Test handler-service interactions
- Verify FSM state transitions
- Test API integration with mock servers

### **Localization Testing**
- Verify all text keys exist in all languages
- Test parameter substitution
- Verify cultural adaptations

## 📈 Scalability Considerations

### **Horizontal Scaling**
- Stateless service design enables multiple bot instances
- Session data can be moved to external storage (Redis, etc.)
- API client connection pooling for high throughput

### **Vertical Scaling**
- Memory-efficient session management
- Lazy loading of services and resources
- Configurable timeouts and limits

### **Performance**
- Caching frequently accessed data
- Async/await patterns throughout
- Efficient database/API call patterns

This architecture ensures the business layer is maintainable, testable, scalable, and follows modern software engineering best practices while providing a solid foundation for bot functionality. 