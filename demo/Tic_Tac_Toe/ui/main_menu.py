"""主界面：标题 + 双人模式/AI模式/退出游戏 三个按钮。"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy

from ui.styles import MAIN_TITLE_QSS, MENU_BUTTON_QSS, MAIN_MENU_BG_QSS


class MainMenuPage(QWidget):
    def __init__(self, app_window):
        super().__init__()
        self.app_window = app_window

        # ---- 背景图：换图只需替换 resources/main_bg.png ----
        self.setObjectName("mainMenuRoot")
        # QWidget 默认不按 QSS 绘制背景，需开启该属性背景图/背景色才会生效
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(MAIN_MENU_BG_QSS)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 60, 40, 60)

        title = QLabel("井 字 棋")
        title.setObjectName("titleLabel")
        title.setStyleSheet(MAIN_TITLE_QSS)
        title.setAlignment(Qt.AlignHCenter)
        layout.addWidget(title)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.btn_pvp = QPushButton("双人模式")
        self.btn_ai = QPushButton("AI模式")
        self.btn_exit = QPushButton("退出游戏")
        for btn in (self.btn_pvp, self.btn_ai, self.btn_exit):
            btn.setStyleSheet(MENU_BUTTON_QSS)
            btn.setFixedHeight(56)
            layout.addWidget(btn)
            layout.addSpacing(16)

        self.btn_pvp.clicked.connect(lambda: self.app_window.open_game_page("pvp"))
        self.btn_ai.clicked.connect(lambda: self.app_window.open_game_page("ai"))
        self.btn_exit.clicked.connect(self._on_exit)

    def _on_exit(self):
        from PySide6.QtWidgets import QApplication
        QApplication.instance().quit()
