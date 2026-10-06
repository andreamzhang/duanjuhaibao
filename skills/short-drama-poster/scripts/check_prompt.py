# -*- coding: utf-8 -*-
"""短剧海报 · 提示词预检（发往生成工具前跑一遍）。

检查项:
  [FAIL] 片名未逐字出现在提示词中（--title 提供；含标点与大小写）
  [FAIL] 出现电影节 / 奖项 / 桂冠类违禁词
  [WARN] 出现真实平台 / 品牌名（海报画面不得出现平台标识）
  [WARN] 出现空泛词（高级感/完美光影/电影级打光…，应改写为可执行描述）
  [WARN] 未见“逐字 / verbatim”锁定句

用法:
    python check_prompt.py <提示词文件> --title "Mafia Princess: Back from Hell"
退出码: 有 FAIL 返回 1，否则 0。
"""
from __future__ import annotations

import argparse
from pathlib import Path

FESTIVAL_TERMS = [
    "电影节", "影展", "桂冠", "金棕榈", "金熊", "金狮", "奥斯卡", "戛纳", "柏林电影节", "圣丹斯",
    "official selection", "palme d'or", "sundance", "cannes", "academy award", "award winner",
]

PLATFORM_TERMS = [
    "reelshort", "dramabox", "shortmax", "goodshort", "flextv",
    "netflix", "disney", "hbo", "prime video",
    "tiktok", "抖音", "快手", "微博", "youtube",
    "爱奇艺", "腾讯视频", "优酷", "芒果tv",
]

VAGUE_TERMS = ["高级感", "完美光影", "电影级打光", "电影级布光", "大片质感", "氛围感"]


def main() -> int:
    ap = argparse.ArgumentParser(description="短剧海报提示词预检")
    ap.add_argument("file", help="提示词文件（.md/.txt）")
    ap.add_argument("--title", required=True, help="片名原文（含标点，逐字符）")
    args = ap.parse_args()

    text = Path(args.file).read_text(encoding="utf-8")
    low = text.lower()
    fails = []
    warns = []

    if args.title and args.title not in text:
        fails.append(
            '片名未逐字出现："%s"（检查拼写/大小写/标点；两行排版时标点应在行尾、引号内为原文）' % args.title
        )
    else:
        print('[PASS] 片名逐字命中："%s"' % args.title)

    for t in FESTIVAL_TERMS:
        if t.lower() in low:
            fails.append("电影节/奖项类违禁词：%s" % t)

    for t in PLATFORM_TERMS:
        if t in low:
            warns.append("真实平台/品牌名：%s（确认仅用于文内说明；画面中不得出现平台 logo）" % t)

    for t in VAGUE_TERMS:
        if t in text:
            warns.append("空泛词：%s（改为可执行描述，见 references/design-aesthetics.md 翻译表）" % t)

    if ("verbatim" not in low) and ("逐字" not in text) and ("逐字符" not in text):
        warns.append('未见"逐字/verbatim"锁定句（建议写"逐字精确呈现（verbatim）、不多不少一个字符"）')

    print("== 预检: %s ==" % Path(args.file).name)
    for w in warns:
        print("[WARN] %s" % w)
    for f in fails:
        print("[FAIL] %s" % f)
    print("结果: %s（FAIL %d / WARN %d）" % ("不通过" if fails else "通过", len(fails), len(warns)))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
