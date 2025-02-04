"""
Unified main window implementation for Kawaii Player
"""
import os
import logging
from typing import Optional
from PyQt5 import QtWidgets, QtCore, QtGui

logger = logging.getLogger(__name__)

class MainWindow(QtWidgets.QMainWindow):
    """Main window implementation using unified components"""
    
    def __init__(
        self,
        media_player,
        network,
        mpris,
        base_dir: str,
        resource_dir: str
    ):
        super().__init__()
        self.media_player = media_player
        self.network = network
        self.mpris = mpris
        self.base_dir = base_dir
        self.resource_dir = resource_dir
        
        # UI components
        self.playlist_widget = None
        self.video_frame = None
        self.controls_widget = None
        self.browser = None
        self.status_bar = None
        
        # Initialize UI
        self.setup_ui()
        self.setup_shortcuts()
        self.setup_signals()
    
    def setup_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('Kawaii Player')
        self.resize(1200, 800)
        
        # Create central widget and layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Create main splitter
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Create playlist widget
        self.playlist_widget = QtWidgets.QWidget()
        playlist_layout = QtWidgets.QVBoxLayout(self.playlist_widget)
        self.playlist = QtWidgets.QListWidget()
        playlist_layout.addWidget(self.playlist)
        splitter.addWidget(self.playlist_widget)
        
        # Create video frame
        self.video_frame = QtWidgets.QFrame()
        self.video_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        splitter.addWidget(self.video_frame)
        
        # Create controls
        self.controls_widget = QtWidgets.QWidget()
        controls_layout = QtWidgets.QHBoxLayout(self.controls_widget)
        
        self.play_button = QtWidgets.QPushButton('Play')
        self.stop_button = QtWidgets.QPushButton('Stop')
        self.prev_button = QtWidgets.QPushButton('Previous')
        self.next_button = QtWidgets.QPushButton('Next')
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        
        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.next_button)
        controls_layout.addWidget(self.volume_slider)
        
        layout.addWidget(self.controls_widget)
        
        # Create status bar
        self.status_bar = self.statusBar()
        
        # Set splitter sizes
        splitter.setSizes([300, 900])  # 300px for playlist, rest for video
    
    def setup_shortcuts(self):
        """Set up keyboard shortcuts"""
        QtWidgets.QShortcut(
            QtGui.QKeySequence("Space"),
            self,
            self.toggle_playback
        )
        QtWidgets.QShortcut(
            QtGui.QKeySequence("F"),
            self,
            self.toggle_fullscreen
        )
        QtWidgets.QShortcut(
            QtGui.QKeySequence("Esc"),
            self,
            self.exit_fullscreen
        )
    
    def setup_signals(self):
        """Connect signals and slots"""
        self.play_button.clicked.connect(self.toggle_playback)
        self.stop_button.clicked.connect(self.stop_playback)
        self.prev_button.clicked.connect(self.play_previous)
        self.next_button.clicked.connect(self.play_next)
        self.volume_slider.valueChanged.connect(self.change_volume)
        self.playlist.itemDoubleClicked.connect(self.playlist_item_activated)
    
    def toggle_playback(self):
        """Toggle between play and pause"""
        if self.media_player.is_playing():
            self.media_player.pause()
            self.play_button.setText('Play')
        else:
            self.media_player.play()
            self.play_button.setText('Pause')
    
    def stop_playback(self):
        """Stop media playback"""
        self.media_player.stop()
        self.play_button.setText('Play')
    
    def play_previous(self):
        """Play previous item in playlist"""
        current_row = self.playlist.currentRow()
        if current_row > 0:
            self.playlist.setCurrentRow(current_row - 1)
            self.playlist_item_activated(self.playlist.currentItem())
    
    def play_next(self):
        """Play next item in playlist"""
        current_row = self.playlist.currentRow()
        if current_row < self.playlist.count() - 1:
            self.playlist.setCurrentRow(current_row + 1)
            self.playlist_item_activated(self.playlist.currentItem())
    
    def change_volume(self, value):
        """Change playback volume"""
        self.media_player.set_volume(value)
    
    def playlist_item_activated(self, item):
        """Handle playlist item activation"""
        if not item:
            return
        
        url = item.data(QtCore.Qt.UserRole)
        if not url:
            return
            
        self.play_media(url)
    
    def play_media(self, url):
        """Play media from URL"""
        self.media_player.load(url)
        self.media_player.play()
        self.play_button.setText('Pause')
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def exit_fullscreen(self):
        """Exit fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.media_player.stop()
        event.accept()
