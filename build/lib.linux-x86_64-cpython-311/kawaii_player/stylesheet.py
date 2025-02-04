import os
from PyQt5 import QtWidgets

class WidgetStyleSheet:
    
    def __init__(self, ui_widet, hm, base, mw, dsession=None):
        global gui, home, BASEDIR, desktop_session, MainWindow
        gui = ui_widet
        home = hm
        BASEDIR = base
        MainWindow = mw
        if dsession is None:
            desktop_session = os.getenv('DESKTOP_SESSION')
            if desktop_session:
                desktop_session = desktop_session.lower()
            else:
                desktop_session = 'lxde'
        else:
            desktop_session = dsession
        
        # Set up resource paths
        self.resource_dir = os.path.join(BASEDIR, 'kawaii_player', 'resources')
        self.down_arrow = os.path.join(self.resource_dir, 'down-arrow.svg')
        self.checkmark = os.path.join(self.resource_dir, 'checkmark.svg')
            
    def change_list2_style(self, mode=None):
        if isinstance(mode, bool):
            gui.list_with_thumbnail = mode
        if gui.list_with_thumbnail:
            height = '128px'
            gui.list2.setWordWrap(True)
        else:
            height = '{}px'.format(gui.global_font_size*3)
            gui.list2.setWordWrap(False)
        if gui.font_bold:
            font_bold = 'bold'
        else:
            font_bold = ''
        if gui.player_theme in ['default', 'transparent', 'mix']:
            gui.list2.setStyleSheet("""
                QListWidget {
                    font: {bold};
                    color: {1};
                    background: rgba(0, 0, 0, 40%);
                    border: 1px solid rgba(255, 255, 255, 10%);
                    border-radius: 8px;
                    padding: 5px;
                }
                QListWidget:item {
                    height: {0};
                    border-radius: 4px;
                    margin: 2px;
                    padding: 4px;
                }
                QListWidget:item:hover {
                    background: rgba(255, 255, 255, 5%);
                }
                QListWidget:item:selected:active {
                    background: rgba(61, 90, 254, 40%);
                    color: {2};
                }
                QListWidget:item:selected:inactive {
                    background: rgba(61, 90, 254, 20%);
                }
                QMenu {
                    color: white;
                    background: rgb(45, 45, 45);
                    border: 1px solid rgba(255, 255, 255, 10%);
                    border-radius: 8px;
                    padding: 5px;
                }
                QMenu::item {
                    padding: 8px 24px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background: rgba(61, 90, 254, 40%);
                }
                """.format(height, gui.list_text_color, gui.list_text_color_focus, bold=font_bold))
        elif gui.player_theme == 'system':
            gui.list2.setAlternatingRowColors(True)
            gui.list2.setStyleSheet("""QListWidget{{
                border-radius:3px;
                }}
                QListWidget:item {{
                height: {0};
                }}
                QListWidget:item:selected:active {{
                background:rgba(0, 0, 0, 20%);
                color: {1};
                }}
                """.format(height, gui.list_text_color_focus))
        elif gui.player_theme == 'dark':
            gui.list2.setStyleSheet("""
                QListWidget{{
                color:{1};background:rgba(0,0,0,30%);border:rgba(0,0,0,30%);
                font: {bold} {size}px {font};
                }}
                QListWidget:item {{
                height: {0};
                }}
                QListWidget:item:selected:active {{
                background:rgba(0, 0, 0, 20%);
                color: {2};
                }}
                
                QListWidget:item:inactive {{
                color:{1};background:rgba(0,0,0,0%);border:rgba(0,0,0,0%);
                font: {bold} {font};
                }}
                
                QMenu{{
                color: white;
                background: rgb(56,60,74);border: rgba(0,0,0, 30%);
                padding: 2px;
                }}
                QMenu::item{{
                color: {1};
                font: {font};
                background:rgb(56,60,74);border: rgba(0,0,0, 30%);
                padding: 4px; margin: 2px 2px 2px 10px;
                }}
                QMenu::item:selected{{
                color: {2};
                background:rgba(0, 0, 0, 20%);border: rgba(0,0,0, 30%);
                }}
                """.format(height, gui.list_text_color, gui.list_text_color_focus,
                           bold=font_bold, font=gui.global_font, size=gui.global_font_size)
                        )
                
    def qmenu_style(self, widget):
        widget.setStyleSheet("""
            QMenu{
            color: white;
            background: rgb(56,60,74);border: rgba(0,0,0, 30%);
            padding: 2px;
            }
            QMenu::item{
            color: white;
            background:rgb(56,60,74);border: rgba(0,0,0, 30%);
            padding: 4px; margin: 2px 2px 2px 10px;
            }
            QMenu::item:selected{
            color: white;
            background:rgba(0, 0, 0, 20%);border: rgba(0,0,0, 30%);
            }
            """)
                
    def webStyle(self, web):
        global desktop_session, gui
        try:
            if desktop_session.lower() != 'plasma':
                if gui.player_theme == 'dark':
                    web.setStyleSheet(
                        """
                        QMenu{
                        color: white;
                        background: rgb(56,60,74);border: rgba(0,0,0, 30%);
                        padding: 2px;
                        }
                        QMenu::item{
                        color: white;
                        background:rgb(56,60,74);border: rgba(0,0,0, 30%);
                        padding: 2px; margin: 2px 2px 2px 10px;
                        }
                        QMenu::item:selected{
                        color: white;
                        background:rgba(0, 0, 0, 20%);border: rgba(0,0,0, 30%);
                        }
                        """)
                else:
                    web.setStyleSheet(
                        """QMenu{color:black;
                        background-image:url('1.png');}""")
        except NameError as e:
            print(e)
            desktop_session = 'lxde'
            
    def apply_stylesheet(self, widget=None, theme=None):
        if gui.font_bold:
            font_bold = 'bold'
        else:
            font_bold = ''
        if not widget and (theme is None or theme in ['default', 'transparent', 'mix']):
            alpha = '40%'
            qbtn = '20%'
            
            # Convert paths to Qt style
            down_arrow = self.down_arrow.replace('\\', '/')
            checkmark = self.checkmark.replace('\\', '/')
            
            for widget in [gui.tab_2, gui.tab_5, gui.tab_6, gui.go_opt,
                           gui.text, gui.cover_label, gui.text_save_btn, gui.search_on_type_btn,
                           gui.frame, gui.frame1, gui.torrent_frame, gui.float_window]:
                if widget in [gui.text_save_btn, gui.search_on_type_btn, gui.frame1]:
                    alpha = '60%'
                else:
                    alpha = '40%'
                if widget == gui.frame1:
                    font_size = '11px'
                    if not font_bold:
                        font_size = ''
                else:
                    font_size = ''
                widget.setStyleSheet("""
                    * {
                        font: {bold} {font_size};
                        color: {color};
                        transition: all 0.2s ease;
                    }
                    QFrame, QWidget {
                        background: rgba(0, 0, 0, {alpha});
                        border: 1px solid rgba(255, 255, 255, 10%);
                        border-radius: 8px;
                    }
                    QPushButton {
                        background: rgba(61, 90, 254, 40%);
                        border: none;
                        border-radius: 6px;
                        padding: 8px 16px;
                        color: white;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background: rgba(61, 90, 254, 60%);
                    }
                    QPushButton:pressed {
                        background: rgba(61, 90, 254, 80%);
                    }
                    QLineEdit {
                        background: rgba(0, 0, 0, 30%);
                        border: 1px solid rgba(255, 255, 255, 10%);
                        border-radius: 6px;
                        padding: 8px;
                        color: white;
                    }
                    QLineEdit:focus {
                        border: 1px solid rgba(61, 90, 254, 60%);
                    }
                    QTextEdit {
                        background: rgba(0, 0, 0, 30%);
                        border: 1px solid rgba(255, 255, 255, 10%);
                        border-radius: 6px;
                        padding: 8px;
                        color: {color};
                    }
                    QLabel {
                        background: transparent;
                        color: {color};
                    }
                    QComboBox {
                        background: rgba(0, 0, 0, {alpha});
                        border: 1px solid rgba(255, 255, 255, 10%);
                        border-radius: 6px;
                        padding: 8px;
                        color: {color};
                        min-width: 100px;
                    }
                    QComboBox:hover {
                        background: rgba(61, 90, 254, 20%);
                    }
                    QComboBox:on {
                        background: rgba(61, 90, 254, 40%);
                    }
                    QComboBox::drop-down {
                        border: none;
                        padding-right: 8px;
                    }
                    QComboBox::down-arrow {
                        image: url({down_arrow});
                        width: 12px;
                        height: 12px;
                    }
                    QScrollBar:vertical {
                        border: none;
                        background: rgba(0, 0, 0, 20%);
                        width: 8px;
                        border-radius: 4px;
                    }
                    QScrollBar::handle:vertical {
                        background: rgba(61, 90, 254, 40%);
                        border-radius: 4px;
                        min-height: 20px;
                    }
                    QScrollBar::handle:vertical:hover {
                        background: rgba(61, 90, 254, 60%);
                    }
                    QScrollBar::add-line:vertical,
                    QScrollBar::sub-line:vertical {
                        height: 0px;
                    }
                    QSlider::groove:horizontal {
                        border: none;
                        height: 4px;
                        background: rgba(255, 255, 255, 20%);
                        border-radius: 2px;
                    }
                    QSlider::handle:horizontal {
                        background: rgb(61, 90, 254);
                        border: none;
                        width: 16px;
                        height: 16px;
                        margin: -6px 0;
                        border-radius: 8px;
                    }
                    QSlider::handle:horizontal:hover {
                        background: rgb(82, 108, 254);
                    }
                    QCheckBox {
                        spacing: 8px;
                        color: {color};
                    }
                    QCheckBox::indicator {
                        width: 18px;
                        height: 18px;
                        border-radius: 4px;
                        border: 1px solid rgba(255, 255, 255, 20%);
                    }
                    QCheckBox::indicator:unchecked {
                        background: rgba(0, 0, 0, 30%);
                    }
                    QCheckBox::indicator:checked {
                        background: rgba(61, 90, 254, 100%);
                        image: url({checkmark});
                    }
                    QToolTip {
                        background: rgb(45, 45, 45);
                        color: white;
                        border: 1px solid rgba(255, 255, 255, 10%);
                        border-radius: 4px;
                        padding: 4px 8px;
                    }
                    """.format(
                        alpha=alpha, color=gui.list_text_color,
                        bold=font_bold, font_size=font_size,
                        down_arrow=down_arrow, checkmark=checkmark
                    ))
            gui.player_opt.setStyleSheet("""
                QFrame{background:rgba(0, 0, 0, 0%);border:rgba(0, 0, 0, 0%);}
                QPushButton{border-radius:0px;max-height:64px;}
                QPushButton::hover{background-color: yellow;color: black;}
                """)
            
            
            gui.settings_box.setStyleSheet("""
                    QFrame{{color:white;background:rgba(0,0,0,{alpha});border:rgba(0,0,0,{alpha});}}
                    QTabWidget{{
                        color:{color};
                        border:rgba(0,0,0,{alpha});background:rgb(56,60,74);
                        background-color:rgba(0,0,0,{alpha});
                        }}
                    QTabWidget:pane {{
                        color:{color};font: {bold} {font};
                        border:rgba(0,0,0,{alpha});background:rgba(56,60,74, {alpha});
                    }}
                    
                    QTabBar {{
                        color:{color};font: {bold} {font};
                        border:rgba(0,0,0,{alpha});background:rgba(56,60,74, {alpha});
                        background-color:rgba(0,0,0,{alpha});
                    }}
                    
                    QTabBar:tab{{
                        color:{color};background:rgba(56,60,74, {alpha});
                    }}
                    
                    QTabBar:tab:selected{{
                        color:{color};background:rgba(0,0,0, 20%);
                    }}
                    
                    QListWidget{{
                        color:{color};background:rgba(0,0,0,30%);border:rgba(0,0,0,30%);
                        font: {bold} {font};
                    }}
                    QListWidget:item {{
                        height: 30px;
                    }}
                    QListWidget:item:selected:active {{
                        background:rgba(0, 0, 0, 20%);
                        color: {focus};
                    }}
                    
                    QPushButton{{color:{color};background:rgba(0,0,0,{btn});border:rgba(0,0,0,{btn});
                    max-height:40px; font: {bold};}}
                    QPushButton::hover{{background-color: yellow;color: black;}}
                    QLineEdit{{color:{color};background:rgba(0,0,0,10%);
                    max-height:40px;border:rgba(0, 0, 0, 10%); font: {bold} {font};}}
                    QTextEdit{{color:{color};background:rgba(0,0,0,10%);
                    border:rgba(0, 0, 0, 10%); font: {bold} {font};}}
                    
                    QScrollBar{{ background: rgba(0,0,0,30%);
                    }}
                    
                    QScrollBar::handle{{ background: rgba(0,0,0, {btn});
                    border-radius:4px;
                    }}
                    
                    QScrollBar::add-line{{ background: rgba(0,0,0,0%);
                    }}
                    
                    QScrollBar::sub-line{{ background: rgba(0,0,0,0%);
                    }}
                    
                    QCheckBox{{color:{color};background:rgba(0,0,0,10%);
                        border:rgba(0, 0, 0, 10%); font: {bold} {font};}}
                    
                    QLabel{{color:{color};background:rgba(0,0,0,0%);
                    max-height:40px;border:rgba(0, 0, 0, 10%);font: {bold} {font};}}
                    QComboBox {{
                    color: {color};
                    selection-color:yellow;background:rgba(0,0,0,{btn});
                    border:rgba(0, 0, 0, 10%);
                    padding: 0px 2px 0px 4px;
                    font: {bold};
                    max-height: 40px;
                    }}
                    QComboBox QAbstractItemView{{
                        background-color: rgba(54,60,74);
                        border-radius: 0px;
                        color: {color};
                        font: {bold} {font};
                     }}
                    QComboBox::hover{{background-color: rgba(0,0,0,40%);color: {color};}}
                    QComboBox::drop-down {{
                    width: 22px;
                    border: 2px;
                    color:white;
                    }}
                    QComboBox::focus {{
                    background-color:rgba(0,0,0,40%);color: {focus};
                    }}
                    QComboBox::down-arrow {{
                    width: 2px;
                    height: 2px;
                    }}""".format(
                        alpha=alpha, btn=qbtn, color=gui.list_text_color,
                        focus=gui.list_text_color_focus, bold=font_bold,
                        size=gui.global_font_size, font=gui.global_font)
                    )
            
            gui.slider.setStyleSheet("""
                QSlider:groove:horizontal {{
                height: 8px;
                border:rgba(0, 0, 0, 30%);
                background:rgba(0, 0, 0, 30%);
                margin: 2px 0;
                }}
                QSlider:handle:horizontal {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
                border: 1px solid #5c5c5c;
                width: 8px;
                margin: -2px 0; 
                border-radius: 3px;
                }}
                QToolTip {{
                font : {bold} {size}px {font};
                color: {color};
                background:rgb(54, 60, 74);
                }}
                """.format(
                        color=gui.list_text_color, bold=font_bold,
                        size=gui.global_font_size+3, font=gui.global_font
                        )
                    )
            gui.list_poster.setStyleSheet("""
                QListWidget{{
                font: {bold};color:{0};
                background:rgba(0, 0, 0, 50%);border:rgba(0, 0, 0, 50%);
                }}
                QListWidget:item {{
                height: 312px;
                width: 256px;
                }}
                QListWidget:item:selected:active {{
                background:rgba(0, 0, 0, 60%);
                color: {1};
                }}
                QListWidget:item:selected:inactive {{
                border:rgba(0, 0, 0, 30%);
                }}
                QMenu{{
                    font: 12px;color:black;background-image:url('1.png');
                }}
                """.format(gui.thumbnail_text_color, gui.thumbnail_text_color_focus, bold=font_bold))
            for widget in [gui.scrollArea, gui.scrollArea1]:
                widget.setStyleSheet("""
                    QListWidget{{
                    font: {bold} ;color:white;
                    background:rgba(0, 0, 0, 30%);border:rgba(0, 0, 0, 30%);border-radius: 3px;
                    }}
                    QListWidget:item:selected:active {{
                    background:rgba(0, 0, 0, 20%);
                    color: yellow;
                    }}
                    QListWidget:item:selected:inactive {{
                    border:rgba(0, 0, 0, 30%);
                    }}
                    QMenu{{
                        font: 12px;color:black;background-image:url('1.png');
                    }}
                    """.format(bold=font_bold))
            for widget in [gui.list1, gui.list3, gui.list4, gui.list5, gui.list6]:
                if widget == gui.list3:
                    border = '0px'
                else:
                    border = '3px'
                widget.setStyleSheet("""
                    QListWidget{{
                    font: {bold};color:{0};background:rgba(0, 0, 0, 30%);
                    border:rgba(0, 0, 0, 30%);border-radius: {2};
                    }}
                    QListWidget:item {{
                    height: {height}px;
                    }}
                    QListWidget:item:selected:active {{
                    background:rgba(0, 0, 0, 20%);
                    color: {1};
                    }}
                    QListWidget:item:selected:inactive {{
                    border:rgba(0, 0, 0, 30%);
                    }}
                    QMenu{{
                        font: 12px;color:black;background-image:url('1.png');
                    }}
                    """.format(gui.list_text_color, gui.list_text_color_focus, border,bold=font_bold, height=gui.global_font_size*3))
            if gui.list_with_thumbnail:
                ht = '128px'
            else:
                ht = '{}px'.format(gui.global_font_size*3)
            gui.list2.setStyleSheet(
                """
                QListWidget{{
                font: {bold}; color:{1};background:rgba(0, 0, 0, 30%);
                border:rgba(0, 0, 0, 30%);border-radius:3px;}}
                QListWidget:item {{height: {0};}}
                QListWidget:item:selected:active {{background:rgba(0, 0, 0, 20%);
                color: {2};}}
                QListWidget:item:selected:inactive {{border:rgba(0, 0, 0, 30%);}}
                QMenu{{font: 12px;color:black;
                background-image:url('1.png');}}
                """.format(ht, gui.list_text_color, gui.list_text_color_focus, bold=font_bold))
            for widget in [gui.progress, gui.progressEpn]:
                widget.setStyleSheet("""QProgressBar{{
                    font: {bold};
                    color:{color};
                    background:rgba(0, 0, 0, 30%);
                    border:rgba(0, 0, 0, 1%) ;
                    border-radius: 1px;
                    text-align: center;}}
                    
                    QProgressBar:chunk {{
                    background-color: rgba(255, 255, 255, 30%);
                    width: 10px;
                    margin: 0.5px;
                    }}""".format(bold=font_bold, color=gui.list_text_color))
            
            for widget in ([gui.btn30, gui.btn2, gui.btn3, gui.btn10,
                            gui.comboBox20, gui.comboBox30, gui.btnOpt]):
                widget.setStyleSheet("""
                    QComboBox {
                    min-height:30px;
                    max-height:63px;
                    padding: 1px 1px 1px 1px;
                    font:bold 10px;background:rgba(0, 0, 0, 30%);border:rgba(0, 0, 0, 30%);
                    selection-color:yellow;
                    }
                    QComboBox::drop-down {
                    width: 22px;
                    border: 0px;
                    color:black;
                    }
                    QComboBox::hover{background-color: lightgray;color: white;}
                    QComboBox::focus {
                        background-color:rgba(0,0,0,60%);color: white;
                    }
                    QComboBox::down-arrow {{
                    width: 2px;
                    height: 2px;
                    }}""")
            
            for widget in [gui.label_torrent_stop, gui.label_down_speed, gui.label_up_speed]:
                widget.setStyleSheet("""
                QToolTip {{
                font : {bold} {size}px {font};
                color: {color};
                background:rgb(56,60,74);
                }}
                """.format(bold=font_bold, font=gui.global_font,
                           size=gui.global_font_size+3, color=gui.list_text_color)
                        )
        elif widget == gui.list2 and (theme is None or theme in ['default', 'transparent', 'mix']):
            if gui.list_with_thumbnail:
                ht = '128px'
            else:
                ht = '{}px'.format(gui.global_font_size*3)
            gui.list2.setStyleSheet("""
                QListWidget{{font: bold 12px;
                color:{1};background:rgba(0, 0, 0, 30%);
                border:rgba(0, 0, 0, 30%);border-radius:3px;}}
                QListWidget:item {{height: {0};}}
                QListWidget:item:selected:active {{background:rgba(0, 0, 0, 20%);
                color: {2};}}
                QListWidget:item:selected:inactive {{border:rgba(0, 0, 0, 30%);}}
                QMenu{{font: 12px;color:black;
                background-image:url('1.png');}}
                """.format(ht, gui.list_text_color, gui.list_text_color_focus))
        elif theme == 'system':
            bgcol = gui.frame1.palette().color(QtWidgets.QWidget.backgroundRole(gui.frame1))
            bgcolor = bgcol.name()
            gui.system_bgcolor = bgcolor
            if widget == gui.list2:
                if gui.list_with_thumbnail:
                    ht = '128px'
                else:
                    ht = '{}px'.format(gui.global_font_size)
                #gui.list2.setAlternatingRowColors(False)
                gui.list2.setStyleSheet("""QListWidget{{
                border-radius:3px;
                }}
                QListWidget:item {{
                height: {0};
                }}
                QListWidget:item:selected:active {{
                background:rgba(0, 0, 0, 20%);
                color: {1};
                }}
                """.format(ht, gui.list_text_color_focus))
            else:
                #gui.VerticalLayoutLabel_Dock3.setSpacing(0)
                #gui.VerticalLayoutLabel_Dock3.setContentsMargins(5, 5, 5, 5)
                for widget in [gui.list1, gui.list3, gui.list4, gui.list5, gui.list6]:
                    #widget.setAlternatingRowColors(False)
                    widget.setStyleSheet("""QListWidget{{
                    border-radius:3px; background-color :{1}; border: 1px solid rgba(0,0,0,20%);
                    }}
                    QListWidget:item {{
                    height: {height}px;
                    }}
                    QListWidget:item:selected:active {{
                    background:rgba(0, 0, 0, 10%);
                    color: {0};
                    }}
                    """.format(gui.list_text_color_focus, bgcolor, height=gui.global_font_size*3))
                if gui.list_with_thumbnail:
                    ht = '128px'
                else:
                    ht = '{}px'.format(gui.global_font_size)
                #gui.list2.setAlternatingRowColors(False)
                gui.list2.setStyleSheet("""QListWidget{{
                border-radius:3px;background-color :{2}; border: 1px solid rgba(0,0,0,20%);
                }}
                QListWidget:item {{
                height: {0};
                }}
                QListWidget:item:selected:active {{
                background:rgba(0, 0, 0, 20%);
                color: {1};
                }}
                """.format(ht, gui.list_text_color_focus, bgcolor))
            
            gui.dockWidget_3.setStyleSheet("""
                QFrame{{
                    background-color:{color};
                    border: 1px solid rgba(0, 0, 0, 40%)
                    }};
                """.format(color=bgcolor)
                )
            gui.text.setStyleSheet("""
                    border-radius:3px; background-color :{1}; border: 1px solid rgba(0,0,0,20%);
                    """.format(gui.list_text_color_focus, bgcolor))
            gui.cover_label.setStyleSheet("""
                    border-radius:3px; background-color :{1}; border: 1px solid rgba(0,0,0,20%);
                    """.format(gui.list_text_color_focus, bgcolor))
            gui.list_poster.setStyleSheet("""
                    QListWidget{{
                    font: {bold} {size}px {font};
                    border-radius:3px;background-color :{bgcolor}; border: 1px solid rgba(0,0,0,20%);
                    }}
                    QListWidget:item {{
                    height: 312px;
                    width:256px;
                    }}
                    """.format(bgcolor=bgcolor,
                               size=gui.global_font_size, font=gui.global_font,
                               bold=gui.font_bold)
                    )
            gui.player_opt.setStyleSheet("""
                    QPushButton{{max-height:64px;
                                font: {bold} {size}px {font};}}
                    """.format(bold=font_bold, size=gui.global_font_size, font=gui.global_font))
            for widget in [gui.progress, gui.progressEpn]:
                    widget.setStyleSheet("""QProgressBar{{
                    background-color:{bgcolor};
                    text-align: center;}}
                    
                    QProgressBar:chunk {{
                    background-color:{bgcolor};
                    }}""".format(bgcolor=bgcolor))
            
        elif theme == 'dark':
            alpha = '30%'
            qbtn = '10%'
            if gui.list_with_thumbnail:
                height = '128px'
            else:
                height = '{}px'.format(gui.global_font_size*3)
            red, green, blue = gui.bg_color_widget_dark_theme
            redc, greenc, bluec = gui.bg_color_control_frame
            redm, greenm, bluem = gui.bg_color_dark_theme
            gui.list2.setStyleSheet("""QListWidget{{
                color:{1};background:rgba({red},{green},{blue},30%);border:rgba(0,0,0,30%);
                font: {bold} {size}px {font};
                }}
                QListWidget:item {{
                height: {0};
                }}
                QListWidget:item:selected:active {{
                background:rgba(0, 0, 0, 20%);
                color: {2};
                }}
                QListWidget:item:inactive {{
                    color:{1};background:rgba(0,0,0,0%);border:rgba(0,0,0,0%);
                    font: {bold} {size}px {font};
                    }}
                QMenu{{
                color: white;
                background: rgba({redm}, {greenm}, {bluem}, 50%);border: rgba(0,0,0, 30%);
                padding: 2px;
                }}
                QMenu::item{{
                font: {font} {size}px {font};
                color: {1};
                background:rgba({redm}, {greenm}, {bluem}, 50%);border: rgba(0,0,0, 30%);
                padding: 4px; margin: 2px 2px 2px 10px;
                }}
                QMenu::item:selected{{
                color: {2};
                background:rgba(0, 0, 0, 20%);border: rgba(0,0,0, 30%);
                }}
                """.format(height, gui.list_text_color, gui.list_text_color_focus,
                           bold=font_bold, font=gui.global_font, size=gui.global_font_size,
                           red=red, blue=blue, green=green,
                           redm=redm, greenm=greenm, bluem=bluem)
                        )
            if widget != gui.list2:
                for widget_item in ([gui.line, gui.text, gui.cover_label, gui.frame1, gui.frame,
                                gui.torrent_frame, gui.float_window,
                                gui.search_on_type_btn, gui.tab_6, gui.tab_5]): 
                    if widget_item == gui.tab_6:
                        alpha = '20%'
                    else:
                        alpha = '30%'
                    if widget_item == gui.frame1:
                        font_size = '10px'
                        if not font_bold:
                            font_size = ''
                        redt, greent, bluet = (redc, greenc, bluec)
                    else:
                        font_size = ''
                        redt, greent, bluet = (red, green, blue)
                    widget_item.setStyleSheet("""
                        color:{color};
                        font: {bold} {size}px {font};
                        background:rgba({red},{green},{blue},{alpha});border:rgba(0,0,0,{alpha});
                        """.format(alpha=alpha, color=gui.list_text_color, font=gui.global_font,
                                   bold=font_bold, size=gui.global_font_size,
                                   red=redt, green=greent, blue=bluet)
                                )
                for frame in [gui.frame2, gui.frame_web, gui.dockWidget_3, gui.goto_epn,
                        gui.frame_extra_toolbar.child_frame, gui.frame_extra_toolbar.tab_frame,
                        gui.frame_extra_toolbar.subtitle_frame]:
                    bg = '30%'
                    if frame == gui.dockWidget_3:
                        qbtn = '50%'
                    else:
                        qbtn = '10%'
                    if frame in [gui.frame_extra_toolbar.child_frame,
                                 gui.frame_extra_toolbar.tab_frame,
                                 gui.frame_extra_toolbar.subtitle_frame]:
                        label_alpha = '0%'
                        new_height = int(gui.frame_height/2.4)
                        min_height = 'height: {}px'.format(new_height)
                        gui.logger.debug('min-height-box={}'.format(min_height))
                    elif frame == gui.frame2:
                        label_alpha = '30%'
                        qbtn = "30%"
                        min_height = 'max-height: {}px'.format(gui.frame2.height())
                    else:
                        label_alpha = '10%'
                        min_height = 'max-height: 30px'
                        
                    frame.setStyleSheet("""
                        QFrame{{color:white;background:rgba({red},{green},{blue},{alpha});border:rgba(0,0,0,{alpha});}}
                        QPushButton{{color:{color};background:rgba(0,0,0,{btn});border:rgba(0,0,0,{btn});
                        {min_height}; font: {bold} {size}px {font};}}
                        QPushButton::hover{{background-color: yellow;color: black;}}
                        QLineEdit{{
                            color:white;background:rgba(0,0,0,{label_alpha});
                            {min_height};border:rgba(0, 0, 0, {label_alpha}); font: {bold} {size}px {font};
                            }}
                        QLabel{{
                            color:{color};background:rgba(0,0,0,{label_alpha});
                            {min_height};border:rgba(0, 0, 0, {label_alpha});font: {bold} {size}px {font};
                            }}
                        QComboBox {{
                        color: {color};
                        selection-color:yellow;background:rgba(0,0,0,{btn});
                        border:rgba(0, 0, 0, 10%);
                        padding: 2px 0px 2px 4px;
                        font: {bold} {size}px {font};
                        }}
                        QComboBox::hover{{background-color: rgba(0,0,0,60%);color: {color};}}
                        QComboBox::drop-down {{
                        width: 22px;
                        border: 2px;
                        color:white;
                        }}
                        QComboBox QAbstractItemView{{
                        background-color: rgb({redm},{greenm},{bluem});
                        border-radius: 0px;
                        color: {color};
                        font: {bold} {size}px {font};
                        }}
                        QComboBox::focus {{
                        background-color:rgba(0,0,0,60%);color: {focus};
                        }}
                        QComboBox::down-arrow {{
                        width: 2px;
                        height: 2px;
                        }}
                        
                        QSlider:groove:horizontal {{
                            height: 8px;
                            background:rgba(0, 0, 0, 30%);
                            margin: 2px 0;
                            }}
                        QSlider:handle:horizontal {{
                            background: qlineargradient(
                                x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
                            border: 1px solid #5c5c5c;
                            width: 8px;
                            margin: -2px 0; 
                            border-radius: 3px;
                        }}
                        QSlider:QToolTip {{
                            font : {bold} {size}px {font};
                            color: {color};
                            background:rgb(56,60,74);
                            padding: 1px 2px 1px 2px;
                        }}
                        QCheckBox{{
                            color:{color};background:rgba(0,0,0,0%);
                            border:rgba(0, 0, 0, 10%); font: {bold} {size}px {font};
                            {min_height};
                            }}
                        QDoubleSpinBox{{
                            color:{color};background:rgba(0,0,0,{btn});
                            border:rgba(0, 0, 0, 10%); font: {bold} {font};
                            {min_height};
                            }}
                        QDoubleSpinBox::up-button{{
                            max-height:32px;
                            }}
                        QDoubleSpinBox::down-button{{
                            max-height:32px;
                            }}
                            
                        QSpinBox{{
                            color:{color};background:rgba(0,0,0,{btn});
                            border:rgba(0, 0, 0, 10%); font: {bold} {font};
                            {min_height};
                            }}
                        QSpinBox::up-button{{
                            max-height:32px;
                            }}
                        QSpinBox::down-button{{
                            max-height:32px;
                            }}
                        """.format(
                            alpha=bg, btn=qbtn, color=gui.list_text_color,
                            focus=gui.list_text_color_focus, bold=font_bold,
                            size=gui.global_font_size, font=gui.global_font,
                            label_alpha=label_alpha, min_height=min_height,
                            red=red, green=green, blue=blue,
                            redm=redm, greenm=greenm, bluem=bluem,
                            size_label=gui.global_font_size+4
                            )
                        )
                gui.player_opt.setStyleSheet("""
                    QFrame{{color:white;background:rgba({red},{green},{blue},30%);border:rgba(0,0,0,30%);}}
                    QPushButton{{max-height:64px;
                                background:rgba({red},{green},{blue},40%);
                                border:rgba(0, 0, 0, 30%);
                                font: {bold} {size}px {font};}}
                    QPushButton::hover{{background-color: yellow;color: black;}}
                    """.format(red=redc, green=greenc, blue=bluec,
                               bold=font_bold, size=gui.global_font_size, font=gui.global_font))
                
                gui.settings_box.setStyleSheet("""
                        QFrame{{color:white;background:rgba({red},{green},{blue},{alpha});border:rgba(0,0,0,{alpha});}}
                        QTabWidget{{
                            color:{color};
                            border:rgba(0,0,0,{alpha});background:rgb(56,60,74);
                            background-color:rgba(0,0,0,{alpha});
                            }}
                        QTabWidget:pane {{
                            color:{color};font: {bold} {size}px {font};
                            border:rgba(0,0,0,{alpha});background:rgba(56,60,74, {alpha});
                        }}
                        
                        QTabBar {{
                            color:{color};font: {bold} {size}px {font};
                            border:rgba(0,0,0,{alpha});background:rgba(56,60,74, {alpha});
                            background-color:rgba(0,0,0,{alpha});
                        }}
                        
                        QTabBar:tab{{
                            color:{color};background:rgba({red},{green},{blue}, {alpha});
                        }}
                        
                        QTabBar:tab:selected{{
                            color:{color};background:rgba(0,0,0, 20%);
                        }}
                        
                        QListWidget{{
                            color:{color};background:rgba(0,0,0,30%);border:rgba(0,0,0,30%);
                            font: {bold} {size}px {font};
                        }}
                        QListWidget:item {{
                            height: 30px;
                        }}
                        QListWidget:item:selected:active {{
                            background:rgba(0, 0, 0, 20%);
                            color: {focus};
                        }}
                        
                        QPushButton{{color:{color};background:rgba(0,0,0,{btn});border:rgba(0,0,0,{btn});
                        max-height:40px; font: {bold} {size}px {font};}}
                        QPushButton::hover{{background-color: yellow;color: black;}}
                        QLineEdit{{color:{color};background:rgba(0,0,0,10%);
                        max-height:40px;border:rgba(0, 0, 0, 10%); font: {bold} {size}px {font};}}
                        QTextEdit{{color:{color};background:rgba(0,0,0,10%);
                        border:rgba(0, 0, 0, 10%); font: {bold} {size}px {font};}}
                        
                        QCheckBox{{color:{color};background:rgba(0,0,0,10%);
                        border:rgba(0, 0, 0, 10%); font: {bold} {font};}}
                        
                        QScrollBar{{ background: rgba(0,0,0,30%);
                        }}
                        
                        QScrollBar::handle{{ background: rgba(54,60,74,30%);
                        border-radius:4px;
                        }}
                        
                        QScrollBar::add-line{{ background: rgba(0,0,0,0%);
                        }}
                        
                        QScrollBar::sub-line{{ background: rgba(0,0,0,0%);
                        }}
                        
                        QLabel{{color:{color};background:rgba(0,0,0,0%);
                        max-height:40px;border:rgba(0, 0, 0, 10%);font: {bold} {size}px {font};}}
                        QComboBox {{
                        color: {color};
                        selection-color:yellow;background:rgba(0,0,0,{btn});
                        border:rgba(0, 0, 0, 10%);
                        padding: 0px 2px 0px 4px;
                        font: {bold} {size}px {font};
                        max-height: 40px;
                        }}
                        QComboBox QAbstractItemView{{
                        background-color: rgb({redm},{greenm},{bluem});
                        border-radius: 0px;
                        border-color:rgb({redm}, {greenm}, {bluem});
                        color: {color};
                        font: {bold} {size}px {font};
                     }}
                        QComboBox::hover{{background-color: rgba(0,0,0,40%);color: {color};}}
                        QComboBox::drop-down {{
                        width: 22px;
                        border: 2px;
                        color:white;
                        }}
                        QComboBox::focus {{
                        background-color:rgba(0,0,0,40%);color: {focus};
                        }}
                        QComboBox::down-arrow {{
                        width: 2px;
                        height: 2px;
                        }}""".format(
                            alpha=bg, btn=qbtn, color=gui.list_text_color,
                            focus=gui.list_text_color_focus, bold=font_bold,
                            size=gui.global_font_size, font=gui.global_font,
                            red=red, blue=blue, green=green,
                            redm=redm, greenm=greenm, bluem=bluem,
                            size_label=gui.global_font_size+4)
                        )
                
                for widget in [gui.progress, gui.progressEpn]:
                    widget.setStyleSheet("""QProgressBar{{
                    color:white;
                    background:rgba({red}, {green}, {blue}, 30%);
                    border:rgba(0, 0, 0, 1%) ;
                    border-radius: 1px;
                    text-align: center;}}
                    
                    QProgressBar:chunk {{
                    background-color:rgba(0,0,0,30%);
                    width: 10px;
                    margin: 0.5px;
                    }}""".format(red=redc, green=greenc, blue=bluec))
                gui.slider.setStyleSheet("""QSlider:groove:horizontal {{
                    height: 8px;
                    border:rgba(0, 0, 0, 30%);
                    background:rgba({red}, {green}, {blue}, 30%);
                    margin: 2px 0;
                    }}
                    QSlider:handle:horizontal {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
                    border: 1px solid #5c5c5c;
                    width: 2px;
                    margin: -2px 0; 
                    border-radius: 3px;
                    }}
                    QToolTip {{
                    font : {bold} {size}px {font};
                    color: {color};
                    background:rgb({red}, {green}, {blue});
                    padding: 1px 2px 1px 2px;
                    }}
                    """.format(
                            alpha=bg, color=gui.list_text_color,
                            bold=font_bold, size=gui.global_font_size,
                            font=gui.global_font, red=redc, green=greenc, blue=bluec
                            )
                        )
                gui.list_poster.setStyleSheet("""
                    QListWidget{{
                    color:{0};
                    background:rgba({red}, {green}, {blue}, 35%);border:rgba(0, 0, 0, 35%);
                    font: {bold} {size}px {font};
                    }}
                    QListWidget:item {{
                    height: 312px;
                    width:256px;
                    }}
                    QListWidget:item:selected:active {{
                    background:rgba(0, 0, 0, 30%);
                    color: {1};
                    }}
                    QListWidget:item:inactive {{
                    color:{0};
                    background:rgba(0, 0, 0, 0%);border:rgba(0, 0, 0, 0%);
                    font: {bold} {size}px {font};
                    }}
                    QMenu{{
                    color: white;
                    background: rgb(56,60,74);border: rgba(0,0,0, 30%);
                    padding: 2px;
                    }}
                    QMenu::item{{
                    color: {0};
                    background:rgb(56,60,74);border: rgba(0,0,0, 30%);
                    padding: 4px; margin: 2px 2px 2px 10px;
                    }}
                    QMenu::item:selected{{
                    color: {1};
                    background:rgba(0, 0, 0, 20%);border: rgba(0,0,0, 30%);
                    }}
                    """.format(gui.thumbnail_text_color, gui.thumbnail_text_color_focus,
                               size=gui.global_font_size, font=gui.global_font,
                               bold=font_bold, red=red, blue=blue, green=green)
                    )
                #gui.VerticalLayoutLabel_Dock3.setSpacing(0)
                #gui.VerticalLayoutLabel_Dock3.setContentsMargins(5, 5, 5, 5)
                for widget in [gui.list1, gui.list3, gui.list4, gui.list5, gui.list6, gui.player_menu]:
                    widget.setStyleSheet("""QListWidget{{
                    color:{0};background:rgba({red},{green},{blue},30%);border:rgba(0,0,0,30%);
                    font: {bold} {size}px {font};
                    }}
                    QListWidget:item {{
                    height: {height}px;
                    }}
                    QListWidget:item:selected:active {{
                    background:rgba(0, 0, 0, 20%);
                    color: {1};
                    }}
                    
                    QListWidget:item:inactive {{
                    color:{0};background:rgba(0,0,0,0%);border:rgba(0,0,0,0%);
                    font: {bold} {size}px {font};
                    }}
                    QMenu{{
                    color: {1};
                    background: rgba({redm},{greenm},{bluem}, 50%);border: rgba(0,0,0, 30%);
                    padding: 2px;
                    }}
                    QMenu::item{{
                    font: {font};
                    color: {0};
                    background:rgba({redm},{greenm},{bluem}, 50%);border: rgba(0,0,0, 30%);
                    padding: 4px; margin: 2px 2px 2px 10px;
                    }}
                    QMenu::item:selected{{
                    color: {1};
                    background:rgba(0, 0, 0, 20%);border: rgba(0,0,0, 30%);
                    }}
                    """.format(gui.list_text_color, gui.list_text_color_focus,
                               bold=font_bold, font=gui.global_font, height=gui.global_font_size*3,
                               red=red, green=green, blue=blue, size=gui.global_font_size,
                               redm=redm, greenm=greenm, bluem=bluem)
                            )
