"""双人模式 / AI 模式共用的棋盘页面。"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QGridLayout,
    QPushButton, QMessageBox, QSizePolicy, QApplication,
)

from core.board import Board, EMPTY, X, O
from ai_model.ai_player import get_ai_action
from ui.styles import (
    BACK_BUTTON_QSS, BOARD_FRAME_QSS, CELL_QSS_EMPTY, CELL_QSS_X, CELL_QSS_O,
    CELL_SIZE, BOARD_SPACING, BOARD_MARGIN, BOARD_FRAME_SIZE, GAME_PAGE_BG_QSS,
)

_CELL_QSS = {EMPTY: CELL_QSS_EMPTY, X: CELL_QSS_X, O: CELL_QSS_O}
_MARK_LABEL = {X: "X", O: "O"}


def ask_first_mover(parent) -> bool:
    """弹窗询问 AI 模式的先后手，返回 True 表示 AI 先手。"""
    box = QMessageBox(parent)
    box.setWindowTitle("选择先后手")
    box.setText("请选择由谁先手：")
    ai_first_btn = box.addButton("AI 先手", QMessageBox.AcceptRole)
    box.addButton("我先手", QMessageBox.RejectRole)
    box.exec()
    return box.clickedButton() is ai_first_btn


class GamePage(QWidget):
    def __init__(self, mode: str, app_window):
        super().__init__()
        self.mode = mode
        self.app_window = app_window

        self.board = Board()
        self.current_mark = X  # X 永远先手
        self._game_over = False
        self.cell_buttons = {}

        # AI 模式下由 _setup_ai_first_mover 决定，先给个默认值
        self.human_mark = X
        self.ai_mark = O

        self._build_ui()

        if self.mode == "ai":
            # 用 0ms 定时器把弹窗推迟到下一次事件循环：
            # 这样棋盘界面先完整显示出来，弹窗紧接着立刻弹出，不会有明显停顿。
            QTimer.singleShot(0, self._setup_ai_first_mover)

    def _setup_ai_first_mover(self):
        # 强制先把棋盘界面的绘制刷新到屏幕上，弹窗再叠加上去，避免出现"棋盘还没画完就弹窗"的闪烁。
        QApplication.processEvents()

        ai_first = ask_first_mover(self)
        if ai_first:
            self.ai_mark, self.human_mark = X, O
        else:
            self.human_mark, self.ai_mark = X, O

        if self.ai_mark == self.current_mark:
            QTimer.singleShot(400, self._do_ai_move)

    # ------------------------------------------------------------------
    # UI 构建
    # ------------------------------------------------------------------
    def _build_ui(self):
        self.setObjectName("gamePageRoot")
        # QWidget 默认不按 QSS 绘制背景，需开启该属性背景图才会生效
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(GAME_PAGE_BG_QSS)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)

        top_row = QHBoxLayout()
        back_btn = QPushButton("返回主菜单")
        back_btn.setStyleSheet(BACK_BUTTON_QSS)
        back_btn.clicked.connect(self._on_back_clicked)
        top_row.addWidget(back_btn, alignment=Qt.AlignLeft)
        top_row.addStretch()
        root.addLayout(top_row)

        root.addStretch()

        board_frame = QFrame()
        board_frame.setObjectName("boardFrame")
        board_frame.setAttribute(Qt.WA_StyledBackground, True)
        board_frame.setStyleSheet(BOARD_FRAME_QSS)
        board_frame.setFixedSize(BOARD_FRAME_SIZE, BOARD_FRAME_SIZE)
        grid = QGridLayout(board_frame)
        grid.setSpacing(BOARD_SPACING)
        grid.setContentsMargins(BOARD_MARGIN, BOARD_MARGIN, BOARD_MARGIN, BOARD_MARGIN)

        for row in range(3):
            for col in range(3):
                btn = QPushButton("")
                btn.setFixedSize(CELL_SIZE, CELL_SIZE)
                btn.setStyleSheet(_CELL_QSS[EMPTY])
                btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                btn.clicked.connect(lambda _checked, r=row, c=col: self._on_cell_clicked(r, c))
                grid.addWidget(btn, row, col)
                self.cell_buttons[(row, col)] = btn

        center_row = QHBoxLayout()
        center_row.addStretch()
        center_row.addWidget(board_frame)
        center_row.addStretch()
        root.addLayout(center_row)

        root.addStretch()

    # ------------------------------------------------------------------
    # 落子与回合切换
    # ------------------------------------------------------------------
    def _on_cell_clicked(self, row: int, col: int):
        if self._game_over:
            return
        if self.mode == "ai" and self.current_mark == self.ai_mark:
            return  # 还没轮到玩家，点击无效
        if not self.board.is_valid_move(row, col):
            return

        self._place_mark(row, col, self.current_mark)
        if self._check_end():
            return
        self._switch_turn()

        if self.mode == "ai" and self.current_mark == self.ai_mark:
            QTimer.singleShot(400, self._do_ai_move)

    def _place_mark(self, row: int, col: int, mark: str):
        self.board.set(row, col, mark)
        btn = self.cell_buttons[(row, col)]
        btn.setText(_MARK_LABEL[mark])
        btn.setStyleSheet(_CELL_QSS[mark])
        btn.setEnabled(False)

    def _switch_turn(self):
        self.current_mark = O if self.current_mark == X else X

    def _check_end(self) -> bool:
        result = self.board.check_winner()
        if result is None:
            return False

        self._game_over = True
        self._disable_all_cells()
        QMessageBox.information(self, "对局结束", self._build_result_message(result))
        self.app_window.return_to_menu()
        return True

    def _build_result_message(self, result: str) -> str:
        if result == "draw":
            return "平局！"
        if self.mode == "pvp":
            role = "先手" if result == "X" else "后手"
            return f"{result}（{role}）获胜！"
        # AI 模式：更贴近玩家视角
        return "你获胜！" if result == self.human_mark else "AI 获胜！"

    def _disable_all_cells(self):
        for btn in self.cell_buttons.values():
            btn.setEnabled(False)

    # ------------------------------------------------------------------
    # AI 回合
    # ------------------------------------------------------------------
    def _do_ai_move(self):
        if self._game_over:
            return
        try:
            action = get_ai_action(self.board.to_string())
            if not (isinstance(action, tuple) and len(action) == 2):
                raise ValueError("AI 返回值格式不正确，需为 (row, col) 二元组")
            row, col = action
            if not (isinstance(row, int) and isinstance(col, int)):
                raise ValueError("AI 返回的坐标类型不正确")
            if not self.board.is_valid_move(row, col):
                raise ValueError("AI 返回了越界或已被占用的坐标")
        except Exception:
            self._on_ai_failure()
            return

        self._place_mark(row, col, self.ai_mark)
        if self._check_end():
            return
        self._switch_turn()

    def _on_ai_failure(self):
        self._game_over = True
        self._disable_all_cells()
        QMessageBox.information(self, "提示", "AI仍在学习中...")
        self.app_window.return_to_menu()

    # ------------------------------------------------------------------
    # 返回主菜单
    # ------------------------------------------------------------------
    def _on_back_clicked(self):
        reply = QMessageBox.question(
            self, "提示", "是否放弃此对局？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.app_window.return_to_menu()
