"""
Autoplay functionality for Kawaii Player
"""
import os
import time
from PyQt5 import QtCore

class AutoPlayTimer(QtCore.QTimer):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.setSingleShot(True)
        self.timeout.connect(self.auto_play_first_item)
        
    def auto_play_first_item(self):
        """Auto play the first item in the playlist when application starts"""
        if self.ui.list2.count() > 0:
            self.ui.list2.setCurrentRow(0)
            item = self.ui.list2.item(0)
            if item:
                self.ui.list2.itemDoubleClicked['QListWidgetItem*'].emit(item)
        elif self.ui.list1.count() > 0:
            self.ui.list1.setCurrentRow(0)
            self.ui.list1.itemDoubleClicked['QListWidgetItem*'].emit(self.ui.list1.item(0))
