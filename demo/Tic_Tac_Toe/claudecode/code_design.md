# 井字棋 (Tic-Tac-Toe) 项目设计文档

> 本文档记录整体架构、每个模块的职责、关键技术决策与"踩过的坑"，方便下次直接依据本文档继续修改，无需重新读全部代码猜设计意图。

## 1. 运行环境

- Python 3.11
- PySide6 6.11（GUI 框架）
- Pillow（`pip install Pillow`，用于程序化生成占位背景图 / 木纹贴图，无需任何外部美术素材）

## 2. 目录结构

```
Tic_Tac_Toe/
├── main.py                      # 入口
├── core/
│   └── board.py                 # 棋盘状态 + 胜负判断（纯 Python，无 Qt 依赖）
├── ai_model/
│   └── ai_player.py              # AI 接口契约（用户自行实现 get_ai_action）
├── ui/
│   ├── styles.py                 # 颜色/QSS/尺寸/资源路径 —— 唯一的样式真源
│   ├── app_window.py              # 顶层无边框窗口 + 页面切换 + 拖动
│   ├── main_menu.py               # 主菜单页面
│   └── game_page.py               # 双人 / AI 通用棋盘页面
├── resources/
│   ├── generate_resources.py      # 用 Pillow 程序化生成占位图/木纹贴图
│   ├── main_bg.png                # 运行时自动生成（首次运行后落盘，之后不会重新生成）
│   ├── game_bg.png                # 同上
│   ├── wood_frame.png             # 棋盘外框木纹（深色）
│   └── wood_cell.png              # 棋盘格子木纹（浅色）
└── claudecode/
    └── code_design.md             # 本文档
```

## 3. 整体架构

### 3.1 单窗口 + QStackedWidget，而非多个独立窗口

`AppWindow`（`ui/app_window.py`）是唯一的顶层 `QMainWindow`：
- `Qt.FramelessWindowHint`：无边框
- `setFixedSize(600, 800)`：固定尺寸（`WINDOW_WIDTH`/`WINDOW_HEIGHT` 定义在 `ui/styles.py`）
- 构造时通过 `QGuiApplication.primaryScreen().availableGeometry()` 计算坐标并 `move()` 到屏幕居中
- 内部持有一个 `QStackedWidget`，`MainMenuPage` 和 `GamePage` 是两个可切换的页面

选择这个方案而不是"每个界面一个独立无边框窗口"，是因为无边框窗口没有系统标题栏，多个独立顶层窗口会重复处理"居中 / 拖动"逻辑；单窗口 + 页面切换只需写一次。

### 3.2 无边框窗口的拖动

`AppWindow` 重写了 `mousePressEvent` / `mouseMoveEvent` / `mouseReleaseEvent`，记录鼠标按下时相对窗口左上角的偏移量 `_drag_offset`，移动时用 `event.globalPosition().toPoint() - self._drag_offset` 计算新位置并 `move()`。这是无边框窗口的标准写法（没有系统标题栏就没有原生拖动）。

### 3.3 页面切换与状态重置

`AppWindow.open_game_page(mode)`：
- 若已有旧的 `GamePage` 实例，先 `stack.removeWidget()` + `deleteLater()` 销毁
- 重新 `GamePage(mode, self)` 创建全新实例，`addWidget` 后 `setCurrentWidget`

**关键设计**：每次进入棋盘页面都新建实例而不是复用/reset，这样保证棋盘状态、回合、AI 先后手等所有实例变量都是全新的，不会有"上一局的残留状态"这类 bug。

`return_to_menu()` 是反向操作：切回主菜单 + 销毁当前 `GamePage`。

## 4. 核心逻辑：`core/board.py`

- 棋盘用长度为 9 的字符串/列表表示，下标 `row*3+col`：`'0'`=空，`'1'`=X，`'2'`=O。
- 这个编码和 AI 接口 `get_ai_action(board_state: str)` 的入参格式完全一致（`board.to_string()` 直接可传给 AI 函数），不需要任何转换层。
- `check_winner()` 遍历 8 条线（3 行 + 3 列 + 2 对角线），返回 `'X'` / `'O'` / `'draw'` / `None`（对局继续）。

这个模块完全不依赖 Qt，可以脱离 GUI 单独单元测试。

## 5. AI 接口契约：`ai_model/ai_player.py`

```python
def get_ai_action(board_state: str) -> tuple[int, int]:
    """
    Args:
        board_state: 长度为9的字符串，'0'=空, '1'=X, '2'=O
    Returns:
        tuple: (row, col)，取值范围均为 0-2
    """
    pass
```

函数体目前是 `pass`（返回 `None`），留给用户后续接入强化学习模型。调用方（`GamePage._do_ai_move`）**不信任**这个函数的返回值，做了三层校验（见第 7.4 节），任何异常或非法返回都会被优雅地捕获，不会导致程序崩溃。

## 6. 样式集中管理：`ui/styles.py`

这是全项目**唯一**定义颜色/尺寸/QSS/资源路径的地方，其他模块只 `import` 常量，不在别处硬编码样式字符串。想改配色、字体、棋盘大小、贴图路径，只需要改这一个文件。

关键常量：
- `COLOR_X` / `COLOR_O`：棋子颜色（红/青）
- `CELL_SIZE`（140）/ `BOARD_SPACING`（10）/ `BOARD_MARGIN`（20）：格子大小、格子间距、棋盘内边距
- `BOARD_FRAME_SIZE = CELL_SIZE*3 + BOARD_SPACING*2 + BOARD_MARGIN*2`：**棋盘外框的固定尺寸由这三个数联算出来**，不是拍脑袋写死的数字（早期版本写死过 `CELL_SIZE*3+40`，比实际布局需要的尺寸小了 20px，棋盘会被内部按钮撑大，与预设尺寸不符——现已修复，任何改动 `CELL_SIZE`/`BOARD_SPACING`/`BOARD_MARGIN` 都会自动联动）
- `RESOURCES_DIR` / `MAIN_BG_PATH` / `GAME_BG_PATH` / `WOOD_FRAME_PATH` / `WOOD_CELL_PATH`：资源绝对路径（统一转成 `/` 分隔，QSS `url()` 在 Windows 下不接受反斜杠）
- 各种 `*_QSS` 字符串常量：主菜单标题、主菜单/游戏页背景、菜单按钮、返回按钮、棋盘外框、棋盘格子

`resources/generate_resources.py` 也会 `from ui.styles import CELL_SIZE, BOARD_FRAME_SIZE`，保证生成的木纹贴图像素尺寸和实际渲染尺寸完全一致（见第 8 节）。

## 7. 棋盘页面：`ui/game_page.py`

### 7.1 双人 / AI 模式复用同一个类

`GamePage(mode, app_window)`，`mode` 取值 `'pvp'` 或 `'ai'`。两种模式共用同一套 UI 构建代码 (`_build_ui`)、同一套落子/胜负判断逻辑，只在"轮到谁走"和"是否需要调用 AI"上分支。

### 7.2 棋盘 UI 结构

```
GamePage (QWidget)
├── 顶部：返回主菜单按钮（左对齐）
├── 居中：QFrame#boardFrame（木纹背景 + 渐变描边）
│   └── QGridLayout 3x3 个 QPushButton（每个都是木纹背景的格子）
```

### 7.3 落子与回合流程

```
点击格子 (_on_cell_clicked)
  → 若游戏已结束 / 若轮到 AI（AI 模式下玩家点击应无效）/ 若格子非空 → 直接 return，忽略点击
  → _place_mark：写入 board，格子按钮显示文字 + 对应颜色样式，禁用该按钮
  → _check_end：检查胜负，若有结果则弹窗 + 返回主菜单
  → _switch_turn：切换 X/O
  → 若轮到 AI（AI 模式），QTimer.singleShot(400ms) 延迟触发 _do_ai_move（模拟"AI思考"，纯体验优化，非必需）
```

### 7.4 AI 回合与异常处理（`_do_ai_move`）

调用 `get_ai_action(board.to_string())` 后做严格校验：
1. 返回值必须是长度为 2 的 `tuple`
2. `row`、`col` 必须是 `int`
3. `(row, col)` 必须是棋盘上一个合法的空位（`board.is_valid_move`）

任意一步失败，或调用过程中抛出任何异常，统一进入 `except Exception` 分支 → `_on_ai_failure()`：弹窗提示"AI仍在学习中..." → 点确定后返回主菜单。**这是当前 `get_ai_action` stub（返回 `None`）下的预期行为** —— 用户接入真实 AI 模型后，只要返回值合法，这条路径就不会被触发。

### 7.5 AI 模式"先后手选择"弹窗的时机（重要，踩过两次坑）

**需求**：进入 AI 模式后需要询问"AI 先手"还是"我先手"。

**最终方案**（`GamePage.__init__` + `_setup_ai_first_mover`）：

```python
def __init__(self, mode, app_window):
    ...
    self._build_ui()          # 棋盘界面在这里已经完整搭好
    if self.mode == "ai":
        QTimer.singleShot(0, self._setup_ai_first_mover)   # 推迟到下一次事件循环

def _setup_ai_first_mover(self):
    QApplication.processEvents()      # 强制把棋盘的绘制刷新到屏幕
    ai_first = ask_first_mover(self)  # 再弹窗
    ...
    if self.ai_mark == self.current_mark:
        QTimer.singleShot(400, self._do_ai_move)
```

**为什么不能在 `__init__` 里直接同步弹窗**：`QMessageBox.exec()` 是阻塞调用，如果在 `GamePage.__init__()`（此时页面还没有被 `AppWindow.open_game_page` 加入 `QStackedWidget`、也没有被设为当前页面）里直接调用，会导致"棋盘界面还没真正显示出来，弹窗就先弹出了"，用户体验上感觉很突兀。

**为什么不能提前到主菜单点击按钮时弹窗**：这是本项目实际踩过的第一个坑——最初为了解决上面那个问题，把询问逻辑挪到了 `MainMenuPage` 点击"AI模式"按钮的回调里（弹窗先于页面切换）。这样确实避免了"棋盘画完后弹窗"的观感，但产品期望的效果其实是相反的：**应该先完整切换到棋盘界面，弹窗再紧跟着立刻出现**，而不是停留在主菜单上问。

**最终确认的正确时序**（已用户验收）：
1. 点击"AI模式" → `AppWindow.open_game_page("ai")` 同步执行完，`GamePage` 已经是 `QStackedWidget` 当前显示的页面（棋盘、背景、木纹全部渲染完毕的状态已经生效）
2. `QTimer.singleShot(0, ...)` 排的回调在下一次事件循环触发，此时先 `QApplication.processEvents()` 把棋盘的绘制真正刷到屏幕上
3. 紧接着（同一时刻，人眼无法察觉延迟）弹出"AI先手/我先手"选择框

验证方法：用 `QT_QPA_PLATFORM=offscreen` + monkeypatch `QMessageBox.exec`/`QApplication.processEvents` 埋点，断言 `open_game_page()` 调用返回时 `stack.currentWidget()` 已经是 `GamePage`，且弹窗此时还未触发；只有手动 `pump` 事件循环后弹窗才出现。

### 7.6 返回主菜单确认框

`_on_back_clicked`：`QMessageBox.question("是否放弃此对局？")`，`Yes` 才调用 `app_window.return_to_menu()`，`No`/关闭 则什么都不做（弹窗本身关闭即可，不需要额外处理）。

## 8. 资源生成：`resources/generate_resources.py`

### 8.1 为什么改用 Pillow 而不是 QPixmap/QPainter

最初考虑用 PySide6 自带的 `QPixmap`/`QPainter` 生成占位图（不需要额外依赖），但用户明确要求"如果 PIL 好用就直接装 PIL"，所以改成 `pip install Pillow` + Pillow 生成。优点：不依赖 `QApplication` 上下文，`ensure_resources()` 可以在创建 `QApplication` 之前调用（`main.py` 里确实是这个顺序）。

### 8.2 「不按最终显示尺寸生成图片」是新手常踩的坑，这里特意避开了

四张图全部按照**最终渲染的精确像素尺寸**生成：
- `main_bg.png` / `game_bg.png`：600×800（等于 `WINDOW_WIDTH`/`WINDOW_HEIGHT`）
- `wood_frame.png`：`BOARD_FRAME_SIZE × BOARD_FRAME_SIZE`（从 `ui/styles.py` 导入，随 `CELL_SIZE`/`BOARD_SPACING`/`BOARD_MARGIN` 自动联动）
- `wood_cell.png`：`CELL_SIZE × CELL_SIZE`

因为尺寸精确匹配，QSS 里用 `background-image: url(...); background-repeat: no-repeat; background-position: center;` 即可原样铺满，不需要任何缩放，不会因为拉伸/裁切产生变形或缝隙。**如果以后要改棋盘大小（改 `CELL_SIZE` 等），只需要删除 `resources/wood_*.png` 让它们在下次启动时按新尺寸重新生成即可**（`ensure_resources()` 只在文件不存在时才生成，不会自动检测尺寸是否匹配，这是一个已知的限制，见第 10 节"已知限制"）。

### 8.3 图片风格

- **背景图**（`main_bg.png` / `game_bg.png`）：`_vertical_gradient()` 用 `Image.linear_gradient("L")` + `ImageOps.colorize()` 做垂直渐变（主菜单深蓝紫，游戏页深棕黑，呼应木纹主题），叠加 `_add_vignette()`（用高斯模糊过的椭圆蒙版做暗角，`Image.composite` 让中心保持原图、边缘变暗），主菜单额外叠加几个半透明超大 "X"/"O" 水印（`_draw_watermark_shapes`）。右下角有一行低透明度小字标注"占位背景图 · xxx.png"，提醒这是占位图、可替换。
- **木纹贴图**（`wood_frame.png` 深色 / `wood_cell.png` 浅色）：`_wood_texture()` 纯程序化生成，无需任何外部素材——用 `random.Random(seed)` 生成若干条正弦波浪线（模拟木材纹理），画在半透明 RGBA 图层上再和底色合成，`GaussianBlur(1)` 柔化，最后加一层很浅的暗角增加立体感。`seed` 固定，所以每次重新生成的图案是一致的（除非改 `seed` 或改算法）。

### 8.4 `ensure_resources()` 的幂等性

```python
def ensure_resources() -> None:
    for filename, builder in _BUILDERS.items():
        path = os.path.join(_RESOURCES_DIR, filename)
        if not os.path.exists(path):
            builder().save(path, "PNG")
```

只在文件不存在时才生成，`main.py` 每次启动都会调用，但正常情况下第二次运行开始就是纯粹的"文件存在检查"，不会有任何生成开销，也不会覆盖用户手动替换的美术资源。

## 9. 一个必须记住的 Qt 坑：`WA_StyledBackground`

**现象**：最初版本的 `MainMenuPage`、`GamePage` 用 `border-image: url(...) stretch stretch` 设置背景图，运行后背景全是 Qt 默认的浅灰色 `(239,239,239)`，图片完全没有生效。

**根因**：普通 `QWidget`（以及 `QFrame`）默认**不会**根据 QSS 的 `background-*` 属性绘制背景，除非显式设置 `self.setAttribute(Qt.WA_StyledBackground, True)`。这是 Qt 的默认行为（避免所有自定义 QWidget 都承担一次额外的样式绘制开销），很多人第一次踩这个坑都会以为是路径写错了或者 QSS 语法错了。

**修复**：
- `MainMenuPage.__init__`、`GamePage._build_ui`、棋盘 `QFrame#boardFrame` 三处都加了 `setAttribute(Qt.WA_StyledBackground, True)`
- 同时把 `border-image`（会连带接管边框绘制，没法再叠加渐变描边）换成 `background-image`（背景层和边框层独立，`BOARD_FRAME_QSS` 里的渐变描边 `border-color` 才能和木纹背景同时生效）

**验证方法**：`QPixmap` 渲染 widget 后用 `QImage.pixelColor()` 采样像素，确认不再是默认的 `(239,239,239)`，而是背景图/木纹图对应位置的颜色。

## 10. 已知限制 / 后续可以做但目前没做的事

- `ensure_resources()` 不会检测已生成图片的尺寸是否和当前 `ui/styles.py` 里的常量匹配——改了 `CELL_SIZE` 之类的尺寸常量后，需要**手动删除** `resources/wood_frame.png`、`resources/wood_cell.png`（以及如果改了窗口尺寸，还要删 `main_bg.png`/`game_bg.png`）让它们重新生成。
- 没有做"连线高亮"（获胜时高亮三连的格子），目前只弹窗提示结果。
- AI"思考延迟"（`QTimer.singleShot(400, ...)`）是写死的 400ms，纯粹是体验优化，不代表任何真实的推理耗时。
- `get_ai_action` 目前是 stub（`pass` / 返回 `None`），AI 模式下每一局都会触发"AI仍在学习中..."的异常兜底路径，这是**预期行为**，等接入真实模型后才会真正对弈。

## 11. 如何验证改动没有破坏现有功能（推荐流程）

1. `python -m py_compile` 跑一遍改动到的文件，排除语法错误。
2. `QT_QPA_PLATFORM=offscreen python -c "..."` 无头模式，用 `QPixmap.render()` + `QImage.pixelColor()` 采样关键像素点，验证背景/贴图颜色符合预期。
3. 涉及弹窗时机的改动，用 monkeypatch `QMessageBox.exec` / `QApplication.processEvents` 埋点断言调用顺序（见 7.5 节的方法），不要只靠肉眼观察——弹窗时序的 bug 很容易在 headless 测试里被掩盖或误判。
4. 最后 `python main.py` 实际跑一遍（或 `timeout N python main.py` 确认不会立即崩溃退出）。
