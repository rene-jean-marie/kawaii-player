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

import os
import shutil
import platform
from setuptools import Extension, setup
from Cython.Build import cythonize
import ctypes.util

system = platform.system().lower()

"""
 GNU/Linux users should install dependencies manually using their native
 package manager
"""

base_requires = [
    "aiohttp>=3.8.0",
    "requests>=2.25.0",
]

if system == "linux":
    base_requires.append("dbus-python>=1.2.0")

install_requires = base_requires.copy()
if system in ["darwin", "nt"]:
    install_requires.extend([
        "PyQt5>=5.15.0",
        "pycurl",
        "bs4",
        "Pillow",
        "mutagen",
        "lxml",
        "yt-dlp",
        "certifi",
        "PyQtWebEngine",
        "PyOpenGL",
        "python-vlc"
    ])

library_path = None
if system == "darwin":
    library_path = ["/usr/local/lib"]

extension_src = "pympv/mpv.pyx"

if system == "linux":
    mpv_so = ctypes.util.find_library("mpv")
    if mpv_so == "libmpv.so.1":
        extension_src = "pympv/pympv-0.7.1/mpv.pyx"

if library_path is None:
    extensions = [Extension("mpv", [extension_src], libraries=["mpv"])]
else:
    extensions = [Extension("mpv", [extension_src], libraries=["mpv"], library_dirs=library_path)]

setup(
    name='kawaii-player',
    version='6.0.0',
    license='GPLv3',
    author='kanishka-linux',
    author_email='kanishka.linux@gmail.com',
    url='https://github.com/kanishka-linux/kawaii-player',
    long_description="README.md",
    packages=[
        'kawaii_player',
        'kawaii_player.Plugins',
        'kawaii_player.widgets',
    ],
    include_package_data=True,
    install_requires=install_requires,
    ext_modules=cythonize(extensions, force=True),
    entry_points={
        'gui_scripts': [
            'kawaii-player = kawaii_player.app:main',
            'kawaii-player-legacy = kawaii_player.kawaii_player:main'
        ],
        'console_scripts': [
            'kawaii-player-console = kawaii_player.app:main',
            'kawaii-player-console-legacy = kawaii_player.kawaii_player:main'
        ]
    },
    description="A modern Audio/Video manager and multimedia player with unified components",
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Multimedia :: Video :: Display',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
