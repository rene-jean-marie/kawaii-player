"""
Main entry point for Kawaii Player application with unified components
"""
import os
import sys
import logging
import asyncio
from PyQt5 import QtWidgets, QtCore

from .browser_unified import BrowserPage
from .network import NetworkManager
from .mpris import MPRISInterface
from .hls import HLSStream
from .unified_player import UnifiedPlayer
from .unified_window import MainWindow
from .playlist_manager import PlaylistManager
from .settings_manager import SettingsManager

logger = logging.getLogger(__name__)

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def get_base_dir():
    """Get the base directory of the application"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

def get_config_dir():
    """Get the configuration directory"""
    if sys.platform == 'win32':
        config_dir = os.path.join(os.environ['APPDATA'], 'kawaii-player')
    else:
        config_dir = os.path.join(
            os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')),
            'kawaii-player'
        )
    return config_dir

class KawaiiPlayer:
    """Main application class using unified components"""
    
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.base_dir = get_base_dir()
        self.config_dir = get_config_dir()
        self.resource_dir = os.path.join(self.base_dir, 'resources')
        self.tmp_dir = os.path.join(self.config_dir, 'tmp')
        
        # Initialize components
        self.settings = SettingsManager(self.config_dir)
        self.network = NetworkManager()
        self.mpris = MPRISInterface()
        self.player = UnifiedPlayer(tmp_dir=self.tmp_dir)
        self.playlist = PlaylistManager(
            os.path.join(self.config_dir, 'playlists')
        )
        self.browser = None
        self.hls = None
        
        # Create main window
        self.window = MainWindow(
            player=self.player,
            network=self.network,
            mpris=self.mpris,
            playlist=self.playlist,
            settings=self.settings,
            base_dir=self.base_dir,
            resource_dir=self.resource_dir
        )
        
        # Apply saved settings
        self._apply_settings()
        
        # Connect signals
        self._connect_signals()
    
    def _apply_settings(self):
        """Apply saved settings"""
        # Window geometry
        size = self.settings.get('interface.window_size', [1200, 800])
        pos = self.settings.get('interface.window_position')
        if pos:
            self.window.move(*pos)
        self.window.resize(*size)
        
        # Player settings
        self.player.set_volume(self.settings.get('player.volume', 100))
        
        # Theme
        theme = self.settings.get('interface.theme', 'system')
        if theme != 'system':
            self.app.setStyle(theme)
    
    def _connect_signals(self):
        """Connect component signals"""
        # Window signals
        self.window.closing.connect(self._save_window_state)
        
        # Player signals
        self.player.playback_started.connect(
            lambda: self.mpris.update_playback_status('Playing')
        )
        self.player.playback_paused.connect(
            lambda: self.mpris.update_playback_status('Paused')
        )
        self.player.playback_stopped.connect(
            lambda: self.mpris.update_playback_status('Stopped')
        )
        
        # Settings signals
        self.settings.settings_changed.connect(self._handle_settings_change)
    
    def _save_window_state(self):
        """Save window state before closing"""
        self.settings.set('interface.window_size', [
            self.window.width(),
            self.window.height()
        ])
        self.settings.set('interface.window_position', [
            self.window.x(),
            self.window.y()
        ])
    
    def _handle_settings_change(self, key: str, value: any):
        """Handle settings changes"""
        if key == 'player.volume':
            self.player.set_volume(value)
        elif key == 'interface.theme':
            if value != 'system':
                self.app.setStyle(value)
    
    def setup_browser(self):
        """Initialize browser component when needed"""
        if not self.browser:
            self.browser = BrowserPage(
                parent=self.window,
                ui=self.window,
                home=self.base_dir,
                tmp=self.tmp_dir
            )
    
    def setup_hls(self):
        """Initialize HLS component when needed"""
        if not self.hls:
            self.hls = HLSStream()
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.tmp_dir, exist_ok=True)
        os.makedirs(os.path.join(self.config_dir, 'playlists'), exist_ok=True)
    
    def run(self):
        """Run the application"""
        try:
            self.ensure_directories()
            
            # Show window
            if self.settings.get('player.remember_playlist', True):
                self.playlist.load_playlists()
            
            self.window.show()
            
            # Start playback if autoplay is enabled
            if self.settings.get('player.autoplay', False):
                items = self.playlist.get_items()
                if items:
                    self.player.load(items[0].url)
                    self.player.play()
            
            return self.app.exec_()
            
        except Exception as e:
            logger.error(f'Application error: {str(e)}')
            return 1
            
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self._save_window_state()
        
        if self.hls:
            asyncio.run(self.hls.close())
        if self.network:
            asyncio.run(self.network.close())

def main():
    """Application entry point"""
    setup_logging()
    app = KawaiiPlayer()
    sys.exit(app.run())

if __name__ == '__main__':
    main()
