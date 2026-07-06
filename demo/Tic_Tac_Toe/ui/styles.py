"""集中管理颜色、字体、QSS、资源路径常量。想改配色/字体/间距/贴图，只需改这个文件。"""
import os

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800

# ---- 棋子颜色：X 默认红色，O 默认青色，改这里即可全局生效 ----
COLOR_X = "#e63946"
COLOR_O = "#48cae4"

COLOR_TITLE = "#f1faee"
COLOR_BUTTON_BG = "#1d3557"
COLOR_BUTTON_BG_HOVER = "#457b9d"
COLOR_BUTTON_TEXT = "#f1faee"

# ---- 棋盘尺寸：格子大小/间距/边距，改这里会联动棋盘外框大小与木纹贴图尺寸 ----
CELL_SIZE = 140
BOARD_SPACING = 10
BOARD_MARGIN = 20
BOARD_FRAME_SIZE = CELL_SIZE * 3 + BOARD_SPACING * 2 + BOARD_MARGIN * 2

# ---- 资源路径：占位图/木纹贴图都在 resources/ 目录下自动生成 ----
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")


def _resource_url(filename: str) -> str:
    return os.path.join(RESOURCES_DIR, filename).replace("\\", "/")


MAIN_BG_PATH = _resource_url("main_bg.png")
GAME_BG_PATH = _resource_url("game_bg.png")
WOOD_FRAME_PATH = _resource_url("wood_frame.png")
WOOD_CELL_PATH = _resource_url("wood_cell.png")

# ---- 主菜单标题：想换艺术字体/大小/发光效果，改这里 ----
MAIN_TITLE_QSS = f"""
QLabel#titleLabel {{
    color: {COLOR_TITLE};
    font-family: "Segoe Print", "华文行楷", "STXingkai", "楷体", sans-serif;
    font-size: 48px;
    font-weight: bold;
}}
"""

# ---- 主菜单/游戏页背景：图片按窗口固定尺寸生成，居中铺满不裁切 ----
MAIN_MENU_BG_QSS = f"""
QWidget#mainMenuRoot {{
    background-image: url({MAIN_BG_PATH});
    background-repeat: no-repeat;
    background-position: center;
}}
"""

GAME_PAGE_BG_QSS = f"""
QWidget#gamePageRoot {{
    background-image: url({GAME_BG_PATH});
    background-repeat: no-repeat;
    background-position: center;
}}
"""

# ---- 主菜单按钮样式：想换按钮圆角/配色/字号，改这里 ----
MENU_BUTTON_QSS = f"""
QPushButton {{
    background-color: {COLOR_BUTTON_BG};
    color: {COLOR_BUTTON_TEXT};
    border-radius: 16px;
    font-size: 22px;
    font-weight: bold;
    padding: 14px;
}}
QPushButton:hover {{
    background-color: {COLOR_BUTTON_BG_HOVER};
}}
QPushButton:pressed {{
    background-color: #14213d;
}}
"""

# ---- 返回按钮样式 ----
BACK_BUTTON_QSS = f"""
QPushButton {{
    background-color: rgba(29, 53, 87, 200);
    color: {COLOR_BUTTON_TEXT};
    border-radius: 10px;
    font-size: 14px;
    padding: 6px 14px;
}}
QPushButton:hover {{
    background-color: {COLOR_BUTTON_BG_HOVER};
}}
"""

# ---- 棋盘容器：深色木纹贴图当底，配色渐变描边营造"木质相框"质感，想换风格改这里 ----
BOARD_FRAME_QSS = f"""
QFrame#boardFrame {{
    border-radius: 24px;
    border: 5px solid;
    border-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                   stop:0 #f4a261, stop:1 #2a9d8f);
    background-image: url({WOOD_FRAME_PATH});
    background-repeat: no-repeat;
    background-position: center;
}}
"""

# ---- 棋盘格子按钮：浅色木纹贴图 + 悬停描边高亮，想换木色/字号改这里 ----
_CELL_BASE_QSS = f"""
QPushButton {{
    background-image: url({WOOD_CELL_PATH});
    background-repeat: no-repeat;
    background-position: center;
    border: 2px solid rgba(0, 0, 0, 60);
    border-radius: 14px;
    font-size: 56px;
    font-weight: bold;
}}
QPushButton:hover {{
    border: 3px solid #ffd166;
}}
"""

CELL_QSS_EMPTY = _CELL_BASE_QSS + "QPushButton { color: #333333; }"
CELL_QSS_X = _CELL_BASE_QSS + f"QPushButton {{ color: {COLOR_X}; }}"
CELL_QSS_O = _CELL_BASE_QSS + f"QPushButton {{ color: {COLOR_O}; }}"
