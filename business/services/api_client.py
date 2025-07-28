"""
API client for external service integration.

Handles HTTP requests to external APIs for submitting questionnaire answers
and other data persistence operations.
"""

import aiohttp
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass

from core.utils.logger import get_logger
from config import config
from business.services.interfaces import ApiClientProtocol, ApiResponse

logger = get_logger()


class ApiClient(ApiClientProtocol):
    """HTTP client for external API integration."""
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for API endpoints
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or config.api_base_url
        self.timeout = aiohttp.ClientTimeout(total=timeout or config.api_timeout)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'TelegramBot/1.0'
                }
            )
        return self._session
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> ApiResponse:
        """
        Make HTTP request to API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            
        Returns:
            ApiResponse with success/failure status and data
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            session = await self._get_session()
            
            logger.debug(f"Making {method} request to {url}")
            
            async with session.request(
                method=method,
                url=url,
                json=data,
                params=params
            ) as response:
                
                status_code = response.status
                
                try:
                    response_data = await response.json()
                except Exception:
                    response_data = {"message": await response.text()}
                
                if 200 <= status_code < 300:
                    logger.info(f"API request successful: {method} {url} -> {status_code}")
                    return ApiResponse(
                        success=True,
                        data=response_data,
                        status_code=status_code
                    )
                else:
                    error_msg = response_data.get('error', f'HTTP {status_code}')
                    logger.warning(f"API request failed: {method} {url} -> {status_code}: {error_msg}")
                    return ApiResponse(
                        success=False,
                        error=error_msg,
                        status_code=status_code,
                        data=response_data
                    )
                    
        except asyncio.TimeoutError:
            error_msg = f"Request timeout ({self.timeout.total}s)"
            logger.error(f"API request timeout: {method} {url}")
            return ApiResponse(success=False, error=error_msg)
            
        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(f"API request error: {method} {url} - {error_msg}")
            return ApiResponse(success=False, error=error_msg)
    
    async def submit_questionnaire_answer(
        self, 
        user_id: int, 
        question_key: str, 
        answer: str,
        session_id: Optional[str] = None
    ) -> ApiResponse:
        """
        Submit a single questionnaire answer.
        
        Args:
            user_id: Telegram user ID
            question_key: Question identifier (e.g., 'question_1', 'gender')
            answer: User's answer
            session_id: Optional session identifier for grouping answers
            
        Returns:
            ApiResponse indicating success/failure
        """
        data = {
            'user_id': user_id,
            'question_key': question_key,
            'answer': answer,
            'timestamp': asyncio.get_event_loop().time()
        }
        
        if session_id:
            data['session_id'] = session_id
        
        return await self._make_request('POST', '/questionnaire/answers', data)
    
    async def submit_gender(self, user_id: int, gender: str) -> ApiResponse:
        """
        Submit gender information.
        
        Args:
            user_id: Telegram user ID
            gender: User's gender
            
        Returns:
            ApiResponse indicating success/failure
        """
        return await self.submit_questionnaire_answer(user_id, 'gender', gender)
    
    async def complete_questionnaire(
        self, 
        user_id: int, 
        session_id: Optional[str] = None
    ) -> ApiResponse:
        """
        Mark questionnaire as completed.
        
        Args:
            user_id: Telegram user ID
            session_id: Session identifier
            
        Returns:
            ApiResponse indicating success/failure
        """
        data = {
            'user_id': user_id,
            'completed_at': asyncio.get_event_loop().time()
        }
        
        if session_id:
            data['session_id'] = session_id
        
        return await self._make_request('POST', '/questionnaire/complete', data)
    
    async def close(self):
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()


# Global API client instance
_api_client: Optional[ApiClient] = None


def get_api_client() -> ApiClient:
    """Get the global API client instance."""
    global _api_client
    if _api_client is None:
        _api_client = ApiClient()
    return _api_client 