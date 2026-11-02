"""量一段中英混排文本在给定字号下的渲染宽度（px）。

用途：写完 SVG 后校验每个 <text> 是否装得进它的框。
用法：python measure_text.py "文字" [字号] [框宽] [左内边距]

宽度模型（无字体度量库时的保守估算）：
  汉字 / 全角标点（含·「」【】等）≈ 1.00 em
  拉丁字母 / 数字 / 半角标点   ≈ 0.55 em
  空格≈ 0.28 em
刻意高估：宁可报"可能溢出"也不漏报。
"""
import sys
import unicodedata


def char_width(ch, size):
    if ch == " ":
        return 0.28 * size
    # 全角判定：East_Asian_Width 为 W 或 F
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 1.00 * size
    return 0.55 * size


def text_width(s, size):
    return sum(char_width(c, size) for c in s)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    s = sys.argv[1]
    size = float(sys.argv[2]) if len(sys.argv) > 2 else 12.0
    box_w = float(sys.argv[3]) if len(sys.argv) > 3 else None
    pad = float(sys.argv[4]) if len(sys.argv) > 4 else 18.0

    w = text_width(s, size)
    print(f"字号 {size}  字符数 {len(s)}")
    print(f"估算宽度 {w:.1f}px")
    for i, c in enumerate(s):
        pass
    if box_w:
        avail = box_w - 2 * pad
        mark = "OK  " if w <= avail else "溢出"
        print(f"框宽 {box_w}  内边距 {pad}  可用 {avail:.1f}  -> {mark}")
        if w > avail:
            # 给出可用的截断建议
            lo, hi = 0, len(s)
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if text_width(s[:mid], size) <= avail:
                    lo = mid
                else:
                    hi = mid - 1
            print(f"  最多容纳 {lo} 字：{s[:lo]}")
            if lo < len(s):
                print(f"  被截断：…{s[lo:]}")


if __name__ == "__main__":
    main()


def contrast_note():
    """对比色相距离：判断嵌套容器边框是否可区分。"""
    pairs = [
        ("旧版 知识层外框 vs 枢纽页", "#5DCAA5", "#9FE1CB"),
        ("新版 知识层外框 vs 枢纽页", "#85B7EB", "#5DCAA5"),
        ("新版 外框 vs 内部卡片",     "#85B7EB", "#5DCAA5"),
    ]
    def rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    for name, a, b in pairs:
        ra, rb = rgb(a), rgb(b)
        dist = sum((x - y) ** 2 for x, y in zip(ra, rb)) ** 0.5
        verdict = "太接近（不可区分）" if dist < 120 else "可区分"
        print(f"{name:28s} {a} vs {b}  RGB距离 {dist:6.1f}  -> {verdict}")
