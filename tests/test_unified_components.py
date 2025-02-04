"""
Unit tests for unified Kawaii Player components
"""
import os
import sys
import asyncio
import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kawaii_player import (
    BrowserPage,
    NetworkManager,
    MPRISInterface,
    HLSStream,
    MainWindow
)

class TestBrowserPage(unittest.TestCase):
    """Test the unified browser implementation"""
    
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])
    
    def setUp(self):
        self.browser = BrowserPage()
    
    def test_load_url(self):
        """Test URL loading"""
        url = 'https://example.com'
        self.browser.load_url(url)
        self.assertEqual(self.browser.url().toString(), url)
    
    def test_save_page(self):
        """Test page saving functionality"""
        test_file = 'test_page.html'
        self.browser.load_url('about:blank')
        self.browser.save_page(test_file)
        self.assertTrue(os.path.exists(test_file))
        os.remove(test_file)
    
    def tearDown(self):
        self.browser.deleteLater()

class TestNetworkManager(unittest.TestCase):
    """Test the unified network manager"""
    
    def setUp(self):
        self.network = NetworkManager()
    
    async def test_request_get(self):
        """Test GET request"""
        url = 'https://example.com'
        response = await self.network.request(url)
        self.assertIsNotNone(response)
    
    async def test_request_post(self):
        """Test POST request"""
        url = 'https://example.com'
        data = {'key': 'value'}
        response = await self.network.request(url, method='POST', data=data)
        self.assertIsNotNone(response)
    
    def tearDown(self):
        asyncio.run(self.network.close())

class TestMPRISInterface(unittest.TestCase):
    """Test the unified MPRIS interface"""
    
    def setUp(self):
        self.mpris = MPRISInterface()
    
    def test_update_metadata(self):
        """Test metadata updates"""
        metadata = {
            'title': 'Test Track',
            'artist': 'Test Artist'
        }
        self.mpris.update_metadata(metadata)
        self.assertEqual(self.mpris.metadata, metadata)
    
    def test_playback_status(self):
        """Test playback status updates"""
        self.mpris.update_playback_status('Playing')
        self.assertEqual(self.mpris.playback_status, 'Playing')

class TestHLSStream(unittest.TestCase):
    """Test the unified HLS implementation"""
    
    def setUp(self):
        self.hls = HLSStream()
    
    async def test_load_playlist(self):
        """Test playlist loading"""
        url = 'http://example.com/playlist.m3u8'
        with patch.object(self.hls.network, 'request') as mock_request:
            mock_request.return_value = '#EXTM3U\n#EXTINF:10,\ntest.ts'
            result = await self.hls.load_playlist(url)
            self.assertTrue(result)
            self.assertEqual(len(self.hls.segments), 1)
    
    async def test_download_segment(self):
        """Test segment downloading"""
        url = 'http://example.com/test.ts'
        output = 'test_segment.ts'
        with patch.object(self.hls.network, 'request') as mock_request:
            mock_request.return_value = b'test data'
            result = await self.hls.download_segment(url, output)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(output))
            os.remove(output)
    
    def tearDown(self):
        asyncio.run(self.hls.close())

class TestMainWindow(unittest.TestCase):
    """Test the unified main window"""
    
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])
    
    def setUp(self):
        self.media_player = MagicMock()
        self.network = MagicMock()
        self.mpris = MagicMock()
        self.window = MainWindow(
            media_player=self.media_player,
            network=self.network,
            mpris=self.mpris,
            base_dir='.',
            resource_dir='./resources'
        )
    
    def test_toggle_playback(self):
        """Test playback toggling"""
        self.media_player.is_playing.return_value = False
        self.window.toggle_playback()
        self.media_player.play.assert_called_once()
        
        self.media_player.is_playing.return_value = True
        self.window.toggle_playback()
        self.media_player.pause.assert_called_once()
    
    def test_playlist_navigation(self):
        """Test playlist navigation"""
        self.window.playlist.addItem('Test 1')
        self.window.playlist.addItem('Test 2')
        self.window.playlist.setCurrentRow(0)
        
        self.window.play_next()
        self.assertEqual(self.window.playlist.currentRow(), 1)
        
        self.window.play_previous()
        self.assertEqual(self.window.playlist.currentRow(), 0)
    
    def tearDown(self):
        self.window.close()
        self.window.deleteLater()

if __name__ == '__main__':
    unittest.main()
