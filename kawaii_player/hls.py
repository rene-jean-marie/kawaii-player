"""
Unified HLS (HTTP Live Streaming) implementation
"""
import os
import logging
import asyncio
from typing import Optional, List, Dict
from urllib.parse import urljoin

from .network import NetworkManager

logger = logging.getLogger(__name__)

class HLSStream:
    """HLS stream handler supporting both WebEngine and WebKit"""
    
    def __init__(self):
        self.network = NetworkManager()
        self.current_playlist = None
        self.segments: List[str] = []
        self.base_url: Optional[str] = None
        self.sequence = 0
        self.target_duration = 10
        self.is_endlist = False
        
    async def load_playlist(self, url: str) -> bool:
        """Load and parse M3U8 playlist"""
        try:
            content = await self.network.request(url)
            if not isinstance(content, str):
                content = content.decode('utf-8')
                
            if not content.startswith('#EXTM3U'):
                logger.error('Invalid M3U8 playlist')
                return False
                
            self.base_url = url
            self.segments = []
            self.current_playlist = content
            
            lines = content.splitlines()
            segment_url = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('#EXT-X-MEDIA-SEQUENCE:'):
                    self.sequence = int(line.split(':')[1])
                elif line.startswith('#EXT-X-TARGETDURATION:'):
                    self.target_duration = int(line.split(':')[1])
                elif line.startswith('#EXT-X-ENDLIST'):
                    self.is_endlist = True
                elif line.startswith('#EXTINF:'):
                    continue
                elif not line.startswith('#'):
                    if line.startswith('http'):
                        segment_url = line
                    else:
                        segment_url = urljoin(self.base_url, line)
                    self.segments.append(segment_url)
            
            return True
        except Exception as e:
            logger.error(f'Failed to load playlist: {str(e)}')
            return False
    
    async def download_segment(self, url: str, output_path: str) -> bool:
        """Download a single HLS segment"""
        try:
            content = await self.network.request(url)
            if isinstance(content, str):
                content = content.encode('utf-8')
                
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f'Failed to download segment: {str(e)}')
            return False
    
    async def monitor_live_stream(self, callback):
        """Monitor a live HLS stream for new segments"""
        while not self.is_endlist:
            if await self.load_playlist(self.base_url):
                for segment in self.segments[self.sequence:]:
                    await callback(segment)
                    self.sequence += 1
            await asyncio.sleep(self.target_duration)
    
    def get_current_segments(self) -> List[str]:
        """Get list of current segments"""
        return self.segments
    
    async def close(self):
        """Clean up resources"""
        await self.network.close()
