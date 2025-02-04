"""
Example Crunchyroll plugin for Kawaii Player
"""
import re
import json
import logging
import asyncio
from typing import Optional, Dict, List
from PyQt5 import QtCore

from kawaii_player import (
    NetworkManager,
    PlaylistManager,
    SettingsManager,
    HLSStream
)

logger = logging.getLogger(__name__)

class CrunchyrollPlugin(QtCore.QObject):
    """Plugin for Crunchyroll integration"""
    
    # Signals
    search_completed = QtCore.pyqtSignal(list)  # search results
    series_loaded = QtCore.pyqtSignal(dict)  # series info
    episode_loaded = QtCore.pyqtSignal(dict)  # episode info
    
    def __init__(
        self,
        network: NetworkManager,
        playlist: PlaylistManager,
        settings: SettingsManager,
        hls: HLSStream
    ):
        super().__init__()
        self.network = network
        self.playlist = playlist
        self.settings = settings
        self.hls = hls
        
        # Get API credentials
        self.client_id = settings.get('plugins.crunchyroll.client_id', '')
        self.client_secret = settings.get('plugins.crunchyroll.client_secret', '')
        self.access_token = None
        
        # Base URLs
        self.api_base = 'https://beta-api.crunchyroll.com'
        self.auth_base = 'https://beta-api.crunchyroll.com/auth/v1'
    
    async def authenticate(self) -> bool:
        """Get access token"""
        if not (self.client_id and self.client_secret):
            logger.error('Crunchyroll credentials not set')
            return False
            
        try:
            url = f'{self.auth_base}/token'
            data = {
                'grant_type': 'client_credentials',
                'scope': 'streaming read'
            }
            headers = {
                'Authorization': f'Basic {self.client_id}:{self.client_secret}'
            }
            
            response = await self.network.request(
                url,
                method='POST',
                data=data,
                headers=headers
            )
            token_data = json.loads(response)
            
            self.access_token = token_data.get('access_token')
            return bool(self.access_token)
            
        except Exception as e:
            logger.error(f'Crunchyroll authentication failed: {str(e)}')
            return False
    
    async def search(
        self,
        query: str,
        media_type: str = 'anime'
    ) -> List[Dict]:
        """Search for anime/manga"""
        if not self.access_token and not await self.authenticate():
            return []
            
        try:
            url = f'{self.api_base}/content/v1/search'
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            params = {
                'q': query,
                'type': media_type,
                'locale': 'en-US'
            }
            
            response = await self.network.request(
                url,
                method='GET',
                headers=headers,
                params=params
            )
            data = json.loads(response)
            
            results = []
            for item in data.get('items', []):
                result = {
                    'id': item['id'],
                    'type': item['type'],
                    'title': item['title'],
                    'description': item.get('description', ''),
                    'thumbnail': item.get('images', {}).get('poster_tall', [{}])[0].get('source'),
                    'url': f'https://www.crunchyroll.com/{item["type"]}/{item["id"]}'
                }
                results.append(result)
            
            self.search_completed.emit(results)
            return results
            
        except Exception as e:
            logger.error(f'Crunchyroll search failed: {str(e)}')
            return []
    
    async def get_series_info(self, series_id: str) -> Optional[Dict]:
        """Get detailed series information"""
        if not self.access_token and not await self.authenticate():
            return None
            
        try:
            url = f'{self.api_base}/content/v1/series/{series_id}'
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = await self.network.request(
                url,
                method='GET',
                headers=headers
            )
            data = json.loads(response)
            
            series = {
                'id': data['id'],
                'title': data['title'],
                'description': data.get('description', ''),
                'episodes': data.get('episode_count', 0),
                'rating': data.get('rating', ''),
                'genres': data.get('genres', []),
                'thumbnail': data.get('images', {}).get('poster_tall', [{}])[0].get('source'),
                'seasons': []
            }
            
            # Get seasons
            seasons_url = f'{self.api_base}/content/v1/series/{series_id}/seasons'
            seasons_response = await self.network.request(
                seasons_url,
                method='GET',
                headers=headers
            )
            seasons_data = json.loads(seasons_response)
            
            for season in seasons_data.get('items', []):
                series['seasons'].append({
                    'id': season['id'],
                    'title': season['title'],
                    'number': season.get('season_number', 0),
                    'episode_count': season.get('episode_count', 0)
                })
            
            self.series_loaded.emit(series)
            return series
            
        except Exception as e:
            logger.error(f'Failed to get series info: {str(e)}')
            return None
    
    async def get_episode_streams(
        self,
        episode_id: str
    ) -> Optional[Dict]:
        """Get episode streaming information"""
        if not self.access_token and not await self.authenticate():
            return None
            
        try:
            url = f'{self.api_base}/content/v1/episodes/{episode_id}/streams'
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = await self.network.request(
                url,
                method='GET',
                headers=headers
            )
            data = json.loads(response)
            
            streams = {
                'adaptive_hls': {},
                'subtitles': []
            }
            
            # Get HLS streams
            for stream in data.get('streams', []):
                if stream['type'] == 'adaptive_hls':
                    streams['adaptive_hls'][stream['quality']] = stream['url']
            
            # Get subtitles
            for sub in data.get('subtitles', []):
                streams['subtitles'].append({
                    'locale': sub['locale'],
                    'url': sub['url'],
                    'format': sub['format']
                })
            
            return streams
            
        except Exception as e:
            logger.error(f'Failed to get episode streams: {str(e)}')
            return None
    
    async def get_season_episodes(
        self,
        season_id: str
    ) -> List[Dict]:
        """Get episodes for a season"""
        if not self.access_token and not await self.authenticate():
            return []
            
        try:
            url = f'{self.api_base}/content/v1/seasons/{season_id}/episodes'
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = await self.network.request(
                url,
                method='GET',
                headers=headers
            )
            data = json.loads(response)
            
            episodes = []
            for ep in data.get('items', []):
                episode = {
                    'id': ep['id'],
                    'title': ep['title'],
                    'number': ep.get('episode_number', 0),
                    'description': ep.get('description', ''),
                    'duration': ep.get('duration_ms', 0) / 1000,
                    'thumbnail': ep.get('images', {}).get('thumbnail', [{}])[0].get('source')
                }
                episodes.append(episode)
            
            return episodes
            
        except Exception as e:
            logger.error(f'Failed to get season episodes: {str(e)}')
            return []
    
    def add_to_playlist(
        self,
        episode_info: Dict,
        playlist_name: Optional[str] = None
    ) -> bool:
        """Add episode to playlist"""
        try:
            return self.playlist.add_item(
                title=f"Episode {episode_info['number']} - {episode_info['title']}",
                url=f"crunchyroll://{episode_info['id']}",
                duration=episode_info.get('duration', 0),
                thumbnail=episode_info.get('thumbnail'),
                metadata={
                    'source': 'crunchyroll',
                    'episode_id': episode_info['id'],
                    'episode_number': episode_info['number']
                },
                playlist_name=playlist_name
            )
        except Exception as e:
            logger.error(f'Failed to add to playlist: {str(e)}')
            return False
    
    async def play_episode(self, episode_id: str):
        """Play an episode"""
        try:
            # Get stream info
            streams = await self.get_episode_streams(episode_id)
            if not streams:
                return False
            
            # Get highest quality HLS stream
            qualities = list(streams['adaptive_hls'].keys())
            if not qualities:
                return False
                
            best_quality = max(qualities)
            stream_url = streams['adaptive_hls'][best_quality]
            
            # Load stream
            await self.hls.load_playlist(stream_url)
            
            # Load subtitles if available
            for sub in streams['subtitles']:
                if sub['locale'] == self.settings.get(
                    'player.subtitle_language',
                    'en-US'
                ):
                    # Download and load subtitle
                    sub_content = await self.network.request(sub['url'])
                    sub_path = f'/tmp/cr_sub_{episode_id}.{sub["format"]}'
                    
                    with open(sub_path, 'wb') as f:
                        f.write(sub_content)
                    
                    self.player.load_subtitle(sub_path)
                    break
            
            return True
            
        except Exception as e:
            logger.error(f'Failed to play episode: {str(e)}')
            return False
