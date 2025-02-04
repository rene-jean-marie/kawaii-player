# Kawaii Player Migration Guide

## Overview
This guide helps you migrate from the legacy Kawaii Player implementation to the new unified components architecture. The new architecture provides better performance, maintainability, and a more modern codebase.

## Key Changes
- Unified browser implementation supporting both WebEngine and WebKit
- Streamlined network layer with async support
- Unified MPRIS service
- Modern HLS implementation
- New main window with improved UI/UX

## Migration Steps

### For Users

1. **Installation**
   ```bash
   pip install --upgrade kawaii-player
   ```

2. **Running the Application**
   - New version: `kawaii-player`
   - Legacy version: `kawaii-player-legacy`

3. **Configuration**
   - Configuration files remain in the same location
   - New settings will be automatically migrated
   - Custom themes and plugins remain compatible

### For Developers

1. **Import Changes**
   ```python
   # Old imports
   from kawaii_player.browser import Browser
   from kawaii_player.vinanti import Vinanti
   
   # New imports
   from kawaii_player import BrowserPage
   from kawaii_player import NetworkManager
   ```

2. **Browser API Changes**
   ```python
   # Old code
   browser = Browser()
   browser.load(url)
   
   # New code
   browser = BrowserPage()
   browser.load_url(url)
   ```

3. **Network API Changes**
   ```python
   # Old code
   client = Vinanti()
   response = client.get(url)
   
   # New code
   network = NetworkManager()
   response = await network.request(url, method='GET')
   ```

4. **MPRIS Integration**
   ```python
   # Old code
   from kawaii_player.mpris_dbus import MPRISInterface
   
   # New code
   from kawaii_player import MPRISInterface
   mpris = MPRISInterface()
   ```

5. **HLS Streaming**
   ```python
   # Old code
   from kawaii_player.hls_webkit import HLSEngine
   
   # New code
   from kawaii_player import HLSStream
   hls = HLSStream()
   await hls.load_playlist(url)
   ```

## Testing the Migration

1. Run both versions in parallel:
   ```bash
   kawaii-player &  # New version
   kawaii-player-legacy &  # Old version
   ```

2. Test key features:
   - Media playback
   - Playlist management
   - Browser functionality
   - Network operations
   - MPRIS controls
   - HLS streaming

## Troubleshooting

1. **Browser Issues**
   - Check Qt version compatibility
   - Verify WebEngine/WebKit installation

2. **Network Problems**
   - Check async/await usage
   - Verify network connectivity
   - Check SSL certificates

3. **MPRIS Issues**
   - Verify D-Bus installation
   - Check system permissions

## Getting Help
- GitHub Issues: [kawaii-player/issues](https://github.com/kanishka-linux/kawaii-player/issues)
- Documentation: [kawaii-player/docs](https://github.com/kanishka-linux/kawaii-player/docs)

## Contributing
We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
