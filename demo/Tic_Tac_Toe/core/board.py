"""井字棋棋盘状态与胜负判断，不依赖任何 Qt 组件。"""

EMPTY = '0'
X = '1'
O = '2'

MARK_TO_LABEL = {X: 'X', O: 'O'}

# 8 种胜利组合：3 行、3 列、2 条对角线（下标 0-8，按行优先展开）
_WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # 行
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # 列
    (0, 4, 8), (2, 4, 6),             # 对角线
]


class Board:
    def __init__(self):
        self.cells = [EMPTY] * 9

    def get(self, row: int, col: int) -> str:
        return self.cells[row * 3 + col]

    def set(self, row: int, col: int, mark: str) -> None:
        self.cells[row * 3 + col] = mark

    def is_valid_move(self, row: int, col: int) -> bool:
        if not (0 <= row <= 2 and 0 <= col <= 2):
            return False
        return self.get(row, col) == EMPTY

    def to_string(self) -> str:
        return ''.join(self.cells)

    def check_winner(self):
        """返回 'X'/'O'（获胜方）、'draw'（平局）或 None（对局继续）。"""
        for a, b, c in _WIN_LINES:
            if self.cells[a] != EMPTY and self.cells[a] == self.cells[b] == self.cells[c]:
                return MARK_TO_LABEL[self.cells[a]]
        if EMPTY not in self.cells:
            return 'draw'
        return None
