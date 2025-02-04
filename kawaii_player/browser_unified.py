"""
Unified browser implementation supporting both WebEngine and WebKit
"""
import os
import logging
from PyQt5 import QtCore, QtWidgets

logger = logging.getLogger(__name__)

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView as WebView
    from PyQt5.QtWebEngineCore import QWebEngineHttpRequest
    BROWSER_ENGINE = 'webengine'
except ImportError:
    try:
        from PyQt5.QtWebKitWidgets import QWebView as WebView
        from PyQt5.QtNetwork import QNetworkRequest
        BROWSER_ENGINE = 'webkit'
    except ImportError:
        logger.error('Neither QtWebEngine nor QtWebKit is available')
        WebView = None
        BROWSER_ENGINE = None

class BrowserPage(WebView):
    """Unified browser page implementation"""
    
    def __init__(self, parent=None, ui=None, home=None, tmp=None, logger=None):
        super().__init__(parent)
        self.ui = ui
        self.home = home
        self.tmp_dir = tmp
        self.logger = logger
        self.cur_location = None
        
        # Set up common settings
        if BROWSER_ENGINE == 'webengine':
            self.settings().setAttribute(
                QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True
            )
            self.settings().setAttribute(
                QtWebEngineWidgets.QWebEngineSettings.JavascriptEnabled, True
            )
        else:
            self.settings().setAttribute(
                QtWebKit.QWebSettings.PluginsEnabled, True
            )
            self.settings().setAttribute(
                QtWebKit.QWebSettings.JavascriptEnabled, True
            )
        
        self.page().setLinkDelegationPolicy(self.page().DelegateAllLinks)
        self.linkClicked.connect(self.link_clicked)
        
    def link_clicked(self, url):
        """Handle clicked links"""
        url_str = url.toString()
        self.cur_location = url_str
        if self.ui:
            self.ui.gui_signals.text_changed(url_str)
        self.load(url)
    
    def load_url(self, url, ref_url=None):
        """Load URL with optional referrer"""
        if BROWSER_ENGINE == 'webengine':
            request = QWebEngineHttpRequest(QtCore.QUrl(url))
            if ref_url:
                request.setHeader(b'Referer', ref_url.encode('utf-8'))
            self.load(request)
        else:
            request = QNetworkRequest(QtCore.QUrl(url))
            if ref_url:
                request.setRawHeader(b'Referer', ref_url.encode('utf-8'))
            self.load(request)
            
    def save_page(self, path):
        """Save current page to file"""
        if BROWSER_ENGINE == 'webengine':
            self.page().save(path, QtWebEngineCore.QWebEngineDownloadItem.CompleteHtmlSaveFormat)
        else:
            frame = self.page().mainFrame()
            html = frame.toHtml()
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
