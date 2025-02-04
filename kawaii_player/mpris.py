"""
Unified MPRIS service supporting both DBus and non-DBus environments
"""
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

try:
    import dbus
    import dbus.service
    from dbus.mainloop.pyqt5 import DBusQtMainLoop
    HAS_DBUS = True
except ImportError:
    HAS_DBUS = False

class MPRISInterface:
    """MPRIS interface that works with or without DBus"""
    
    MPRIS_INTERFACE = 'org.mpris.MediaPlayer2'
    MPRIS_PLAYER_INTERFACE = 'org.mpris.MediaPlayer2.Player'
    
    def __init__(self, name: str = 'kawaii-player'):
        self.name = name
        self._service = None
        self._player = None
        self.metadata = {}
        self.playback_status = 'Stopped'
        
        if HAS_DBUS:
            self._setup_dbus()
    
    def _setup_dbus(self):
        """Initialize DBus service if available"""
        try:
            DBusQtMainLoop(set_as_default=True)
            session_bus = dbus.SessionBus()
            bus_name = dbus.service.BusName(
                f'org.mpris.MediaPlayer2.{self.name}',
                session_bus
            )
            
            class MPRISInterface(dbus.service.Object):
                def __init__(self, bus_name):
                    dbus.service.Object.__init__(
                        self,
                        bus_name,
                        '/org/mpris/MediaPlayer2'
                    )
                
                @dbus.service.method(MPRIS_INTERFACE)
                def Raise(self):
                    pass
                
                @dbus.service.method(MPRIS_INTERFACE)
                def Quit(self):
                    pass
            
            class MPRISPlayerInterface(dbus.service.Object):
                def __init__(self, bus_name):
                    dbus.service.Object.__init__(
                        self,
                        bus_name,
                        '/org/mpris/MediaPlayer2'
                    )
                
                @dbus.service.method(MPRIS_PLAYER_INTERFACE)
                def Play(self):
                    pass
                
                @dbus.service.method(MPRIS_PLAYER_INTERFACE)
                def Pause(self):
                    pass
                
                @dbus.service.method(MPRIS_PLAYER_INTERFACE)
                def PlayPause(self):
                    pass
                
                @dbus.service.method(MPRIS_PLAYER_INTERFACE)
                def Stop(self):
                    pass
                
                @dbus.service.method(MPRIS_PLAYER_INTERFACE)
                def Next(self):
                    pass
                
                @dbus.service.method(MPRIS_PLAYER_INTERFACE)
                def Previous(self):
                    pass
            
            self._service = MPRISInterface(bus_name)
            self._player = MPRISPlayerInterface(bus_name)
            logger.info('MPRIS DBus service initialized')
        except Exception as e:
            logger.error(f'Failed to initialize MPRIS DBus service: {str(e)}')
            self._service = None
            self._player = None
    
    def update_metadata(self, metadata: Dict[str, Any]):
        """Update metadata for current media"""
        self.metadata = metadata
        if HAS_DBUS and self._player:
            self._player.PropertiesChanged(
                self.MPRIS_PLAYER_INTERFACE,
                {'Metadata': dbus.Dictionary(metadata, signature='sv')},
                []
            )
    
    def update_playback_status(self, status: str):
        """Update playback status"""
        self.playback_status = status
        if HAS_DBUS and self._player:
            self._player.PropertiesChanged(
                self.MPRIS_PLAYER_INTERFACE,
                {'PlaybackStatus': status},
                []
            )
    
    def play(self):
        """Start playback"""
        if HAS_DBUS and self._player:
            self._player.Play()
        self.update_playback_status('Playing')
    
    def pause(self):
        """Pause playback"""
        if HAS_DBUS and self._player:
            self._player.Pause()
        self.update_playback_status('Paused')
    
    def stop(self):
        """Stop playback"""
        if HAS_DBUS and self._player:
            self._player.Stop()
        self.update_playback_status('Stopped')
    
    def next(self):
        """Play next track"""
        if HAS_DBUS and self._player:
            self._player.Next()
    
    def previous(self):
        """Play previous track"""
        if HAS_DBUS and self._player:
            self._player.Previous()
