"""
Unified player implementation that wraps existing player functionality
"""
import os
import logging
from typing import Optional, Dict, Any
from PyQt5 import QtCore, QtWidgets

from .player import PlayerWidget

logger = logging.getLogger(__name__)

class UnifiedPlayer(QtCore.QObject):
    """
    Unified player implementation that provides a clean interface
    to the underlying player functionality
    """
    
    # Signals
    playback_started = QtCore.pyqtSignal()
    playback_paused = QtCore.pyqtSignal()
    playback_stopped = QtCore.pyqtSignal()
    position_changed = QtCore.pyqtSignal(float)  # 0-1 range
    duration_changed = QtCore.pyqtSignal(float)  # in seconds
    volume_changed = QtCore.pyqtSignal(int)  # 0-100 range
    
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None,
        tmp_dir: Optional[str] = None
    ):
        super().__init__(parent)
        self._player = PlayerWidget(parent, tmp=tmp_dir)
        self._is_playing = False
        self._volume = 100
        self._duration = 0
        self._position = 0
        
        # Connect internal signals
        self._setup_signals()
    
    def _setup_signals(self):
        """Setup internal signal connections"""
        if hasattr(self._player, 'mpvplayer'):
            # Connect MPV player signals if available
            self._player.mpvplayer.positionChanged.connect(self._on_position_changed)
            self._player.mpvplayer.durationChanged.connect(self._on_duration_changed)
            self._player.mpvplayer.playbackStateChanged.connect(self._on_state_changed)
    
    def _on_position_changed(self, position: float):
        """Handle position changes"""
        self._position = position
        if self._duration > 0:
            normalized_pos = position / self._duration
            self.position_changed.emit(normalized_pos)
    
    def _on_duration_changed(self, duration: float):
        """Handle duration changes"""
        self._duration = duration
        self.duration_changed.emit(duration)
    
    def _on_state_changed(self, state: str):
        """Handle playback state changes"""
        if state == 'playing':
            self._is_playing = True
            self.playback_started.emit()
        elif state == 'paused':
            self._is_playing = False
            self.playback_paused.emit()
        elif state == 'stopped':
            self._is_playing = False
            self.playback_stopped.emit()
    
    def get_video_widget(self) -> QtWidgets.QWidget:
        """Get the video widget for embedding in UI"""
        return self._player
    
    def load(self, url: str):
        """Load media from URL"""
        if hasattr(self._player, 'mpvplayer'):
            self._player.mpvplayer.command('loadfile', url)
    
    def play(self):
        """Start or resume playback"""
        if hasattr(self._player, 'mpvplayer'):
            if not self._is_playing:
                self._player.mpvplayer.command('set', 'pause', 'no')
                self._is_playing = True
                self.playback_started.emit()
    
    def pause(self):
        """Pause playback"""
        if hasattr(self._player, 'mpvplayer'):
            if self._is_playing:
                self._player.mpvplayer.command('set', 'pause', 'yes')
                self._is_playing = False
                self.playback_paused.emit()
    
    def stop(self):
        """Stop playback"""
        if hasattr(self._player, 'mpvplayer'):
            self._player.mpvplayer.command('stop')
            self._is_playing = False
            self.playback_stopped.emit()
    
    def seek(self, position: float):
        """
        Seek to position
        Args:
            position: Float between 0-1 representing position in media
        """
        if hasattr(self._player, 'mpvplayer') and self._duration > 0:
            absolute_pos = position * self._duration
            self._player.mpvplayer.command('seek', str(absolute_pos), 'absolute')
    
    def set_volume(self, volume: int):
        """
        Set volume level
        Args:
            volume: Integer between 0-100
        """
        if hasattr(self._player, 'mpvplayer'):
            self._volume = max(0, min(100, volume))
            self._player.mpvplayer.command('set', 'volume', str(self._volume))
            self.volume_changed.emit(self._volume)
    
    def is_playing(self) -> bool:
        """Check if media is currently playing"""
        return self._is_playing
    
    def get_position(self) -> float:
        """Get current position (0-1 range)"""
        if self._duration > 0:
            return self._position / self._duration
        return 0
    
    def get_duration(self) -> float:
        """Get media duration in seconds"""
        return self._duration
    
    def get_volume(self) -> int:
        """Get current volume (0-100 range)"""
        return self._volume
    
    def set_aspect_ratio(self, ratio: str):
        """Set video aspect ratio"""
        if hasattr(self._player, 'mpvplayer'):
            self._player.mpvplayer.command('set', 'video-aspect', ratio)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if hasattr(self._player, 'mpvplayer'):
            self._player.mpvplayer.command('cycle', 'fullscreen')
    
    def set_subtitle_track(self, track_id: int):
        """Set subtitle track"""
        if hasattr(self._player, 'mpvplayer'):
            self._player.mpvplayer.command('set', 'sid', str(track_id))
    
    def set_audio_track(self, track_id: int):
        """Set audio track"""
        if hasattr(self._player, 'mpvplayer'):
            self._player.mpvplayer.command('set', 'aid', str(track_id))
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get media metadata"""
        if hasattr(self._player, 'mpvplayer'):
            return self._player.mpvplayer.get_property('metadata') or {}
        return {}
