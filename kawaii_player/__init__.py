"""
Copyright (C) 2017 kanishka-linux kanishka.linux@gmail.com

This file is part of kawaii-player.

kawaii-player is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

kawaii-player is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with kawaii-player.  If not, see <http://www.gnu.org/licenses/>.
"""

__version__ = '6.0.0'

# Import unified components
from .browser_unified import BrowserPage
from .network import NetworkManager
from .mpris import MPRISInterface
from .hls import HLSStream
from .unified_window import MainWindow

# For backward compatibility
from .kawaii_player import main as legacy_main

__all__ = [
    'BrowserPage',
    'NetworkManager',
    'MPRISInterface',
    'HLSStream',
    'MainWindow',
    'legacy_main'
]
