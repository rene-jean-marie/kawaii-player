"""
Example media library plugin for Kawaii Player
Integrates with local media and TMDb for metadata
"""
import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, List, Set
from PyQt5 import QtCore
from pathlib import Path

from kawaii_player import (
    NetworkManager,
    PlaylistManager,
    SettingsManager,
    UnifiedPlayer
)

logger = logging.getLogger(__name__)

class MediaLibraryPlugin(QtCore.QObject):
    """Plugin for managing local media libraries with metadata"""
    
    # Signals
    library_scanned = QtCore.pyqtSignal(dict)  # library stats
    media_found = QtCore.pyqtSignal(dict)  # media info
    metadata_updated = QtCore.pyqtSignal(str, dict)  # path, metadata
    
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
        
        # Get TMDb API key
        self.tmdb_key = settings.get('plugins.library.tmdb_key', '')
        self.tmdb_base = 'https://api.themoviedb.org/3'
        
        # Configure library paths
        self.library_paths = settings.get('plugins.library.paths', [])
        
        # Media types and extensions
        self.video_extensions = {
            '.mp4', '.mkv', '.avi', '.mov',
            '.wmv', '.flv', '.webm', '.m4v'
        }
        self.audio_extensions = {
            '.mp3', '.wav', '.flac', '.m4a',
            '.ogg', '.aac', '.wma'
        }
        
        # Cache for metadata
        self.metadata_cache: Dict[str, Dict] = {}
        self.cache_file = os.path.join(
            settings.config_dir,
            'media_library_cache.json'
        )
        
        # Load cache
        self._load_cache()
    
    def _load_cache(self):
        """Load metadata cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    self.metadata_cache = json.load(f)
        except Exception as e:
            logger.error(f'Failed to load cache: {str(e)}')
    
    def _save_cache(self):
        """Save metadata cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.metadata_cache, f, indent=2)
        except Exception as e:
            logger.error(f'Failed to save cache: {str(e)}')
    
    def is_media_file(self, path: str) -> bool:
        """Check if file is a media file"""
        ext = os.path.splitext(path)[1].lower()
        return ext in self.video_extensions or ext in self.audio_extensions
    
    def get_media_type(self, path: str) -> Optional[str]:
        """Get media type from file extension"""
        ext = os.path.splitext(path)[1].lower()
        if ext in self.video_extensions:
            return 'video'
        elif ext in self.audio_extensions:
            return 'audio'
        return None
    
    async def scan_library(
        self,
        paths: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """Scan library paths for media files"""
        if paths is None:
            paths = self.library_paths
        
        stats = {
            'total_files': 0,
            'videos': 0,
            'audio': 0,
            'with_metadata': 0,
            'missing_metadata': 0
        }
        
        try:
            for base_path in paths:
                for root, _, files in os.walk(base_path):
                    for file in files:
                        path = os.path.join(root, file)
                        if self.is_media_file(path):
                            stats['total_files'] += 1
                            
                            media_type = self.get_media_type(path)
                            if media_type == 'video':
                                stats['videos'] += 1
                            elif media_type == 'audio':
                                stats['audio'] += 1
                            
                            # Check metadata
                            rel_path = os.path.relpath(path, base_path)
                            if rel_path in self.metadata_cache:
                                stats['with_metadata'] += 1
                            else:
                                stats['missing_metadata'] += 1
                                
                                # Try to get metadata
                                await self.fetch_metadata(path)
            
            self.library_scanned.emit(stats)
            return stats
            
        except Exception as e:
            logger.error(f'Library scan failed: {str(e)}')
            return stats
    
    async def fetch_metadata(self, path: str) -> Optional[Dict]:
        """Fetch metadata for media file"""
        if not self.tmdb_key:
            logger.error('TMDb API key not set')
            return None
            
        try:
            # Get filename without extension
            name = os.path.splitext(os.path.basename(path))[0]
            
            # Clean up name
            name = name.replace('.', ' ').replace('_', ' ')
            
            # Search TMDb
            url = (
                f'{self.tmdb_base}/search/multi'
                f'?api_key={self.tmdb_key}'
                f'&query={name}'
                '&include_adult=false'
            )
            
            response = await self.network.request(url)
            data = json.loads(response)
            
            if not data.get('results'):
                return None
            
            # Get first result
            result = data['results'][0]
            
            # Get detailed info
            media_type = result['media_type']
            media_id = result['id']
            
            url = (
                f'{self.tmdb_base}/{media_type}/{media_id}'
                f'?api_key={self.tmdb_key}'
                '&append_to_response=credits,keywords'
            )
            
            response = await self.network.request(url)
            details = json.loads(response)
            
            # Format metadata
            metadata = {
                'id': details['id'],
                'title': details.get('title') or details.get('name', ''),
                'original_title': (
                    details.get('original_title') or
                    details.get('original_name', '')
                ),
                'overview': details.get('overview', ''),
                'poster_path': details.get('poster_path'),
                'backdrop_path': details.get('backdrop_path'),
                'release_date': (
                    details.get('release_date') or
                    details.get('first_air_date', '')
                ),
                'genres': [g['name'] for g in details.get('genres', [])],
                'vote_average': details.get('vote_average', 0),
                'media_type': media_type,
                'last_updated': datetime.now().isoformat()
            }
            
            # Add cast and crew
            if 'credits' in details:
                metadata['cast'] = [
                    {
                        'name': c['name'],
                        'character': c.get('character', ''),
                        'profile_path': c.get('profile_path')
                    }
                    for c in details['credits'].get('cast', [])[:10]
                ]
                
                metadata['crew'] = [
                    {
                        'name': c['name'],
                        'job': c['job'],
                        'profile_path': c.get('profile_path')
                    }
                    for c in details['credits'].get('crew', [])
                    if c['job'] in ['Director', 'Writer']
                ]
            
            # Add keywords
            if 'keywords' in details:
                keywords = (
                    details['keywords'].get('keywords') or
                    details['keywords'].get('results', [])
                )
                metadata['keywords'] = [
                    k['name'] for k in keywords
                ]
            
            # Cache metadata
            rel_path = os.path.relpath(
                path,
                self.settings.get('plugins.library.paths', [''])[0]
            )
            self.metadata_cache[rel_path] = metadata
            self._save_cache()
            
            self.metadata_updated.emit(path, metadata)
            return metadata
            
        except Exception as e:
            logger.error(f'Failed to fetch metadata: {str(e)}')
            return None
    
    def get_metadata(self, path: str) -> Optional[Dict]:
        """Get cached metadata for media file"""
        try:
            rel_path = os.path.relpath(
                path,
                self.settings.get('plugins.library.paths', [''])[0]
            )
            return self.metadata_cache.get(rel_path)
        except Exception as e:
            logger.error(f'Failed to get metadata: {str(e)}')
            return None
    
    async def organize_library(
        self,
        target_dir: Optional[str] = None
    ) -> Dict[str, int]:
        """Organize media files by metadata"""
        if target_dir is None:
            target_dir = self.library_paths[0]
        
        stats = {
            'organized': 0,
            'skipped': 0,
            'failed': 0
        }
        
        try:
            for path in self.metadata_cache:
                full_path = os.path.join(
                    self.library_paths[0],
                    path
                )
                
                if not os.path.exists(full_path):
                    continue
                
                metadata = self.metadata_cache[path]
                if not metadata:
                    stats['skipped'] += 1
                    continue
                
                try:
                    # Create directory structure
                    media_type = metadata['media_type']
                    year = metadata['release_date'][:4]
                    title = metadata['title']
                    
                    new_dir = os.path.join(
                        target_dir,
                        media_type,
                        f'{title} ({year})'
                    )
                    os.makedirs(new_dir, exist_ok=True)
                    
                    # Move file
                    new_path = os.path.join(
                        new_dir,
                        os.path.basename(path)
                    )
                    os.rename(full_path, new_path)
                    
                    # Update cache
                    new_rel_path = os.path.relpath(new_path, target_dir)
                    self.metadata_cache[new_rel_path] = metadata
                    del self.metadata_cache[path]
                    
                    stats['organized'] += 1
                    
                except Exception as e:
                    logger.error(f'Failed to organize {path}: {str(e)}')
                    stats['failed'] += 1
            
            self._save_cache()
            return stats
            
        except Exception as e:
            logger.error(f'Library organization failed: {str(e)}')
            return stats
    
    def add_to_playlist(
        self,
        path: str,
        playlist_name: Optional[str] = None
    ) -> bool:
        """Add media file to playlist"""
        try:
            metadata = self.get_metadata(path)
            title = os.path.basename(path)
            
            if metadata:
                title = metadata['title']
            
            return self.playlist.add_item(
                title=title,
                url=f'file://{path}',
                metadata={
                    'source': 'local',
                    'type': self.get_media_type(path),
                    'metadata': metadata
                } if metadata else None,
                playlist_name=playlist_name
            )
        except Exception as e:
            logger.error(f'Failed to add to playlist: {str(e)}')
            return False
    
    async def search_library(
        self,
        query: str,
        media_type: Optional[str] = None
    ) -> List[Dict]:
        """Search library using metadata"""
        results = []
        
        try:
            for path, metadata in self.metadata_cache.items():
                if media_type and metadata['media_type'] != media_type:
                    continue
                
                # Search in various fields
                searchable_text = ' '.join([
                    metadata['title'],
                    metadata['original_title'],
                    metadata['overview'],
                    *metadata['genres'],
                    *metadata.get('keywords', []),
                    *[p['name'] for p in metadata.get('cast', [])],
                    *[p['name'] for p in metadata.get('crew', [])]
                ]).lower()
                
                if query.lower() in searchable_text:
                    results.append({
                        'path': os.path.join(self.library_paths[0], path),
                        'metadata': metadata
                    })
            
            return sorted(
                results,
                key=lambda x: x['metadata']['vote_average'],
                reverse=True
            )
            
        except Exception as e:
            logger.error(f'Library search failed: {str(e)}')
            return []
    
    def get_library_stats(self) -> Dict[str, Any]:
        """Get library statistics"""
        stats = {
            'total_files': len(self.metadata_cache),
            'by_type': {},
            'by_genre': {},
            'by_year': {},
            'total_duration': 0,
            'avg_rating': 0
        }
        
        try:
            ratings = []
            
            for metadata in self.metadata_cache.values():
                # Count by type
                media_type = metadata['media_type']
                stats['by_type'][media_type] = (
                    stats['by_type'].get(media_type, 0) + 1
                )
                
                # Count by genre
                for genre in metadata['genres']:
                    stats['by_genre'][genre] = (
                        stats['by_genre'].get(genre, 0) + 1
                    )
                
                # Count by year
                year = metadata['release_date'][:4]
                stats['by_year'][year] = (
                    stats['by_year'].get(year, 0) + 1
                )
                
                # Track ratings
                if metadata['vote_average']:
                    ratings.append(metadata['vote_average'])
            
            # Calculate average rating
            if ratings:
                stats['avg_rating'] = sum(ratings) / len(ratings)
            
            return stats
            
        except Exception as e:
            logger.error(f'Failed to get library stats: {str(e)}')
            return stats
