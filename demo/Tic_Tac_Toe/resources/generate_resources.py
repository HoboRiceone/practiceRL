"""自动生成占位背景图与木纹贴图（首次运行时），后续运行若文件已存在则跳过。

全部用 Pillow 程序化生成（渐变 + 描边水印 + 木纹纹理 + 暗角），
所有图片按照最终显示的固定像素尺寸生成，避免运行时缩放变形，
方便用户后续直接替换成正式美术资源（文件名保持不变即可）。
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from ui.styles import CELL_SIZE, BOARD_FRAME_SIZE

WIDTH, HEIGHT = 600, 800

_RESOURCES_DIR = os.path.dirname(os.path.abspath(__file__))

# ---- 想换主菜单/游戏背景配色，改这两组渐变色 ----
_MAIN_BG_TOP, _MAIN_BG_BOTTOM = (26, 26, 58), (12, 44, 74)
_GAME_BG_TOP, _GAME_BG_BOTTOM = (36, 26, 20), (14, 12, 10)

# ---- 想换木纹颜色，改这两组底色/纹理色（框深色、格浅色） ----
_WOOD_FRAME_BASE, _WOOD_FRAME_GRAIN = (69, 42, 24), (38, 21, 10)
_WOOD_CELL_BASE, _WOOD_CELL_GRAIN = (201, 160, 111), (156, 112, 67)


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for font_name in ("msyh.ttc", "simhei.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _vertical_gradient(width: int, height: int, top_color: tuple, bottom_color: tuple) -> Image.Image:
    base = Image.linear_gradient("L").resize((width, height))
    return ImageOps.colorize(base, black=top_color, white=bottom_color).convert("RGB")


def _add_vignette(img: Image.Image, amount: float = 0.3) -> Image.Image:
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    mx, my = int(w * 0.2), int(h * 0.2)
    draw.ellipse((-mx, -my, w + mx, h + my), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(min(w, h) // 6))
    darkened = ImageEnhance.Brightness(img).enhance(1 - amount)
    return Image.composite(img, darkened, mask)


def _draw_watermark_shapes(img: Image.Image, seed: int) -> Image.Image:
    rng = random.Random(seed)
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = _load_font(180)
    for _ in range(5):
        symbol = rng.choice(["X", "O"])
        x = rng.randint(-40, img.width - 60)
        y = rng.randint(-40, img.height - 60)
        draw.text((x, y), symbol, font=font, fill=(255, 255, 255, 16))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def _draw_corner_label(img: Image.Image, text: str) -> Image.Image:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = _load_font(14)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = 12
    pos = (img.width - tw - pad, img.height - th - pad)
    draw.text(pos, text, font=font, fill=(255, 255, 255, 80))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def _wood_texture(width: int, height: int, base_color: tuple, grain_color: tuple, seed: int) -> Image.Image:
    """程序化生成木纹：随机波浪纹理线 + 轻微模糊 + 暗角，无需外部素材。"""
    rng = random.Random(seed)
    img = Image.new("RGB", (width, height), base_color)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    num_lines = max(20, height // 5)
    for i in range(num_lines):
        y0 = rng.uniform(-10, height + 10)
        amplitude = rng.uniform(2, 7)
        frequency = rng.uniform(1.2, 3.5)
        phase = rng.uniform(0, math.tau)
        alpha = rng.randint(16, 55)
        points = [
            (x, y0 + amplitude * math.sin(x / max(width, 1) * math.pi * frequency + phase))
            for x in range(0, width + 6, 6)
        ]
        draw.line(points, fill=(*grain_color, alpha), width=rng.choice([1, 1, 2]))

    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    img = img.filter(ImageFilter.GaussianBlur(1))
    return _add_vignette(img, amount=0.18)


def _build_main_bg() -> Image.Image:
    img = _vertical_gradient(WIDTH, HEIGHT, _MAIN_BG_TOP, _MAIN_BG_BOTTOM)
    img = _draw_watermark_shapes(img, seed=1)
    img = _add_vignette(img, amount=0.32)
    return _draw_corner_label(img, "占位背景图 · main_bg.png")


def _build_game_bg() -> Image.Image:
    img = _vertical_gradient(WIDTH, HEIGHT, _GAME_BG_TOP, _GAME_BG_BOTTOM)
    img = _add_vignette(img, amount=0.38)
    return _draw_corner_label(img, "占位背景图 · game_bg.png")


def _build_wood_frame() -> Image.Image:
    return _wood_texture(BOARD_FRAME_SIZE, BOARD_FRAME_SIZE, _WOOD_FRAME_BASE, _WOOD_FRAME_GRAIN, seed=11)


def _build_wood_cell() -> Image.Image:
    return _wood_texture(CELL_SIZE, CELL_SIZE, _WOOD_CELL_BASE, _WOOD_CELL_GRAIN, seed=22)


_BUILDERS = {
    "main_bg.png": _build_main_bg,
    "game_bg.png": _build_game_bg,
    "wood_frame.png": _build_wood_frame,
    "wood_cell.png": _build_wood_cell,
}


def ensure_resources() -> None:
    for filename, builder in _BUILDERS.items():
        path = os.path.join(_RESOURCES_DIR, filename)
        if not os.path.exists(path):
            builder().save(path, "PNG")
