"""
Example subtitle plugin for Kawaii Player
"""
import os
import re
import logging
from typing import Optional, Dict, List
from PyQt5 import QtCore

from kawaii_player import NetworkManager, SettingsManager, UnifiedPlayer

logger = logging.getLogger(__name__)

class SubtitlePlugin(QtCore.QObject):
    """Plugin for subtitle download and management"""
    
    # Signals
    subtitles_found = QtCore.pyqtSignal(list)  # list of available subtitles
    subtitle_downloaded = QtCore.pyqtSignal(str)  # path to downloaded subtitle
    
    def __init__(
        self,
        network: NetworkManager,
        player: UnifiedPlayer,
        settings: SettingsManager
    ):
        super().__init__()
        self.network = network
        self.player = player
        self.settings = settings
        
        # Get API keys from settings
        self.opensubtitles_key = settings.get(
            'plugins.subtitles.opensubtitles_key',
            ''
        )
        
        # Configure subtitle directory
        self.subtitle_dir = os.path.join(
            settings.get(
                'downloads.download_path',
                os.path.expanduser('~/Downloads')
            ),
            'subtitles'
        )
        os.makedirs(self.subtitle_dir, exist_ok=True)
    
    async def search_subtitles(
        self,
        query: str,
        language: str = 'eng'
    ) -> List[Dict]:
        """Search for subtitles using OpenSubtitles API"""
        if not self.opensubtitles_key:
            logger.error('OpenSubtitles API key not set')
            return []
            
        try:
            url = 'https://api.opensubtitles.com/api/v1/subtitles'
            headers = {
                'Api-Key': self.opensubtitles_key,
                'Content-Type': 'application/json'
            }
            params = {
                'query': query,
                'languages': language
            }
            
            response = await self.network.request(
                url,
                method='GET',
                headers=headers,
                params=params
            )
            data = response.json()
            
            results = []
            for item in data.get('data', []):
                subtitle = {
                    'id': item['id'],
                    'language': item['attributes']['language'],
                    'title': item['attributes']['feature_details']['title'],
                    'format': item['attributes']['format'],
                    'download_url': item['attributes']['files'][0]['file_id'],
                    'rating': item['attributes'].get('ratings', 0)
                }
                results.append(subtitle)
            
            self.subtitles_found.emit(results)
            return results
            
        except Exception as e:
            logger.error(f'Subtitle search failed: {str(e)}')
            return []
    
    async def download_subtitle(
        self,
        subtitle_id: str,
        file_id: str
    ) -> Optional[str]:
        """Download a subtitle file"""
        if not self.opensubtitles_key:
            logger.error('OpenSubtitles API key not set')
            return None
            
        try:
            # Get download link
            url = f'https://api.opensubtitles.com/api/v1/download/{file_id}'
            headers = {'Api-Key': self.opensubtitles_key}
            
            response = await self.network.request(
                url,
                method='POST',
                headers=headers
            )
            data = response.json()
            
            if 'link' not in data:
                logger.error('No download link in response')
                return None
            
            # Download subtitle file
            subtitle_content = await self.network.request(
                data['link'],
                method='GET'
            )
            
            # Save to file
            filename = f'subtitle_{subtitle_id}.srt'
            filepath = os.path.join(self.subtitle_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(subtitle_content)
            
            self.subtitle_downloaded.emit(filepath)
            return filepath
            
        except Exception as e:
            logger.error(f'Subtitle download failed: {str(e)}')
            return None
    
    def load_subtitle(self, filepath: str):
        """Load subtitle into player"""
        try:
            self.player.load_subtitle(filepath)
        except Exception as e:
            logger.error(f'Failed to load subtitle: {str(e)}')
    
    def get_media_hash(self, filepath: str) -> Optional[str]:
        """Calculate hash of media file for subtitle search"""
        try:
            size = os.path.getsize(filepath)
            
            with open(filepath, 'rb') as f:
                # Read first 64KB
                head = f.read(64 * 1024)
                f.seek(max(0, size - 64 * 1024))
                tail = f.read(64 * 1024)
            
            # Calculate hash
            media_hash = md5()
            media_hash.update(head)
            media_hash.update(tail)
            
            return media_hash.hexdigest()
            
        except Exception as e:
            logger.error(f'Failed to calculate media hash: {str(e)}')
            return None
    
    def clean_subtitle_cache(self, max_age_days: int = 30):
        """Remove old subtitle files"""
        try:
            current_time = time.time()
            for file in os.listdir(self.subtitle_dir):
                filepath = os.path.join(self.subtitle_dir, file)
                if os.path.isfile(filepath):
                    age_days = (
                        current_time - os.path.getmtime(filepath)
                    ) / (24 * 3600)
                    
                    if age_days > max_age_days:
                        os.remove(filepath)
                        
        except Exception as e:
            logger.error(f'Failed to clean subtitle cache: {str(e)}')
    
    def extract_subtitle_track(
        self,
        media_file: str,
        track_index: int
    ) -> Optional[str]:
        """Extract embedded subtitle from media file"""
        try:
            output = os.path.join(
                self.subtitle_dir,
                f'extracted_{os.path.basename(media_file)}.srt'
            )
            
            self.player.extract_subtitle(
                media_file,
                output,
                track_index
            )
            
            if os.path.exists(output):
                self.subtitle_downloaded.emit(output)
                return output
            return None
            
        except Exception as e:
            logger.error(f'Failed to extract subtitle: {str(e)}')
            return None
