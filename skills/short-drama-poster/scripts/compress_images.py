# -*- coding: utf-8 -*-
"""
批量压缩超限图片（短剧海报素材上传用）。

约定：
- 压缩版放原路径，文件名加「_压缩」后缀；原图保留不覆盖。
- 默认只处理 >10MiB 的图（Windows 显示口径），压到 <=9.5MiB
  （9.5MiB 同时低于 10MiB 与 10MB 两种口径，双保险）。

用法:
    python compress_images.py <目录> [--upload-limit-mib 10] [--target-mib 9.5]

依赖: Pillow
"""
import glob
import os
import sys

from PIL import Image

EXTS = ('.png', '.jpg', '.jpeg', '.webp')


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else '.'
    upload_limit = 10.0
    target = 9.5
    argv = sys.argv
    if '--upload-limit-mib' in argv:
        upload_limit = float(argv[argv.index('--upload-limit-mib') + 1])
    if '--target-mib' in argv:
        target = float(argv[argv.index('--target-mib') + 1])

    select = int(upload_limit * 1024 * 1024)   # 只处理超过上传上限的图
    limit = int(target * 1024 * 1024)          # 压到这个大小以内

    targets = [
        f for f in sorted(glob.glob(os.path.join(folder, '*')))
        if os.path.splitext(f)[1].lower() in EXTS
        and os.path.getsize(f) > select
        and '_压缩' not in os.path.basename(f)
    ]
    if not targets:
        print('没有超过上限的图片。')
        return

    for src in targets:
        base, ext = os.path.splitext(src)
        out = base + '_压缩' + ext
        orig = os.path.getsize(src)
        im = Image.open(src).convert('RGB')
        w0, h0 = im.size
        print(f'== {os.path.basename(src)}  原始 {orig / 1048576:.2f} MiB, {w0}x{h0}')

        def save(img, path):
            if ext.lower() == '.png':
                img.save(path, 'PNG', optimize=True, compress_level=9)
            else:
                img.save(path, 'JPEG', quality=90)

        save(im, out)
        size = os.path.getsize(out)
        print(f'   全分辨率优化: {size / 1048576:.2f} MiB')
        if size > limit:
            for s in (0.96, 0.93, 0.90, 0.87, 0.84, 0.80):
                w, h = int(w0 * s), int(h0 * s)
                save(im.resize((w, h), Image.LANCZOS), out)
                size = os.path.getsize(out)
                print(f'   缩放 {s:.0%} ({w}x{h}): {size / 1048576:.2f} MiB')
                if size <= limit:
                    break
        ok = 'OK' if size <= select else 'STILL-OVER'
        print(f'   => {os.path.basename(out)}  {size / 1048576:.2f} MiB ({size / 1e6:.2f} MB)  [{ok}]')


if __name__ == '__main__':
    main()
