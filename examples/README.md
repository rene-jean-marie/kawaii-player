# Kawaii Player Example Plugins

This directory contains example plugins demonstrating how to extend Kawaii Player's functionality using the unified components.

## Available Plugins

### YouTube Plugin
Integration with YouTube for searching and playing videos.

Features:
- Search YouTube videos
- Get video information
- Add videos to playlists
- Extract video IDs from URLs

### Subtitle Plugin
Download and manage subtitles for media files.

Features:
- Search subtitles using OpenSubtitles API
- Download subtitle files
- Load subtitles into player
- Extract embedded subtitles
- Clean subtitle cache

### Streaming Plugin
Integration with streaming services like Twitch.

Features:
- Search live streams
- Get stream URLs
- Start/stop streaming
- Chat integration
- Add streams to playlists

## Usage

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your API keys in the settings:
```python
settings = SettingsManager()
settings.set('plugins.youtube.api_key', 'YOUR_API_KEY')
settings.set('plugins.subtitles.opensubtitles_key', 'YOUR_API_KEY')
settings.set('plugins.streaming.twitch_client_id', 'YOUR_CLIENT_ID')
settings.set('plugins.streaming.twitch_secret', 'YOUR_CLIENT_SECRET')
```

3. Import and use the plugins:
```python
from kawaii_player.plugins.youtube_plugin import YouTubePlugin
from kawaii_player.plugins.subtitle_plugin import SubtitlePlugin
from kawaii_player.plugins.streaming_plugin import StreamingPlugin

# Initialize components
network = NetworkManager()
playlist = PlaylistManager()
settings = SettingsManager()
player = UnifiedPlayer()
hls = HLSStream()

# Create plugin instances
youtube = YouTubePlugin(network, playlist, settings)
subtitles = SubtitlePlugin(network, player, settings)
streaming = StreamingPlugin(network, playlist, settings, hls)

# Use plugins
async def main():
    # Search YouTube
    results = await youtube.search('kawaii music')
    for video in results:
        youtube.add_to_playlist(video)
    
    # Download subtitles
    subs = await subtitles.search_subtitles('movie title')
    if subs:
        path = await subtitles.download_subtitle(subs[0]['id'])
        subtitles.load_subtitle(path)
    
    # Start streaming
    streams = await streaming.search_streams('game category')
    if streams:
        await streaming.start_stream(streams[0]['username'])

# Run example
asyncio.run(main())
```

## Creating Your Own Plugins

1. Create a new Python file in the plugins directory
2. Import required components from kawaii_player
3. Create a class that inherits from QtCore.QObject
4. Initialize with required components in __init__
5. Define your plugin's functionality
6. Use signals to communicate state changes

Example structure:
```python
from PyQt5 import QtCore
from kawaii_player import NetworkManager, PlaylistManager

class MyPlugin(QtCore.QObject):
    # Define signals
    my_signal = QtCore.pyqtSignal(str)
    
    def __init__(self, network: NetworkManager, playlist: PlaylistManager):
        super().__init__()
        self.network = network
        self.playlist = playlist
    
    async def my_function(self):
        # Implement functionality
        pass
```

## Best Practices

1. **Error Handling**
   - Always catch and log exceptions
   - Provide meaningful error messages
   - Return None/False on failure

2. **Resource Management**
   - Clean up resources in stop/close methods
   - Use context managers when appropriate
   - Cancel async tasks properly

3. **Settings**
   - Store API keys and credentials in settings
   - Use meaningful setting keys
   - Provide default values

4. **Documentation**
   - Document class and method purposes
   - Specify parameter types and return values
   - Include usage examples

5. **Testing**
   - Write unit tests for your plugin
   - Test error cases
   - Mock external services

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your plugin
4. Add documentation and tests
5. Submit a pull request

## License

These examples are licensed under the same terms as Kawaii Player itself.
