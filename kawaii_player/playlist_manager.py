"""
Unified playlist manager for Kawaii Player
"""
import os
import json
import logging
from typing import List, Dict, Optional, Any
from PyQt5 import QtCore

logger = logging.getLogger(__name__)

class PlaylistItem:
    """Represents a single item in a playlist"""
    
    def __init__(
        self,
        title: str,
        url: str,
        duration: Optional[float] = None,
        thumbnail: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.title = title
        self.url = url
        self.duration = duration
        self.thumbnail = thumbnail
        self.metadata = metadata or {}
        self.played = False
        self.favorite = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary for serialization"""
        return {
            'title': self.title,
            'url': self.url,
            'duration': self.duration,
            'thumbnail': self.thumbnail,
            'metadata': self.metadata,
            'played': self.played,
            'favorite': self.favorite
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlaylistItem':
        """Create item from dictionary"""
        item = cls(
            title=data['title'],
            url=data['url'],
            duration=data.get('duration'),
            thumbnail=data.get('thumbnail'),
            metadata=data.get('metadata', {})
        )
        item.played = data.get('played', False)
        item.favorite = data.get('favorite', False)
        return item

class PlaylistManager(QtCore.QObject):
    """Manages playlists and playlist items"""
    
    # Signals
    playlist_changed = QtCore.pyqtSignal(str)  # playlist_name
    item_added = QtCore.pyqtSignal(str, int)  # playlist_name, index
    item_removed = QtCore.pyqtSignal(str, int)  # playlist_name, index
    item_moved = QtCore.pyqtSignal(str, int, int)  # playlist_name, old_index, new_index
    
    def __init__(self, config_dir: str):
        super().__init__()
        self.config_dir = config_dir
        self.playlists: Dict[str, List[PlaylistItem]] = {}
        self.active_playlist = 'default'
        
        # Create default playlist
        self.playlists['default'] = []
        
        # Load saved playlists
        self.load_playlists()
    
    def get_playlist_path(self, name: str) -> str:
        """Get filesystem path for playlist"""
        return os.path.join(self.config_dir, f'{name}.playlist')
    
    def load_playlists(self):
        """Load all saved playlists"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            return
            
        for file in os.listdir(self.config_dir):
            if file.endswith('.playlist'):
                name = file[:-9]  # Remove .playlist extension
                try:
                    self.load_playlist(name)
                except Exception as e:
                    logger.error(f'Failed to load playlist {name}: {str(e)}')
    
    def load_playlist(self, name: str):
        """Load a specific playlist from file"""
        path = self.get_playlist_path(name)
        if not os.path.exists(path):
            self.playlists[name] = []
            return
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.playlists[name] = [
                    PlaylistItem.from_dict(item) for item in data
                ]
        except Exception as e:
            logger.error(f'Error loading playlist {name}: {str(e)}')
            self.playlists[name] = []
    
    def save_playlist(self, name: str):
        """Save a specific playlist to file"""
        if name not in self.playlists:
            return
            
        path = self.get_playlist_path(name)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(
                    [item.to_dict() for item in self.playlists[name]],
                    f,
                    indent=2
                )
        except Exception as e:
            logger.error(f'Error saving playlist {name}: {str(e)}')
    
    def create_playlist(self, name: str) -> bool:
        """Create a new playlist"""
        if name in self.playlists:
            return False
            
        self.playlists[name] = []
        self.save_playlist(name)
        self.playlist_changed.emit(name)
        return True
    
    def delete_playlist(self, name: str) -> bool:
        """Delete a playlist"""
        if name == 'default' or name not in self.playlists:
            return False
            
        path = self.get_playlist_path(name)
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                logger.error(f'Error deleting playlist file {name}: {str(e)}')
                return False
                
        del self.playlists[name]
        if self.active_playlist == name:
            self.active_playlist = 'default'
            
        self.playlist_changed.emit(name)
        return True
    
    def add_item(
        self,
        title: str,
        url: str,
        playlist_name: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Add an item to a playlist"""
        name = playlist_name or self.active_playlist
        if name not in self.playlists:
            return False
            
        item = PlaylistItem(title, url, **kwargs)
        self.playlists[name].append(item)
        self.save_playlist(name)
        
        index = len(self.playlists[name]) - 1
        self.item_added.emit(name, index)
        return True
    
    def remove_item(
        self,
        index: int,
        playlist_name: Optional[str] = None
    ) -> bool:
        """Remove an item from a playlist"""
        name = playlist_name or self.active_playlist
        if name not in self.playlists:
            return False
            
        if 0 <= index < len(self.playlists[name]):
            self.playlists[name].pop(index)
            self.save_playlist(name)
            self.item_removed.emit(name, index)
            return True
        return False
    
    def move_item(
        self,
        old_index: int,
        new_index: int,
        playlist_name: Optional[str] = None
    ) -> bool:
        """Move an item within a playlist"""
        name = playlist_name or self.active_playlist
        if name not in self.playlists:
            return False
            
        if (0 <= old_index < len(self.playlists[name]) and
            0 <= new_index < len(self.playlists[name])):
            item = self.playlists[name].pop(old_index)
            self.playlists[name].insert(new_index, item)
            self.save_playlist(name)
            self.item_moved.emit(name, old_index, new_index)
            return True
        return False
    
    def get_item(
        self,
        index: int,
        playlist_name: Optional[str] = None
    ) -> Optional[PlaylistItem]:
        """Get an item from a playlist"""
        name = playlist_name or self.active_playlist
        if name not in self.playlists:
            return None
            
        if 0 <= index < len(self.playlists[name]):
            return self.playlists[name][index]
        return None
    
    def get_items(
        self,
        playlist_name: Optional[str] = None
    ) -> List[PlaylistItem]:
        """Get all items in a playlist"""
        name = playlist_name or self.active_playlist
        return self.playlists.get(name, [])[:]
    
    def clear_playlist(self, playlist_name: Optional[str] = None):
        """Clear all items from a playlist"""
        name = playlist_name or self.active_playlist
        if name in self.playlists:
            self.playlists[name] = []
            self.save_playlist(name)
            self.playlist_changed.emit(name)
    
    def set_active_playlist(self, name: str) -> bool:
        """Set the active playlist"""
        if name in self.playlists:
            self.active_playlist = name
            self.playlist_changed.emit(name)
            return True
        return False
    
    def get_active_playlist(self) -> str:
        """Get the name of the active playlist"""
        return self.active_playlist
    
    def get_playlist_names(self) -> List[str]:
        """Get names of all playlists"""
        return list(self.playlists.keys())
