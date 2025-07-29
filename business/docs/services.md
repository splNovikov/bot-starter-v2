# 🛠️ Service Development Guide

This guide explains how to create reusable business logic services that handlers can use to implement bot functionality.

## 📋 Service Principles

### 1. Single Responsibility Principle (SRP)
Each service should focus on one business domain or responsibility:
- **Greeting service**: User greeting and personalization
- **Localization service**: Multi-language support and text localization
- **Help service**: Localized help text generation
- **Questionnaire service**: Orchestrates questionnaire interactions
- **Session manager**: Manages questionnaire session lifecycle
- **Question provider**: Handles question logic and sequencing
- **API client**: External HTTP communication
- **Database service**: Data persistence operations
- **Auth service**: User authentication and authorization

### 2. Dependency Inversion Principle (DIP)
Services depend on interfaces, not concrete implementations:
- Use protocols to define service interfaces
- Enable dependency injection for testing
- Allow easy swapping of implementations

### 3. Stateless Design
Services should be stateless functions when possible:
- Easy to test and reason about
- No hidden dependencies or side effects
- Predictable behavior across calls

### 4. Clear Interfaces
Services provide simple, clear APIs for handlers:
- Handler calls service function
- Service handles all business logic
- Service returns result or raises exception

### 5. Error Handling
Services handle their own errors gracefully:
- Log errors with proper context
- Provide fallback behavior when possible
- Re-raise exceptions for handlers to handle

## 🎨 Service Patterns

### 1. Utility Functions

Pure functions for data transformation:

```python
from aiogram.types import User

def get_username(user: User) -> str:
    """Extract display-friendly username from Telegram user."""
    return user.first_name or user.username or "Anonymous"

def format_user_info(user: User) -> dict:
    """Format user data for display."""
    return {
        "id": user.id,
        "name": get_username(user),
        "username": f"@{user.username}" if user.username else None
    }

def validate_command_args(args: list, min_args: int) -> bool:
    """Validate command has minimum required arguments."""
    return len(args) >= min_args
```

### 2. Orchestrating Services

Services that coordinate between multiple specialized services:

```python
from core.protocols.base import ApiClientProtocol
from core.questionnaire.protocols import SessionManagerProtocol

class QuestionnaireService:
    """Orchestrates questionnaire interactions."""
    
    def __init__(
        self,
        api_client: ApiClientProtocol,
        session_manager: SessionManagerProtocol
    ):
        self._api_client = api_client
        self._session_manager = session_manager
    
    async def submit_answer(self, user_id: int, answer: str) -> bool:
        """Submit answer using coordinated services."""
        # Use session manager for state
        session = self._session_manager.get_session(user_id)
        if not session:
            return False
        
        # Use API client for persistence
        result = await self._api_client.submit_answer(user_id, answer)
        return result.success
```

### 3. Specialized Services

Services with focused, single responsibilities:

```python
from core.questionnaire.protocols import SessionManagerProtocol

class SessionManager(SessionManagerProtocol):
    """Manages questionnaire session lifecycle."""
    
    def create_session(self, user_id: int) -> str:
        """Create new session."""
        session_id = str(uuid.uuid4())
        self._sessions[user_id] = QuestionnaireSession(
            session_id=session_id,
            user_id=user_id,
            current_question=0,
            answers={}
        )
        return session_id
    
    def add_answer(self, user_id: int, question_key: str, answer: str) -> bool:
        """Add answer to session."""
        session = self._sessions.get(user_id)
        if not session:
            return False
        session.answers[question_key] = answer
        return True
```

### 4. Interface-Based Services

Services implementing protocols for testability:

```python
from core.protocols.base import ApiClientProtocol, ApiResponse

class ApiClient(ApiClientProtocol):
    """HTTP client implementing the API protocol."""
    
    async def submit_questionnaire_answer(
        self, 
        user_id: int, 
        question_key: str, 
        answer: str,
        session_id: Optional[str] = None
    ) -> ApiResponse:
        """Submit answer to external API."""
        try:
            async with self._get_session() as session:
                async with session.post(
                    f"{self.base_url}/questionnaire/answers",
                    json={
                        'user_id': user_id,
                        'question_key': question_key,
                        'answer': answer,
                        'session_id': session_id
                    }
                ) as response:
                    data = await response.json()
                    return ApiResponse(
                        success=response.status < 400,
                        data=data,
                        status_code=response.status
                    )
        except Exception as e:
            return ApiResponse(success=False, error=str(e))
```

## 🧪 Testing Services

Services are designed for easy testing through dependency injection:

```python
import pytest
from unittest.mock import Mock
from business.services.questionnaire_service import QuestionnaireService

def test_questionnaire_service():
    # Mock dependencies
    mock_api_client = Mock()
    mock_session_manager = Mock()
    mock_question_provider = Mock()
    
    # Inject mocks
    service = QuestionnaireService(
        api_client=mock_api_client,
        session_manager=mock_session_manager,
        question_provider=mock_question_provider
    )
    
    # Test behavior
    mock_session_manager.get_session.return_value = {'answers': {}}
    mock_question_provider.get_next_question.return_value = 'question_1'
    
    # Verify service coordinates correctly
    result = service.get_current_question_key(123, mock_user)
    assert result == 'question_1'
    mock_session_manager.get_session.assert_called_with(123)
```

## 📚 Available Services

### Core Services
- **`LocalizationService`** - Multi-language text management
- **`LoggingService`** - Structured logging with context

### Business Services  
- **`GreetingService`** - User greeting and personalization
- **`HelpService`** - Localized help text generation

### Questionnaire Services
- **`QuestionnaireService`** - Orchestrates questionnaire flow
- **`SessionManager`** - Manages session lifecycle and state
- **`QuestionProvider`** - Handles question logic and sequencing
- **`ApiClient`** - External API communication

## 🔧 Service Registration

Services are registered globally for easy access:

```python
# business/services/__init__.py
from .questionnaire_service import get_questionnaire_service
from .session_manager import get_session_manager
from .question_provider import get_question_provider
from .api_client import get_api_client

# Global access functions
def get_questionnaire_service() -> QuestionnaireService:
    global _questionnaire_service
    if _questionnaire_service is None:
        _questionnaire_service = QuestionnaireService()
    return _questionnaire_service
```

## 🎯 Best Practices

### Service Design
1. **Single Responsibility** - One service, one concern
2. **Interface Segregation** - Small, focused interfaces
3. **Dependency Injection** - Inject dependencies, don't create them
4. **Fail Fast** - Validate inputs early
5. **Comprehensive Logging** - Log all important operations

### Error Handling
1. **Graceful Degradation** - Continue operation when possible
2. **Meaningful Messages** - Provide localized error messages
3. **Proper Logging** - Log errors with context
4. **Exception Propagation** - Let handlers decide error response

### Testing
1. **Mock Dependencies** - Use interfaces to enable mocking
2. **Test Behavior** - Focus on service interactions
3. **Edge Cases** - Test error conditions and edge cases
4. **Integration Tests** - Test service coordination

This architecture ensures services are maintainable, testable, and follow SOLID principles while providing clear separation of concerns. 