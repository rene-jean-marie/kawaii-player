# Kawaii Player API Documentation

## Core Components

### UnifiedPlayer

The media playback engine that provides a clean interface to MPV.

```python
from kawaii_player import UnifiedPlayer

player = UnifiedPlayer()

# Basic playback control
player.load("video.mp4")
player.play()
player.pause()
player.stop()

# Properties
position = player.get_position()  # 0-1 range
duration = player.get_duration()  # in seconds
volume = player.get_volume()  # 0-100 range

# Connect to signals
player.playback_started.connect(on_started)
player.playback_paused.connect(on_paused)
player.position_changed.connect(on_position)
```

### PlaylistManager

Manages playlists and media items.

```python
from kawaii_player import PlaylistManager

playlists = PlaylistManager("/path/to/config")

# Create and manage playlists
playlists.create_playlist("favorites")
playlists.add_item(
    title="My Video",
    url="video.mp4",
    playlist_name="favorites",
    duration=120,
    thumbnail="thumb.jpg"
)

# Get items
items = playlists.get_items("favorites")
current = playlists.get_item(0)

# Connect to signals
playlists.playlist_changed.connect(on_change)
playlists.item_added.connect(on_add)
```

### SettingsManager

Handles application configuration.

```python
from kawaii_player import SettingsManager

settings = SettingsManager("/path/to/config")

# Get/Set settings
volume = settings.get("player.volume", 100)
settings.set("player.volume", 80)

# Categories
player_settings = settings.get_category("player")
settings.set_category("player", {"volume": 80})

# Import/Export
settings.export_settings("backup.json")
settings.import_settings("backup.json")
```

### NetworkManager

Handles network operations with async support.

```python
from kawaii_player import NetworkManager

network = NetworkManager()

# Make requests
async def fetch_data():
    response = await network.request(
        url="https://api.example.com/data",
        method="GET",
        headers={"Accept": "application/json"}
    )
    return response

# Clean up
await network.close()
```

### MPRISInterface

Provides media control integration.

```python
from kawaii_player import MPRISInterface

mpris = MPRISInterface()

# Update state
mpris.update_playback_status("Playing")
mpris.update_metadata({
    "title": "My Video",
    "artist": "Artist Name"
})
```

### HLSStream

Handles HTTP Live Streaming.

```python
from kawaii_player import HLSStream

hls = HLSStream()

# Load and manage streams
async def stream_video():
    await hls.load_playlist("http://example.com/stream.m3u8")
    segments = hls.get_current_segments()
    
    async def on_segment(segment):
        await hls.download_segment(segment, "output.ts")
    
    await hls.monitor_live_stream(on_segment)
```

### BrowserPage

Unified web browser component.

```python
from kawaii_player import BrowserPage

browser = BrowserPage()

# Navigation
browser.load_url("https://example.com")
browser.save_page("page.html")
```

## Plugin Development

Plugins can extend Kawaii Player's functionality using these components. Here's how to create plugins:
