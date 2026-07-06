"""顶层窗口：无边框、固定尺寸、居中显示，内部用 QStackedWidget 切换页面。"""
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from ui.styles import WINDOW_WIDTH, WINDOW_HEIGHT
from ui.main_menu import MainMenuPage
from ui.game_page import GamePage


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle("井字棋")

        self._drag_offset = None

        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        self.main_menu = MainMenuPage(self)
        self.stack.addWidget(self.main_menu)
        self.stack.setCurrentWidget(self.main_menu)

        self._game_page = None
        self._center_on_screen()

    def _center_on_screen(self):
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        x = geo.x() + (geo.width() - self.width()) // 2
        y = geo.y() + (geo.height() - self.height()) // 2
        self.move(x, y)

    def open_game_page(self, mode: str):
        """mode: 'pvp' or 'ai'。每次进入都新建实例，保证棋盘状态重置。"""
        if self._game_page is not None:
            self.stack.removeWidget(self._game_page)
            self._game_page.deleteLater()
            self._game_page = None

        self._game_page = GamePage(mode, self)
        self.stack.addWidget(self._game_page)
        self.stack.setCurrentWidget(self._game_page)

    def return_to_menu(self):
        self.stack.setCurrentWidget(self.main_menu)
        if self._game_page is not None:
            self.stack.removeWidget(self._game_page)
            self._game_page.deleteLater()
            self._game_page = None

    # ---- 无边框窗口拖动 ----
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_offset = None
        super().mouseReleaseEvent(event)
