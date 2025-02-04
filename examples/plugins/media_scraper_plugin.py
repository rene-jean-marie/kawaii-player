"""
Example media scraper plugin for Kawaii Player
Supports various media sites using yt-dlp
"""
import os
import re
import json
import logging
import asyncio
from typing import Optional, Dict, List, Any
from PyQt5 import QtCore
import yt_dlp

from kawaii_player import (
    NetworkManager,
    PlaylistManager,
    SettingsManager,
    UnifiedPlayer
)

logger = logging.getLogger(__name__)

class MediaScraperPlugin(QtCore.QObject):
    """Plugin for scraping media from various sites"""
    
    # Signals
    extraction_started = QtCore.pyqtSignal(str)  # url
    extraction_progress = QtCore.pyqtSignal(str, float)  # url, progress
    extraction_complete = QtCore.pyqtSignal(str, dict)  # url, info
    extraction_error = QtCore.pyqtSignal(str, str)  # url, error
    
    def __init__(
        self,
        network: NetworkManager,
        playlist: PlaylistManager,
        settings: SettingsManager,
        player: UnifiedPlayer
    ):
        super().__init__()
        self.network = network
        self.playlist = playlist
        self.settings = settings
        self.player = player
        
        # Configure yt-dlp options
        self.ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
            'ignoreerrors': True,
            'nocheckcertificate': True,
            'prefer_ffmpeg': True,
            'progress_hooks': [self._progress_hook]
        }
        
        # Supported sites (partial list)
        self.supported_sites = {
            'dailymotion.com': 'Dailymotion',
            'vimeo.com': 'Vimeo',
            'nicovideo.jp': 'Niconico',
            'bilibili.com': 'Bilibili',
            'soundcloud.com': 'SoundCloud',
            'instagram.com': 'Instagram',
            'facebook.com': 'Facebook',
            'twitter.com': 'Twitter'
        }
    
    def _progress_hook(self, d: Dict[str, Any]):
        """Handle download progress"""
        if d['status'] == 'downloading':
            try:
                progress = float(d['_percent_str'].replace('%', '')) / 100
                self.extraction_progress.emit(d['filename'], progress)
            except:
                pass
    
    def is_supported_url(self, url: str) -> bool:
        """Check if URL is supported"""
        return any(site in url for site in self.supported_sites)
    
    def get_site_name(self, url: str) -> Optional[str]:
        """Get name of site from URL"""
        for site, name in self.supported_sites.items():
            if site in url:
                return name
        return None
    
    async def extract_info(self, url: str) -> Optional[Dict]:
        """Extract information from URL"""
        self.extraction_started.emit(url)
        
        try:
            # Run yt-dlp in a thread pool
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = await loop.run_in_executor(
                    None,
                    lambda: ydl.extract_info(url, download=False)
                )
            
            if not info:
                raise Exception('No information extracted')
            
            # Format info
            result = {
                'id': info.get('id', ''),
                'title': info.get('title', ''),
                'description': info.get('description', ''),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'webpage_url': info.get('webpage_url', url),
                'uploader': info.get('uploader', ''),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'formats': [],
                'subtitles': {},
                'is_live': info.get('is_live', False),
                'site': self.get_site_name(url) or info.get('extractor', '')
            }
            
            # Get available formats
            for f in info.get('formats', []):
                format_info = {
                    'format_id': f.get('format_id', ''),
                    'url': f.get('url', ''),
                    'ext': f.get('ext', ''),
                    'width': f.get('width', 0),
                    'height': f.get('height', 0),
                    'fps': f.get('fps', 0),
                    'vcodec': f.get('vcodec', ''),
                    'acodec': f.get('acodec', ''),
                    'abr': f.get('abr', 0),
                    'filesize': f.get('filesize', 0)
                }
                result['formats'].append(format_info)
            
            # Get subtitles
            for lang, subs in info.get('subtitles', {}).items():
                result['subtitles'][lang] = [
                    {
                        'url': sub.get('url', ''),
                        'ext': sub.get('ext', '')
                    }
                    for sub in subs
                ]
            
            self.extraction_complete.emit(url, result)
            return result
            
        except Exception as e:
            logger.error(f'Extraction failed for {url}: {str(e)}')
            self.extraction_error.emit(url, str(e))
            return None
    
    async def download_media(
        self,
        url: str,
        format_id: Optional[str] = None
    ) -> Optional[str]:
        """Download media from URL"""
        try:
            # Configure download options
            download_opts = self.ydl_opts.copy()
            download_opts['outtmpl'] = os.path.join(
                self.settings.get(
                    'downloads.download_path',
                    os.path.expanduser('~/Downloads')
                ),
                '%(title)s.%(ext)s'
            )
            
            if format_id:
                download_opts['format'] = format_id
            
            # Download in thread pool
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(download_opts) as ydl:
                info = await loop.run_in_executor(
                    None,
                    lambda: ydl.extract_info(url, download=True)
                )
            
            if not info:
                raise Exception('Download failed')
            
            # Get downloaded file path
            filepath = ydl.prepare_filename(info)
            if not os.path.exists(filepath):
                # Try with different extension
                base, _ = os.path.splitext(filepath)
                for ext in ['.mp4', '.webm', '.mkv']:
                    if os.path.exists(base + ext):
                        filepath = base + ext
                        break
            
            return filepath
            
        except Exception as e:
            logger.error(f'Download failed for {url}: {str(e)}')
            self.extraction_error.emit(url, str(e))
            return None
    
    def add_to_playlist(
        self,
        media_info: Dict,
        playlist_name: Optional[str] = None
    ) -> bool:
        """Add media to playlist"""
        try:
            return self.playlist.add_item(
                title=media_info['title'],
                url=media_info['webpage_url'],
                duration=media_info.get('duration', 0),
                thumbnail=media_info.get('thumbnail'),
                metadata={
                    'source': media_info['site'].lower(),
                    'uploader': media_info.get('uploader'),
                    'view_count': media_info.get('view_count'),
                    'like_count': media_info.get('like_count')
                },
                playlist_name=playlist_name
            )
        except Exception as e:
            logger.error(f'Failed to add to playlist: {str(e)}')
            return False
    
    async def play_url(self, url: str):
        """Play media from URL"""
        try:
            # Extract info first
            info = await self.extract_info(url)
            if not info:
                return False
            
            # For live streams
            if info['is_live']:
                if not info['formats']:
                    return False
                    
                # Get best quality stream URL
                stream_url = info['formats'][-1]['url']
                self.player.load(stream_url)
                return True
            
            # For regular media
            # Download if needed
            download_path = await self.download_media(url)
            if not download_path:
                return False
            
            # Load media
            self.player.load(download_path)
            
            # Load subtitles if available
            preferred_lang = self.settings.get(
                'player.subtitle_language',
                'en'
            )
            if preferred_lang in info['subtitles']:
                sub = info['subtitles'][preferred_lang][0]
                sub_content = await self.network.request(sub['url'])
                
                sub_path = f'/tmp/media_sub_{info["id"]}.{sub["ext"]}'
                with open(sub_path, 'wb') as f:
                    f.write(sub_content)
                
                self.player.load_subtitle(sub_path)
            
            return True
            
        except Exception as e:
            logger.error(f'Failed to play URL: {str(e)}')
            return False
    
    async def extract_playlist(self, url: str) -> Optional[Dict]:
        """Extract playlist information"""
        try:
            # Configure playlist options
            playlist_opts = self.ydl_opts.copy()
            playlist_opts['extract_flat'] = True
            
            # Extract playlist info
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(playlist_opts) as ydl:
                info = await loop.run_in_executor(
                    None,
                    lambda: ydl.extract_info(url, download=False)
                )
            
            if not info:
                raise Exception('No playlist information extracted')
            
            # Format playlist info
            result = {
                'id': info.get('id', ''),
                'title': info.get('title', ''),
                'description': info.get('description', ''),
                'uploader': info.get('uploader', ''),
                'entries': []
            }
            
            # Get entries
            for entry in info.get('entries', []):
                if entry:
                    result['entries'].append({
                        'id': entry.get('id', ''),
                        'title': entry.get('title', ''),
                        'duration': entry.get('duration', 0),
                        'url': entry.get('url', ''),
                        'thumbnail': entry.get('thumbnail', '')
                    })
            
            return result
            
        except Exception as e:
            logger.error(f'Failed to extract playlist: {str(e)}')
            return None
    
    async def import_playlist(
        self,
        url: str,
        playlist_name: Optional[str] = None
    ) -> bool:
        """Import a playlist"""
        try:
            # Extract playlist info
            playlist = await self.extract_playlist(url)
            if not playlist:
                return False
            
            # Create new playlist if needed
            if playlist_name:
                self.playlist.create_playlist(playlist_name)
            else:
                playlist_name = f"Imported: {playlist['title']}"
                self.playlist.create_playlist(playlist_name)
            
            # Add entries
            for entry in playlist['entries']:
                self.playlist.add_item(
                    title=entry['title'],
                    url=entry['url'],
                    duration=entry.get('duration', 0),
                    thumbnail=entry.get('thumbnail'),
                    playlist_name=playlist_name,
                    metadata={
                        'source': self.get_site_name(url) or 'unknown',
                        'playlist_id': playlist['id']
                    }
                )
            
            return True
            
        except Exception as e:
            logger.error(f'Failed to import playlist: {str(e)}')
            return False
