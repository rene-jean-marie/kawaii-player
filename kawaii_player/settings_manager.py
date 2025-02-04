"""
Unified settings manager for Kawaii Player
"""
import os
import json
import logging
from typing import Any, Dict, Optional, List
from PyQt5 import QtCore

logger = logging.getLogger(__name__)

class SettingsManager(QtCore.QObject):
    """Manages application settings and configuration"""
    
    # Signals
    settings_changed = QtCore.pyqtSignal(str, object)  # key, value
    
    def __init__(self, config_dir: str):
        super().__init__()
        self.config_dir = config_dir
        self.settings_file = os.path.join(config_dir, 'settings.json')
        
        # Default settings
        self.defaults = {
            'player': {
                'volume': 100,
                'remember_position': True,
                'remember_playlist': True,
                'autoplay': False,
                'repeat_mode': 'off',  # off, one, all
                'video_output': 'opengl',
                'audio_output': 'auto',
                'hardware_decoding': True,
                'subtitle_font': 'Sans',
                'subtitle_size': 40,
                'subtitle_color': '#FFFFFF',
                'subtitle_outline': True
            },
            'interface': {
                'theme': 'system',  # system, light, dark
                'language': 'en',
                'show_playlist': True,
                'show_controls': True,
                'show_status_bar': True,
                'thumbnail_size': 200,
                'window_size': [1200, 800],
                'window_position': None
            },
            'network': {
                'proxy_enabled': False,
                'proxy_type': 'http',  # http, socks5
                'proxy_host': '',
                'proxy_port': 8080,
                'user_agent': 'Kawaii-Player/6.0.0',
                'connection_timeout': 30,
                'max_retries': 3
            },
            'downloads': {
                'download_path': os.path.expanduser('~/Downloads'),
                'organize_by_type': True,
                'max_concurrent': 3,
                'auto_convert': False,
                'preferred_format': 'mp4'
            },
            'shortcuts': {
                'play_pause': 'Space',
                'stop': 'S',
                'next': 'N',
                'previous': 'P',
                'fullscreen': 'F',
                'mute': 'M',
                'volume_up': 'Up',
                'volume_down': 'Down'
            }
        }
        
        # Current settings
        self.settings = self.defaults.copy()
        
        # Load saved settings
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self._merge_settings(saved)
            except Exception as e:
                logger.error(f'Error loading settings: {str(e)}')
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            logger.error(f'Error saving settings: {str(e)}')
    
    def _merge_settings(self, saved: Dict[str, Any]):
        """Merge saved settings with defaults"""
        for category, values in saved.items():
            if category in self.settings:
                if isinstance(values, dict):
                    self.settings[category].update(values)
                else:
                    self.settings[category] = values
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value
        Args:
            key: Dot-separated path to setting (e.g. 'player.volume')
            default: Default value if setting doesn't exist
        """
        try:
            parts = key.split('.')
            value = self.settings
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """
        Set a setting value
        Args:
            key: Dot-separated path to setting (e.g. 'player.volume')
            value: Value to set
        """
        try:
            parts = key.split('.')
            target = self.settings
            for part in parts[:-1]:
                target = target[part]
            target[parts[-1]] = value
            self.settings_changed.emit(key, value)
            self.save_settings()
        except (KeyError, TypeError) as e:
            logger.error(f'Error setting {key}: {str(e)}')
    
    def reset(self, key: Optional[str] = None):
        """
        Reset settings to defaults
        Args:
            key: Optional dot-separated path to reset specific setting
        """
        if key is None:
            self.settings = self.defaults.copy()
            self.settings_changed.emit('', None)
        else:
            try:
                parts = key.split('.')
                default_value = self.defaults
                for part in parts:
                    default_value = default_value[part]
                self.set(key, default_value)
            except (KeyError, TypeError) as e:
                logger.error(f'Error resetting {key}: {str(e)}')
        
        self.save_settings()
    
    def get_categories(self) -> List[str]:
        """Get list of setting categories"""
        return list(self.settings.keys())
    
    def get_category(self, category: str) -> Dict[str, Any]:
        """Get all settings in a category"""
        return self.settings.get(category, {}).copy()
    
    def set_category(self, category: str, values: Dict[str, Any]):
        """Set all settings in a category"""
        if category in self.settings:
            self.settings[category].update(values)
            for key, value in values.items():
                self.settings_changed.emit(f'{category}.{key}', value)
            self.save_settings()
    
    def reset_category(self, category: str):
        """Reset all settings in a category to defaults"""
        if category in self.defaults:
            self.settings[category] = self.defaults[category].copy()
            self.settings_changed.emit(category, None)
            self.save_settings()
    
    def export_settings(self, path: str) -> bool:
        """Export settings to a file"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            logger.error(f'Error exporting settings: {str(e)}')
            return False
    
    def import_settings(self, path: str) -> bool:
        """Import settings from a file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                self._merge_settings(saved)
                self.settings_changed.emit('', None)
                self.save_settings()
            return True
        except Exception as e:
            logger.error(f'Error importing settings: {str(e)}')
            return False
