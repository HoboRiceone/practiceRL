"""AI 对战接口契约。

调用方（ui/game_page.py）会在 AI 回合时调用 get_ai_action，并对返回值做严格校验：
- 必须是 (row, col) 二元组
- row、col 必须在 0-2 范围内
- 目标格必须为空

任何异常，或返回值不满足以上条件，都会被调用方视为“AI 尚未就绪”，
弹窗提示后返回主菜单，不会导致程序崩溃。
"""

def get_ai_action(board_state: str) -> tuple[int, int]:
    """
    Args:
        board_state: 长度为9的字符串，从左到右、从上到下表示棋盘。
                     '0'=空, '1'=X, '2'=O
    Returns:
        tuple: (row, col)，取值范围均为 0-2
    """
    pass
