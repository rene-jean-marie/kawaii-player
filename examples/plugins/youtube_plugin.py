"""
Example YouTube plugin for Kawaii Player
"""
import re
import json
import logging
from typing import Optional, Dict, List
from PyQt5 import QtCore

from kawaii_player import NetworkManager, PlaylistManager, SettingsManager

logger = logging.getLogger(__name__)

class YouTubePlugin(QtCore.QObject):
    """Plugin for YouTube integration"""
    
    # Signals
    search_completed = QtCore.pyqtSignal(list)  # list of results
    video_info_loaded = QtCore.pyqtSignal(dict)  # video metadata
    
    def __init__(
        self,
        network: NetworkManager,
        playlist: PlaylistManager,
        settings: SettingsManager
    ):
        super().__init__()
        self.network = network
        self.playlist = playlist
        self.settings = settings
        self.api_key = settings.get('plugins.youtube.api_key', '')
    
    async def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search YouTube videos"""
        if not self.api_key:
            logger.error('YouTube API key not set')
            return []
            
        try:
            url = (
                'https://www.googleapis.com/youtube/v3/search'
                f'?key={self.api_key}'
                f'&q={query}'
                f'&maxResults={max_results}'
                '&part=snippet'
                '&type=video'
            )
            
            response = await self.network.request(url)
            data = json.loads(response)
            
            results = []
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                snippet = item['snippet']
                results.append({
                    'id': video_id,
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'thumbnail': snippet['thumbnails']['medium']['url'],
                    'url': f'https://www.youtube.com/watch?v={video_id}'
                })
            
            self.search_completed.emit(results)
            return results
            
        except Exception as e:
            logger.error(f'YouTube search failed: {str(e)}')
            return []
    
    async def get_video_info(self, video_id: str) -> Optional[Dict]:
        """Get detailed video information"""
        if not self.api_key:
            logger.error('YouTube API key not set')
            return None
            
        try:
            url = (
                'https://www.googleapis.com/youtube/v3/videos'
                f'?key={self.api_key}'
                f'&id={video_id}'
                '&part=snippet,contentDetails,statistics'
            )
            
            response = await self.network.request(url)
            data = json.loads(response)
            
            if not data.get('items'):
                return None
                
            video = data['items'][0]
            info = {
                'id': video_id,
                'title': video['snippet']['title'],
                'description': video['snippet']['description'],
                'duration': video['contentDetails']['duration'],
                'views': video['statistics']['viewCount'],
                'likes': video['statistics'].get('likeCount', 0),
                'thumbnail': video['snippet']['thumbnails']['high']['url']
            }
            
            self.video_info_loaded.emit(info)
            return info
            
        except Exception as e:
            logger.error(f'Failed to get video info: {str(e)}')
            return None
    
    def add_to_playlist(
        self,
        video_info: Dict,
        playlist_name: Optional[str] = None
    ) -> bool:
        """Add a YouTube video to a playlist"""
        try:
            return self.playlist.add_item(
                title=video_info['title'],
                url=video_info['url'],
                playlist_name=playlist_name,
                thumbnail=video_info.get('thumbnail'),
                metadata={
                    'source': 'youtube',
                    'video_id': video_info['id'],
                    'views': video_info.get('views'),
                    'likes': video_info.get('likes')
                }
            )
        except Exception as e:
            logger.error(f'Failed to add to playlist: {str(e)}')
            return False
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:v=|/v/|youtu\.be/)([^"&?/\s]{11})',
            r'(?:embed/)([^"&?/\s]{11})',
            r'(?:watch\?feature=player_embedded&v=)([^"&?/\s]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
