"""
Unified network layer supporting both async and sync operations
"""
import os
import logging
import asyncio
from typing import Optional, Dict, Any, Union
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False
    import requests

class NetworkManager:
    def __init__(self):
        self.session = None
        self._setup_session()
    
    def _setup_session(self):
        """Initialize the appropriate session type"""
        if HAS_AIOHTTP:
            self.session = aiohttp.ClientSession()
        else:
            self.session = requests.Session()
    
    async def request(
        self,
        url: str,
        method: str = 'GET',
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Any] = None,
        timeout: int = 30
    ) -> Union[str, bytes]:
        """Make a network request"""
        if HAS_AIOHTTP:
            return await self._async_request(url, method, headers, data, timeout)
        else:
            return self._sync_request(url, method, headers, data, timeout)
    
    async def _async_request(
        self,
        url: str,
        method: str,
        headers: Optional[Dict[str, str]],
        data: Optional[Any],
        timeout: int
    ) -> Union[str, bytes]:
        """Make an async request using aiohttp"""
        try:
            async with self.session.request(
                method, url, headers=headers, data=data, timeout=timeout
            ) as response:
                if 'text' in response.headers.get('content-type', '').lower():
                    return await response.text()
                return await response.read()
        except Exception as e:
            logger.error(f'Async request failed: {str(e)}')
            raise
    
    def _sync_request(
        self,
        url: str,
        method: str,
        headers: Optional[Dict[str, str]],
        data: Optional[Any],
        timeout: int
    ) -> Union[str, bytes]:
        """Make a sync request using requests"""
        try:
            response = self.session.request(
                method, url, headers=headers, data=data, timeout=timeout
            )
            response.raise_for_status()
            if 'text' in response.headers.get('content-type', '').lower():
                return response.text
            return response.content
        except Exception as e:
            logger.error(f'Sync request failed: {str(e)}')
            raise
    
    async def close(self):
        """Close the session"""
        if HAS_AIOHTTP and self.session:
            await self.session.close()
            
    def __del__(self):
        """Cleanup when object is deleted"""
        if self.session:
            if HAS_AIOHTTP:
                asyncio.create_task(self.close())
            else:
                self.session.close()
