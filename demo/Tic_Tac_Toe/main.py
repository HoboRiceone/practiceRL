"""程序入口：生成占位资源 -> 创建 QApplication -> 显示居中的无边框主窗口。"""
import sys

from resources.generate_resources import ensure_resources


def main():
    ensure_resources()

    from PySide6.QtWidgets import QApplication
    from ui.app_window import AppWindow

    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
