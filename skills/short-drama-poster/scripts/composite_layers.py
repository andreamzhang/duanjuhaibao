# -*- coding: utf-8 -*-
"""短剧海报 · 分层合成（底图层 + 标题层 → 网格定位合成）。

黑底白字用 screen、白底黑字用 multiply、透明层用 normal；
本地只做裁剪/缩放/移动/透明度；输出合成图 + grid.json（记录全部参数，便于复查与复用）。

用法:
    python composite_layers.py --base 底图.png --type 标题层.png \
        --out 合成.jpg --grid-out grid.json \
        [--canvas 1080x1440] [--type-box 0.06,0.64,0.88,0.16] \
        [--mode screen|multiply|normal] [--opacity 0.95]

--type-box: x,y,w,h —— 可全用画布比例（0-1），也可全用像素值；标题层在框内等比适配、居中。
依赖: Pillow（系统 Python311 已装）
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops


def parse_size(value: str):
    w, h = value.lower().split("x", 1)
    return int(w), int(h)


def parse_box(value: str, canvas):
    parts = [float(x.strip()) for x in value.split(",")]
    if len(parts) != 4:
        raise ValueError("--type-box 需要 4 个数值：x,y,w,h")
    cw, ch = canvas
    if all(0.0 <= v <= 1.0 for v in parts):
        x, y, w, h = parts
        return int(round(x * cw)), int(round(y * ch)), int(round(w * cw)), int(round(h * ch))
    return tuple(int(round(v)) for v in parts)


def cover(im: Image.Image, size) -> Image.Image:
    """等比放大后居中裁切铺满画布（底图用）。"""
    w, h = size
    iw, ih = im.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale + 0.5), int(ih * scale + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return im.crop((left, top, left + w, top + h))


def contain(im: Image.Image, bw: int, bh: int) -> Image.Image:
    """等比缩放到框内（标题层用）。"""
    iw, ih = im.size
    scale = min(bw / iw, bh / ih)
    nw, nh = max(1, int(iw * scale + 0.5)), max(1, int(ih * scale + 0.5))
    return im.resize((nw, nh), Image.LANCZOS)


def main() -> int:
    ap = argparse.ArgumentParser(description="短剧海报分层合成（底图 + 标题层）")
    ap.add_argument("--base", required=True, help="无字底图")
    ap.add_argument("--type", required=True, help="标题层（黑底白字 / 白底黑字 / 透明层）")
    ap.add_argument("--out", required=True, help="输出合成图（.jpg/.png）")
    ap.add_argument("--grid-out", required=True, help="输出网格 JSON（记录参数）")
    ap.add_argument("--canvas", default="1080x1440", help="画布尺寸，默认 1080x1440（3:4）；9:16 用 1080x1920")
    ap.add_argument("--type-box", default="0.06,0.64,0.88,0.16", help="标题层落位 x,y,w,h（比例或像素）")
    ap.add_argument("--mode", choices=["screen", "multiply", "normal"], default="screen",
                    help="黑底白字=screen；白底黑字=multiply；透明层=normal")
    ap.add_argument("--opacity", type=float, default=1.0, help="0-1，标题层整体不透明度")
    args = ap.parse_args()

    canvas = parse_size(args.canvas)
    base = cover(Image.open(args.base).convert("RGB"), canvas)

    type_im = Image.open(args.type)
    has_alpha = type_im.mode in ("RGBA", "LA", "PA") or "transparency" in type_im.info
    type_im = type_im.convert("RGBA" if has_alpha else "RGB")

    box = parse_box(args.type_box, canvas)
    x, y, bw, bh = box
    if bw <= 0 or bh <= 0:
        print("ERROR: --type-box 的宽/高必须大于 0")
        return 2
    fitted = contain(type_im, bw, bh)
    px, py = x + (bw - fitted.width) // 2, y + (bh - fitted.height) // 2
    opacity = max(0.0, min(1.0, args.opacity))

    if args.mode == "normal":
        layer = Image.new("RGBA", canvas, (0, 0, 0, 0))
        if has_alpha:
            layer.alpha_composite(fitted, (px, py))
        else:
            layer.paste(fitted, (px, py))
        if opacity < 1:
            alpha = layer.getchannel("A").point(lambda v: int(v * opacity))
            layer.putalpha(alpha)
        out = Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")
    else:
        # screen: 黑色=不改变底图；multiply: 白色=不改变底图
        neutral = (0, 0, 0) if args.mode == "screen" else (255, 255, 255)
        flat = Image.new("RGB", canvas, neutral)
        if has_alpha:
            flat.paste(fitted.convert("RGB"), (px, py), fitted.getchannel("A"))
        else:
            flat.paste(fitted, (px, py))
        blended = ImageChops.screen(base, flat) if args.mode == "screen" else ImageChops.multiply(base, flat)
        out = blended if opacity >= 1 else Image.blend(base, blended, opacity)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.suffix.lower() == ".png":
        out.save(out_path, optimize=True)
    else:
        out.save(out_path, quality=95)

    grid = {
        "canvas": f"{canvas[0]}x{canvas[1]}",
        "base": str(Path(args.base).resolve()),
        "type": str(Path(args.type).resolve()),
        "type_box_px": [x, y, bw, bh],
        "fitted_px": [px, py, fitted.width, fitted.height],
        "mode": args.mode,
        "opacity": opacity,
        "output": str(out_path.resolve()),
    }
    Path(args.grid_out).write_text(json.dumps(grid, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(grid, ensure_ascii=False, indent=2))
    print(f"OK → {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
