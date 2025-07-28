# 🎯 Practical Examples

This guide provides real-world examples of implementing common bot features using the handler and service architecture.

## 📋 Example 1: Weather Bot

Complete implementation of a weather command with external API integration.

### Step 1: Create Weather Service

```python
# business/services/weather.py

import aiohttp
import asyncio
from typing import Optional
from dataclasses import dataclass
from core.utils.logger import get_logger

logger = get_logger()

@dataclass
class WeatherData:
    """Weather information data structure."""
    city: str
    temperature: float
    description: str
    humidity: int
    wind_speed: float

class WeatherService:
    """Weather API service with configuration and caching."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.openweathermap.org/data/2.5"):
        self.api_key = api_key
        self.base_url = base_url
        self._cache = {}  # Simple in-memory cache
        
    async def get_weather(self, city: str) -> Optional[WeatherData]:
        """Get weather data for a city."""
        try:
            # Check cache first (5 minute TTL)
            cache_key = city.lower()
            if cache_key in self._cache:
                cached_data, timestamp = self._cache[cache_key]
                if asyncio.get_event_loop().time() - timestamp < 300:  # 5 minutes
                    return cached_data
            
            # Fetch from API
            weather_data = await self._fetch_weather_data(city)
            
            # Cache the result
            if weather_data:
                self._cache[cache_key] = (weather_data, asyncio.get_event_loop().time())
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Weather service error for {city}: {e}")
            return None
    
    async def _fetch_weather_data(self, city: str) -> Optional[WeatherData]:
        """Fetch weather data from API."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/weather"
                params = {
                    'q': city,
                    'appid': self.api_key,
                    'units': 'metric'
                }
                
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return WeatherData(
                            city=data['name'],
                            temperature=data['main']['temp'],
                            description=data['weather'][0]['description'],
                            humidity=data['main']['humidity'],
                            wind_speed=data['wind']['speed']
                        )
                    elif response.status == 404:
                        logger.warning(f"City not found: {city}")
                        return None
                    else:
                        logger.error(f"Weather API error: {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error(f"Weather API timeout for {city}")
            return None
        except Exception as e:
            logger.error(f"Weather API request failed: {e}")
            return None

# Service instance (configured from environment)
import os
weather_service = WeatherService(os.getenv('OPENWEATHER_API_KEY', ''))

async def get_weather(city: str) -> str:
    """Get formatted weather information for a city."""
    if not weather_service.api_key:
        return "Weather service not configured. Please set OPENWEATHER_API_KEY."
    
    weather_data = await weather_service.get_weather(city)
    
    if not weather_data:
        return f"Sorry, I couldn't find weather information for '{city}'. Please check the city name."
    
    return format_weather_message(weather_data)

def format_weather_message(weather: WeatherData) -> str:
    """Format weather data for user display."""
    return (
        f"🌤️ **Weather in {weather.city}**\n\n"
        f"🌡️ Temperature: {weather.temperature:.1f}°C\n"
        f"☁️ Condition: {weather.description.title()}\n"
        f"💧 Humidity: {weather.humidity}%\n"
        f"💨 Wind Speed: {weather.wind_speed} m/s"
    )
```

### Step 2: Create Handler

```python
# In business/handlers/user_handlers.py

@command(
    "weather",
    description="Get current weather information for any city",
    category=HandlerCategory.UTILITY,
    usage="/weather <city name>",
    examples=[
        "/weather London",
        "/weather New York",
        "/weather Tokyo"
    ],
    aliases=["w"],
    tags=["weather", "utility", "api"]
)
async def cmd_weather(message: Message) -> None:
    """Handle /weather command."""
    args = message.text.split()[1:] if message.text else []
    
    if not args:
        await message.answer(
            "Please specify a city name.\n"
            "Usage: /weather <city name>\n"
            "Examples: /weather London, /weather New York"
        )
        return
    
    city = " ".join(args)
    
    # Show typing indicator
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        weather_info = await get_weather(city)
        await message.answer(weather_info, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error in weather command: {e}")
        await message.answer("Sorry, something went wrong while getting weather information.")
```

### Step 3: Export Service

```python
# business/services/__init__.py
from .weather import get_weather

__all__.extend(['get_weather'])
```

## 📋 Example 2: User Profile System

Complete user profile management with database integration.

### Step 1: Database Service

```python
# business/services/database.py

import aiosqlite
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from core.utils.logger import get_logger

logger = get_logger()

@dataclass
class UserProfile:
    """User profile data structure."""
    user_id: int
    username: str
    display_name: str
    bio: Optional[str] = None
    language: str = "en"
    timezone: Optional[str] = None
    created_at: Optional[str] = None

class DatabaseService:
    """Database service for user data management."""
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        
    async def initialize(self) -> None:
        """Initialize database tables."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    display_name TEXT NOT NULL,
                    bio TEXT,
                    language TEXT DEFAULT 'en',
                    timezone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
    
    async def save_user_profile(self, profile: UserProfile) -> bool:
        """Save or update user profile."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO user_profiles 
                    (user_id, username, display_name, bio, language, timezone)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    profile.user_id,
                    profile.username,
                    profile.display_name,
                    profile.bio,
                    profile.language,
                    profile.timezone
                ))
                await db.commit()
                
            logger.info(f"Saved profile for user {profile.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving user profile: {e}")
            return False
    
    async def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile by ID."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT * FROM user_profiles WHERE user_id = ?", 
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    
                if row:
                    return UserProfile(
                        user_id=row[0],
                        username=row[1],
                        display_name=row[2],
                        bio=row[3],
                        language=row[4],
                        timezone=row[5],
                        created_at=row[6]
                    )
                return None
                
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None

# Service instance
db_service = DatabaseService()

async def get_or_create_profile(user_id: int, username: str, display_name: str) -> UserProfile:
    """Get existing profile or create new one."""
    profile = await db_service.get_user_profile(user_id)
    
    if not profile:
        profile = UserProfile(
            user_id=user_id,
            username=username,
            display_name=display_name
        )
        await db_service.save_user_profile(profile)
    
    return profile

async def update_profile_field(user_id: int, field: str, value: str) -> bool:
    """Update a specific profile field."""
    profile = await db_service.get_user_profile(user_id)
    if not profile:
        return False
    
    # Update the field
    if hasattr(profile, field):
        setattr(profile, field, value)
        return await db_service.save_user_profile(profile)
    
    return False
```

### Step 2: Profile Commands

```python
# In business/handlers/user_handlers.py

@command(
    "profile",
    description="View your profile",
    category=HandlerCategory.USER,
    usage="/profile",
    examples=["/profile"]
)
async def cmd_profile(message: Message) -> None:
    """Show user profile."""
    user = message.from_user
    username = get_username(user)
    
    profile = await get_or_create_profile(user.id, user.username or "", username)
    
    profile_text = (
        f"👤 **Your Profile**\n\n"
        f"📛 Name: {profile.display_name}\n"
        f"🔤 Username: @{profile.username or 'Not set'}\n"
        f"📝 Bio: {profile.bio or 'Not set'}\n"
        f"🌍 Language: {profile.language}\n"
        f"⏰ Timezone: {profile.timezone or 'Not set'}\n"
        f"📅 Member since: {profile.created_at or 'Unknown'}"
    )
    
    await message.answer(profile_text, parse_mode="Markdown")

@command(
    "setbio",
    description="Set your profile bio",
    category=HandlerCategory.USER,
    usage="/setbio <your bio>",
    examples=["/setbio I love coding!"]
)
async def cmd_setbio(message: Message) -> None:
    """Set user bio."""
    args = message.text.split(maxsplit=1)[1:] if message.text else []
    
    if not args:
        await message.answer("Please provide your bio.\nUsage: /setbio <your bio>")
        return
    
    bio = args[0]
    if len(bio) > 200:
        await message.answer("Bio is too long (max 200 characters)")
        return
    
    success = await update_profile_field(message.from_user.id, "bio", bio)
    
    if success:
        await message.answer(f"✅ Bio updated: {bio}")
    else:
        await message.answer("❌ Failed to update bio. Please try again.")
```

## 📋 Example 3: Quiz System

Interactive quiz with state management.

### Step 1: Quiz Service

```python
# business/services/quiz.py

import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from core.utils.logger import get_logger

logger = get_logger()

@dataclass
class Question:
    """Quiz question data structure."""
    question: str
    options: List[str]
    correct_answer: int  # Index of correct option
    explanation: Optional[str] = None

@dataclass
class QuizSession:
    """Active quiz session."""
    user_id: int
    questions: List[Question]
    current_question: int = 0
    correct_answers: int = 0
    started_at: float = 0

class QuizService:
    """Quiz management service."""
    
    def __init__(self):
        self.active_sessions: Dict[int, QuizSession] = {}
        self.questions = self._load_questions()
    
    def _load_questions(self) -> List[Question]:
        """Load quiz questions."""
        return [
            Question(
                "What is the capital of France?",
                ["London", "Berlin", "Paris", "Madrid"],
                2,
                "Paris is the capital and largest city of France."
            ),
            Question(
                "Which planet is closest to the Sun?",
                ["Venus", "Mercury", "Earth", "Mars"],
                1,
                "Mercury is the smallest and innermost planet in the Solar System."
            ),
            Question(
                "What is 15 + 27?",
                ["40", "41", "42", "43"],
                2,
                "15 + 27 = 42"
            ),
            # Add more questions...
        ]
    
    async def start_quiz(self, user_id: int, num_questions: int = 5) -> Question:
        """Start a new quiz session."""
        # Select random questions
        selected_questions = random.sample(self.questions, min(num_questions, len(self.questions)))
        
        session = QuizSession(
            user_id=user_id,
            questions=selected_questions,
            started_at=time.time()
        )
        
        self.active_sessions[user_id] = session
        logger.info(f"Started quiz for user {user_id} with {len(selected_questions)} questions")
        
        return selected_questions[0]
    
    async def answer_question(self, user_id: int, answer: int) -> Dict[str, Any]:
        """Process quiz answer."""
        if user_id not in self.active_sessions:
            return {"error": "No active quiz session"}
        
        session = self.active_sessions[user_id]
        current_q = session.questions[session.current_question]
        
        is_correct = answer == current_q.correct_answer
        if is_correct:
            session.correct_answers += 1
        
        result = {
            "correct": is_correct,
            "correct_answer": current_q.options[current_q.correct_answer],
            "explanation": current_q.explanation,
            "score": f"{session.correct_answers}/{session.current_question + 1}"
        }
        
        session.current_question += 1
        
        # Check if quiz is complete
        if session.current_question >= len(session.questions):
            result["quiz_complete"] = True
            result["final_score"] = f"{session.correct_answers}/{len(session.questions)}"
            result["percentage"] = round((session.correct_answers / len(session.questions)) * 100, 1)
            del self.active_sessions[user_id]
        else:
            result["next_question"] = session.questions[session.current_question]
        
        return result
    
    def get_session(self, user_id: int) -> Optional[QuizSession]:
        """Get active quiz session."""
        return self.active_sessions.get(user_id)

# Service instance
quiz_service = QuizService()
```

### Step 2: Quiz Handlers

```python
# In business/handlers/user_handlers.py

@command(
    "quiz",
    description="Start a knowledge quiz",
    category=HandlerCategory.FUN,
    usage="/quiz [number_of_questions]",
    examples=["/quiz", "/quiz 3"]
)
async def cmd_quiz(message: Message) -> None:
    """Start a quiz."""
    args = message.text.split()[1:] if message.text else []
    
    # Parse number of questions
    num_questions = 5
    if args:
        try:
            num_questions = int(args[0])
            if num_questions < 1 or num_questions > 10:
                await message.answer("Number of questions must be between 1 and 10")
                return
        except ValueError:
            await message.answer("Invalid number. Using default (5 questions)")
    
    try:
        first_question = await quiz_service.start_quiz(message.from_user.id, num_questions)
        
        question_text = format_question(first_question, 1, num_questions)
        await message.answer(question_text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error starting quiz: {e}")
        await message.answer("Sorry, couldn't start the quiz. Please try again.")

def format_question(question: Question, current: int, total: int) -> str:
    """Format question for display."""
    options_text = "\n".join([
        f"{i+1}. {option}" for i, option in enumerate(question.options)
    ])
    
    return (
        f"❓ **Question {current}/{total}**\n\n"
        f"{question.question}\n\n"
        f"{options_text}\n\n"
        f"Send the number of your answer (1-{len(question.options)})"
    )

# Enhanced text handler to process quiz answers
@text_handler(
    "quiz_text_processor",
    description="Process quiz answers and general text",
    category=HandlerCategory.USER,
    hidden=True
)
async def handle_quiz_text(message: Message) -> None:
    """Handle text messages, including quiz answers."""
    user_id = message.from_user.id
    
    # Check if user has active quiz
    session = quiz_service.get_session(user_id)
    if session:
        await handle_quiz_answer(message, session)
    else:
        # Regular text handling (greeting)
        await send_greeting(message)

async def handle_quiz_answer(message: Message, session: QuizSession) -> None:
    """Handle quiz answer."""
    try:
        answer = int(message.text.strip())
        if answer < 1 or answer > len(session.questions[session.current_question].options):
            await message.answer(f"Please send a number between 1 and {len(session.questions[session.current_question].options)}")
            return
    except ValueError:
        await message.answer("Please send the number of your answer")
        return
    
    # Process answer (convert to 0-based index)
    result = await quiz_service.answer_question(message.from_user.id, answer - 1)
    
    if "error" in result:
        await message.answer(result["error"])
        return
    
    # Send answer feedback
    feedback = "✅ Correct!" if result["correct"] else "❌ Incorrect"
    feedback += f"\n\nCorrect answer: {result['correct_answer']}"
    
    if result.get("explanation"):
        feedback += f"\n💡 {result['explanation']}"
    
    feedback += f"\n\n📊 Score: {result['score']}"
    
    await message.answer(feedback)
    
    # Send next question or final results
    if result.get("quiz_complete"):
        final_message = (
            f"🎉 **Quiz Complete!**\n\n"
            f"Final Score: {result['final_score']} ({result['percentage']}%)\n\n"
            f"Great job! Use /quiz to play again."
        )
        await message.answer(final_message, parse_mode="Markdown")
    else:
        next_q = result["next_question"]
        question_text = format_question(
            next_q, 
            session.current_question + 1, 
            len(session.questions)
        )
        await message.answer(question_text, parse_mode="Markdown")
```

## 📋 Example 4: Reminder System

Scheduled reminders with background tasks.

### Step 1: Reminder Service

```python
# business/services/reminders.py

import asyncio
import re
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass
from core.utils.logger import get_logger

logger = get_logger()

@dataclass
class Reminder:
    """Reminder data structure."""
    user_id: int
    chat_id: int
    text: str
    scheduled_time: datetime
    created_at: datetime

class ReminderService:
    """Background reminder service."""
    
    def __init__(self):
        self.reminders: Dict[str, Reminder] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        self.bot = None  # Will be set from main
    
    def set_bot(self, bot):
        """Set bot instance for sending reminders."""
        self.bot = bot
    
    async def schedule_reminder(self, user_id: int, chat_id: int, time_str: str, text: str) -> bool:
        """Schedule a new reminder."""
        try:
            # Parse time string
            delay_seconds = self._parse_time_string(time_str)
            if delay_seconds is None:
                return False
            
            scheduled_time = datetime.now() + timedelta(seconds=delay_seconds)
            reminder_id = f"{user_id}_{int(datetime.now().timestamp())}"
            
            reminder = Reminder(
                user_id=user_id,
                chat_id=chat_id,
                text=text,
                scheduled_time=scheduled_time,
                created_at=datetime.now()
            )
            
            # Store reminder
            self.reminders[reminder_id] = reminder
            
            # Schedule task
            task = asyncio.create_task(self._send_reminder_later(reminder_id, delay_seconds))
            self.tasks[reminder_id] = task
            
            logger.info(f"Scheduled reminder for user {user_id} in {delay_seconds} seconds")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling reminder: {e}")
            return False
    
    def _parse_time_string(self, time_str: str) -> Optional[int]:
        """Parse time string like '5m', '1h', '2d' into seconds."""
        pattern = r'^(\d+)([smhd])$'
        match = re.match(pattern, time_str.lower())
        
        if not match:
            return None
        
        value, unit = match.groups()
        value = int(value)
        
        multipliers = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400
        }
        
        return value * multipliers[unit]
    
    async def _send_reminder_later(self, reminder_id: str, delay: int) -> None:
        """Send reminder after delay."""
        try:
            await asyncio.sleep(delay)
            
            if reminder_id in self.reminders and self.bot:
                reminder = self.reminders[reminder_id]
                
                message = (
                    f"⏰ **Reminder**\n\n"
                    f"{reminder.text}\n\n"
                    f"_Set {self._format_time_ago(reminder.created_at)}_"
                )
                
                await self.bot.send_message(
                    chat_id=reminder.chat_id,
                    text=message,
                    parse_mode="Markdown"
                )
                
                logger.info(f"Sent reminder to user {reminder.user_id}")
            
            # Cleanup
            self.reminders.pop(reminder_id, None)
            self.tasks.pop(reminder_id, None)
            
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
    
    def _format_time_ago(self, created_at: datetime) -> str:
        """Format how long ago reminder was created."""
        delta = datetime.now() - created_at
        
        if delta.days > 0:
            return f"{delta.days} day(s) ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour(s) ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute(s) ago"
        else:
            return "just now"
    
    def get_user_reminders(self, user_id: int) -> List[Reminder]:
        """Get active reminders for user."""
        return [r for r in self.reminders.values() if r.user_id == user_id]

# Service instance
reminder_service = ReminderService()
```

### Step 2: Reminder Handler

```python
# In business/handlers/user_handlers.py

@command(
    "remind",
    description="Set a reminder",
    category=HandlerCategory.UTILITY,
    usage="/remind <time> <message>",
    examples=[
        "/remind 5m Take a break",
        "/remind 1h Meeting with team",
        "/remind 2d Pay bills"
    ]
)
async def cmd_remind(message: Message) -> None:
    """Handle /remind command."""
    args = message.text.split(maxsplit=2)[1:] if message.text else []
    
    if len(args) < 2:
        await message.answer(
            "Usage: /remind <time> <message>\n\n"
            "Time formats:\n"
            "• 30s - 30 seconds\n"
            "• 5m - 5 minutes\n"
            "• 2h - 2 hours\n"
            "• 1d - 1 day\n\n"
            "Example: /remind 1h Take a break"
        )
        return
    
    time_str = args[0]
    reminder_text = args[1]
    
    success = await reminder_service.schedule_reminder(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        time_str=time_str,
        text=reminder_text
    )
    
    if success:
        await message.answer(f"✅ Reminder set: {reminder_text}")
    else:
        await message.answer(
            "❌ Invalid time format. Use: 30s, 5m, 1h, 2d\n"
            "Example: /remind 1h Take a break"
        )

@command(
    "reminders",
    description="View your active reminders",
    category=HandlerCategory.UTILITY,
    usage="/reminders"
)
async def cmd_reminders(message: Message) -> None:
    """Show user's active reminders."""
    reminders = reminder_service.get_user_reminders(message.from_user.id)
    
    if not reminders:
        await message.answer("You have no active reminders.")
        return
    
    reminder_list = []
    for i, reminder in enumerate(reminders, 1):
        time_left = reminder.scheduled_time - datetime.now()
        if time_left.total_seconds() > 0:
            reminder_list.append(
                f"{i}. {reminder.text}\n"
                f"   ⏱️ In {format_time_delta(time_left)}"
            )
    
    if reminder_list:
        message_text = "⏰ **Your Active Reminders:**\n\n" + "\n\n".join(reminder_list)
        await message.answer(message_text, parse_mode="Markdown")
    else:
        await message.answer("You have no active reminders.")

def format_time_delta(delta: timedelta) -> str:
    """Format time delta for display."""
    total_seconds = int(delta.total_seconds())
    
    if total_seconds >= 86400:
        days = total_seconds // 86400
        return f"{days} day(s)"
    elif total_seconds >= 3600:
        hours = total_seconds // 3600
        return f"{hours} hour(s)"
    elif total_seconds >= 60:
        minutes = total_seconds // 60
        return f"{minutes} minute(s)"
    else:
        return f"{total_seconds} second(s)"
```

### Step 3: Integration with Main Bot

```python
# In main.py, add to bot initialization:

from business.services.reminders import reminder_service

async def _create_bot(self) -> Bot:
    """Create and configure bot instance."""
    bot = Bot(
        token=config.token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            protect_content=False,
            allow_sending_without_reply=True
        )
    )
    
    # Set bot instance for reminder service
    reminder_service.set_bot(bot)
    
    return bot
```

## 📚 Key Patterns Demonstrated

### 1. Service Architecture
- **Single Responsibility**: Each service handles one domain
- **Clear Interfaces**: Simple function calls from handlers
- **Error Handling**: Consistent error patterns across services

### 2. Handler Design
- **Thin Handlers**: Delegate business logic to services
- **Rich Metadata**: Comprehensive command information
- **User-Friendly**: Clear usage instructions and examples

### 3. State Management
- **In-Memory Storage**: For temporary data like quiz sessions
- **Database Persistence**: For long-term data like user profiles
- **Background Tasks**: For scheduled operations like reminders

### 4. Error Handling
- **Graceful Degradation**: Fallback responses for errors
- **User Feedback**: Clear error messages for users
- **Logging**: Comprehensive logging for debugging

These examples demonstrate how to build sophisticated bot features while maintaining clean architecture and separation of concerns. Each example can be extended and customized for specific use cases. 