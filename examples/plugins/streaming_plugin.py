"""
Example streaming service plugin for Kawaii Player
"""
import os
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

class StreamingPlugin(QtCore.QObject):
    """Plugin for streaming service integration"""
    
    # Signals
    stream_started = QtCore.pyqtSignal(str)  # stream URL
    stream_ended = QtCore.pyqtSignal()
    stream_error = QtCore.pyqtSignal(str)  # error message
    chat_message = QtCore.pyqtSignal(dict)  # message data
    
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
        
        # Get API credentials from settings
        self.twitch_client_id = settings.get(
            'plugins.streaming.twitch_client_id',
            ''
        )
        self.twitch_secret = settings.get(
            'plugins.streaming.twitch_secret',
            ''
        )
        
        # Stream state
        self.current_stream = None
        self.chat_websocket = None
        self.chat_task = None
    
    async def authenticate(self) -> Optional[str]:
        """Get Twitch access token"""
        if not (self.twitch_client_id and self.twitch_secret):
            logger.error('Twitch credentials not set')
            return None
            
        try:
            url = 'https://id.twitch.tv/oauth2/token'
            data = {
                'client_id': self.twitch_client_id,
                'client_secret': self.twitch_secret,
                'grant_type': 'client_credentials'
            }
            
            response = await self.network.request(
                url,
                method='POST',
                data=data
            )
            token_data = json.loads(response)
            
            return token_data.get('access_token')
            
        except Exception as e:
            logger.error(f'Twitch authentication failed: {str(e)}')
            return None
    
    async def search_streams(
        self,
        query: str,
        max_results: int = 20
    ) -> List[Dict]:
        """Search for live streams"""
        token = await self.authenticate()
        if not token:
            return []
            
        try:
            url = 'https://api.twitch.tv/helix/search/channels'
            headers = {
                'Client-ID': self.twitch_client_id,
                'Authorization': f'Bearer {token}'
            }
            params = {
                'query': query,
                'first': max_results,
                'live_only': True
            }
            
            response = await self.network.request(
                url,
                method='GET',
                headers=headers,
                params=params
            )
            data = json.loads(response)
            
            streams = []
            for item in data.get('data', []):
                stream = {
                    'id': item['id'],
                    'username': item['broadcaster_login'],
                    'title': item['title'],
                    'game': item.get('game_name', 'Unknown'),
                    'viewers': item.get('viewer_count', 0),
                    'thumbnail': item.get(
                        'thumbnail_url',
                        ''
                    ).replace('{width}x{height}', '1280x720'),
                    'language': item.get('broadcaster_language', 'en')
                }
                streams.append(stream)
            
            return streams
            
        except Exception as e:
            logger.error(f'Stream search failed: {str(e)}')
            return []
    
    async def get_stream_url(self, channel: str) -> Optional[str]:
        """Get HLS stream URL for channel"""
        token = await self.authenticate()
        if not token:
            return None
            
        try:
            # Get stream info
            url = f'https://api.twitch.tv/helix/streams?user_login={channel}'
            headers = {
                'Client-ID': self.twitch_client_id,
                'Authorization': f'Bearer {token}'
            }
            
            response = await self.network.request(
                url,
                method='GET',
                headers=headers
            )
            data = json.loads(response)
            
            if not data.get('data'):
                logger.error('Stream not found or offline')
                return None
            
            # Get access token for stream
            url = (
                'https://gql.twitch.tv/gql'
                f'?login={channel}'
                '&platform=web'
                '&player_type=site'
            )
            
            response = await self.network.request(
                url,
                method='POST',
                headers=headers,
                data=json.dumps([{
                    'operationName': 'PlaybackAccessToken',
                    'variables': {
                        'isLive': True,
                        'login': channel,
                        'isVod': False,
                        'vodID': '',
                        'playerType': 'site'
                    }
                }])
            )
            token_data = json.loads(response)
            
            # Get playlist URL
            playlist_url = (
                f'https://usher.ttvnw.net/api/channel/hls/{channel}.m3u8'
                '?client_id=' + self.twitch_client_id +
                '&token=' + token_data['data']['streamPlaybackAccessToken']['value'] +
                '&sig=' + token_data['data']['streamPlaybackAccessToken']['signature'] +
                '&allow_source=true'
            )
            
            return playlist_url
            
        except Exception as e:
            logger.error(f'Failed to get stream URL: {str(e)}')
            return None
    
    async def start_stream(self, channel: str):
        """Start streaming a channel"""
        try:
            # Stop current stream if any
            await self.stop_stream()
            
            # Get stream URL
            stream_url = await self.get_stream_url(channel)
            if not stream_url:
                self.stream_error.emit('Failed to get stream URL')
                return
            
            # Load HLS playlist
            await self.hls.load_playlist(stream_url)
            self.current_stream = channel
            
            # Start chat connection
            self.chat_task = asyncio.create_task(
                self.connect_chat(channel)
            )
            
            self.stream_started.emit(stream_url)
            
        except Exception as e:
            logger.error(f'Failed to start stream: {str(e)}')
            self.stream_error.emit(str(e))
    
    async def stop_stream(self):
        """Stop current stream"""
        if self.current_stream:
            try:
                # Stop chat connection
                if self.chat_task:
                    self.chat_task.cancel()
                    self.chat_task = None
                
                if self.chat_websocket:
                    await self.chat_websocket.close()
                    self.chat_websocket = None
                
                # Stop HLS stream
                await self.hls.close()
                
                self.current_stream = None
                self.stream_ended.emit()
                
            except Exception as e:
                logger.error(f'Error stopping stream: {str(e)}')
    
    async def connect_chat(self, channel: str):
        """Connect to Twitch chat"""
        try:
            # Connect to chat websocket
            self.chat_websocket = await self.network.websocket_connect(
                'wss://irc-ws.chat.twitch.tv:443'
            )
            
            # Send authentication
            await self.chat_websocket.send(
                f'PASS oauth:{await self.authenticate()}'
            )
            await self.chat_websocket.send(
                f'NICK justinfan{random.randint(10000, 99999)}'
            )
            await self.chat_websocket.send(f'JOIN #{channel}')
            
            # Handle messages
            while True:
                message = await self.chat_websocket.recv()
                if message.startswith('PING'):
                    await self.chat_websocket.send('PONG :tmi.twitch.tv')
                elif 'PRIVMSG' in message:
                    # Parse chat message
                    parts = message.split(':', 2)
                    if len(parts) == 3:
                        user = parts[1].split('!')[0]
                        text = parts[2].strip()
                        
                        self.chat_message.emit({
                            'user': user,
                            'message': text,
                            'channel': channel
                        })
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f'Chat connection error: {str(e)}')
        finally:
            if self.chat_websocket:
                await self.chat_websocket.close()
                self.chat_websocket = None
    
    def add_to_playlist(self, stream_info: Dict) -> bool:
        """Add stream to playlist"""
        try:
            return self.playlist.add_item(
                title=f"{stream_info['username']} - {stream_info['title']}",
                url=f"twitch://{stream_info['username']}",
                metadata={
                    'source': 'twitch',
                    'channel': stream_info['username'],
                    'game': stream_info['game'],
                    'viewers': stream_info['viewers']
                }
            )
        except Exception as e:
            logger.error(f'Failed to add to playlist: {str(e)}')
            return False
