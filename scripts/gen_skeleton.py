"""生成知识库框架 SVG：坐标由代码计算，保证嵌套包含关系成立 + 文字不溢出 + 描边色可区分。

用法：python gen_frame.py  -> 输出 frame.svg
设计原则：
  1. 坐标全部算出，不手填——手填正是上次容器装不下子框的原因
  2. 每个子框必须被父框包含（含 20px 内缩），程序断言
  3. 每行文字实测宽度，程序断言
  4. 描边色两两 RGB 距离可区分，程序断言
"""
import os
import sys

# 用脚本自身位置定位同目录的 measure_text，避免把本机绝对路径写死（换机器就 ImportError）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measure_text import text_width  # noqa: E402

# ---------- 配色：结构同一家族深浅分层，不用绿蓝混搭 ----------
C = {
    # 外层容器（由深到浅，表示层级由内到外递减的注意力）
    "focus_fill":   "#042C53",   # 知识层：最深，主体
    "focus_stroke": "#85B7EB",
    "box_fill":     "#0C447C",
    "box_stroke":   "#85B7EB",
    # 内层卡片：同蓝家族更亮一档，色相一致但明度分明
    "card_fill":    "#0F3A63",
    "card_stroke":  "#378ADD",
    # 枢纽页：比卡片再亮一档（层级更高）
    "hub_fill":     "#185FA5",
    "hub_stroke":   "#B5D4F4",
    # 语义色：只读用暖色，工具用紫
    "warn_fill":    "#412402",
    "warn_stroke":  "#EF9F27",
    "tool_fill":    "#26215C",
    "tool_stroke":  "#CECBF6",
}
T = {  # 文字
    "t_focus": "#E6F1FB", "t_focus2": "#B5D4F4",
    "t_card":  "#E6F1FB", "t_card2": "#B5D4F4",
    "t_warn":  "#FAEEDA", "t_warn2": "#FAC775",
    "t_tool":  "#EEEDFE", "t_tool2": "#CECBF6",
    "t_dim":   "#888780",
}

PAD = 20          # 父框到子框的内缩
GAP = 10
LINE = 17         # 行距

asserts = []


def check(cond, msg):
    asserts.append((bool(cond), msg))
    if not cond:
        print("  [断言失败]", msg)


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(rgb(a), rgb(b))) ** 0.5


def text(x, y, s, size, fill, box_right, pad=18, anchor="start"):
    """生成一个 text，并断言不溢出。

    box_right = 该文本所在框的**右边界 x**（不是宽度）。
    可用宽度 = box_right - pad - x。
    """
    w = text_width(s, size)
    avail = box_right - pad - x
    check(w <= avail, f'文字溢出「{s[:24]}」{w:.0f} > {avail:.0f}')
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text x="{x}" y="{y}" font-family="var(--font-sans)" '
            f'font-size="{size}" fill="{fill}"{a}>{s}</text>')


def box(x, y, w, h, fill, stroke, r=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="0.5"/>')


def parent_child_ok(px, py, pw, ph, cx, cy, cw, ch, name):
    inside = (cx >= px + PAD - 0.5 and cy >= py + PAD - 0.5 and
              cx + cw <= px + pw - PAD + 0.5 and cy + ch <= py + ph - PAD + 0.5)
    check(inside, f"{name} 未被父框包含（父 {py}..{py+ph} / 子 {cy}..{cy+ch}）")


out = []
H = 0

# ============ 标题 ============
out.append(text(40, 26, "示例：某知识库　实测 2026-10-05", 14, T["t_focus2"], 680, 0))

# ============ ① 规则层 ============
y = 40
r1_h = 70
out.append(box(40, y, 600, r1_h, C["box_fill"], "#B5D4F4", 10))
out.append(text(58, y + 21, "① 规则层　唯一规则来源", 13, T["t_focus"], 640))
out.append(text(58, y + 41, "AGENTS.md 13 条款　·　AGENTS-CHANGELOG.md 附属（不单独生效）", 12, T["t_focus2"], 640))
out.append(text(58, y + 59, "PORTABILITY.md 移植说明　·　kb.config.json 目录配置", 12, T["t_focus2"], 640))
y_next = y + r1_h

# ============ ② 知识层（主体，外框高度由子框实测推出）============
y = y_next + 24
# 先算子框
hub_h = 26 + 3 * LINE + 12          # 枢纽页
card_h = 26 + 2 * LINE + 12# 四个卡片
inner_w = (600 - 2 * PAD - GAP) // 2

kids = []  # (x, y, w, h)
ky = y + 34
kids.append((40 + PAD, ky, 600 - 2 * PAD, hub_h))
cy1 = ky + hub_h + GAP
kids.append((40 + PAD, cy1, inner_w, card_h))
kids.append((40 + PAD + inner_w + GAP, cy1, inner_w, card_h))
cy2 = cy1 + card_h + GAP
kids.append((40 + PAD, cy2, inner_w, card_h))
kids.append((40 + PAD + inner_w + GAP, cy2, inner_w, card_h))
r2_h = (cy2 + card_h + PAD) - y     # 由子框推出，不手填

out.append(box(40, y, 600, r2_h, C["focus_fill"], C["focus_stroke"], 12))
out.append(text(58, y + 22, "② 知识层　知识库 wiki/　100 页 · 1,706 链接 · 零孤立页", 13, T["t_focus"], 640))

# 枢纽页
hx, hy, hw, hh = kids[0]
parent_child_ok(40, y, 600, r2_h, hx, hy, hw, hh, "枢纽页")
out.append(box(hx, hy, hw, hh, C["hub_fill"], C["hub_stroke"]))
out.append(text(hx + 16, hy + 20, "三张枢纽页　唯一的跨层入口", 13, T["t_card"], hx + hw))
for i, s in enumerate(["目录 index　21KB · 117 出链",
                       "日志 log　123KB · 95 出链",
                       "综述 overview　21KB · 66 出链"]):
    out.append(text(hx + 16, hy + 39 + i * LINE, s, 12, T["t_card2"], hx + hw))

# 四个卡片
cards = [
    ("资料摘要 sources　24 页 · 143KB", "一份逻辑资料一页", "答：这份资料讲了什么"),
    ("实体 entities　27 页 · 100KB", "一个实体一页", "答：它在本库处于什么位置"),
    ("概念 concepts　37 页 · 171KB", "数量最多 · 均 4KB", "含法律线 11 页"),
    ("分析 analyses　9 页 · 81KB", "均 9KB · 最厚", "查询与体检的沉淀出口"),
]
for k, (kx, ky2, kw, kh) in enumerate(kids[1:]):
    parent_child_ok(40, y, 600, r2_h, kx, ky2, kw, kh, f"卡片{k+1}")
    out.append(box(kx, ky2, kw, kh, C["card_fill"], C["card_stroke"]))
    lx = kx - 40                       # 局部坐标
    out.append(text(kx + 16, ky2 + 20, cards[k][0], 12, T["t_card"], kx + kw))
    out.append(text(kx + 16, ky2 + 40, cards[k][1], 12, T["t_card2"], kx + kw))
    out.append(text(kx + 16, ky2 + 58, cards[k][2], 12, T["t_card2"], kx + kw))

y_next = y + r2_h

# ============ ③ 原料层 ============
y = y_next + 24
r3_h = 70
out.append(box(40, y, 600, r3_h, C["warn_fill"], C["warn_stroke"], 10))
out.append(text(58, y + 21, "③ 原料层　原始资料 raw/　只读", 13, T["t_warn"], 640))
out.append(text(58, y + 41, "已摄入 49 项（23 文件 + 智泊分 P 子目录）　·　待处理 1", 12, T["t_warn2"], 640))
out.append(text(58, y + 59, "不改动 · 不改名 · 不删除　唯一例外：读不了的移入 待处理/", 12, T["t_warn2"], 640))
y_next = y + r3_h

# ============ ④a ④b 产出与工具 ============
y = y_next + 24
r4_h = 70
half = (600 - GAP) // 2
out.append(box(40, y, half, r4_h, C["tool_fill"], C["tool_stroke"], 10))
out.append(text(58, y + 21, "④a 工具层　C 库　10 文件", 13, T["t_tool"], 40 + half))
out.append(text(58, y + 41, "tools/scripts 4 个 .py", 12, T["t_tool2"], 40 + half))
out.append(text(58, y + 59, "skill/ 仅 1 个 README（空置）", 12, T["t_tool2"], 40 + half))

x2 = 40 + half + GAP
out.append(box(x2, y, 600 - half - GAP, r4_h, C["tool_fill"], C["tool_stroke"], 10))
out.append(text(x2 + 18, y + 21, "④b 产出层", 13, T["t_tool"], 640))
out.append(text(x2 + 18, y + 40, "报告 reports/ 18 份", 12, T["t_tool2"], 640))
out.append(text(x2 + 18, y + 56, "体检 9 · 摄入 6 · 其他 3", 12, T["t_tool2"], 640))
out.append(text(x2 + 18, y + 72 - 14, "output/ 182 文件 · 15 顶层项", 12, T["t_tool2"], 640))
y_next = y + r4_h

# ============ 四库循环 ============
y = y_next + 24
r5_h = 26 + 3 * LINE + 12
out.append(box(40, y, 600, r5_h, C["focus_fill"], C["box_stroke"], 10))
out.append(text(58, y + 21, "四库循环　这套框架真正在跑的东西", 13, T["t_focus"], 640))
for i, (s, c) in enumerate([
        ("A 需求（人提问）→ B 知识（wiki 编译一次，之后保持最新）", T["t_focus2"]),
        ("→ C 工具（脚本判定能否复用）→ D 成果（报告 / 交付物）", T["t_focus2"]),
        ("→ 交回 A 的需求方判断成果对错 —— 判断者必须是使用者", T["t_warn2"])]):
    out.append(text(58, y + 40 + i * LINE, s, 12, c, 600))
y_next = y + r5_h

# ============ 守卫层 ============
y = y_next + 16
r6_h = 26 + 3 * LINE + 12
out.append(box(40, y, 600, r6_h, C["focus_fill"], C["box_stroke"], 10))
out.append(text(58, y + 21, "守卫层　kb-lint.py　12 项检查 · 退出码 0 全绿", 13, T["t_focus"], 640))
for i, s in enumerate([
        "单页合法性 6：重名 · 断链 · 异常字符 · 标签越界 · 空文件 · 规则绑定",
        "字段时效 2：字段越界 · Star/Fork 缺抓取日期　　规模 1：日志条目数",
        "页间关系 3：未被摘要覆盖 · 实体页缺边界说明 · 别名冲突"]):
    out.append(text(58, y + 40 + i * LINE, s, 12, T["t_focus2"], 640))
y_next = y + r6_h

# 脚注
H = y_next + 28
out.append(text(40, y_next + 24, "全图为本轮实测。检查项数以 kb-lint 实际输出条数为准：12 项", 12, T["t_dim"], 680, 0))

# ============ 描边色可区分性 ============
print("\n=== 描边色两两 RGB 距离（阈值 > 40，须明显可分）===")
pairs = [
    ("知识层外框 / 卡片", C["focus_stroke"], C["card_stroke"]),
    ("知识层外框 / 枢纽页", C["focus_stroke"], C["hub_stroke"]),
    ("卡片 / 枢纽页",     C["card_stroke"], C["hub_stroke"]),
    ("规则层 / 知识层外框", "#B5D4F4", C["focus_stroke"]),
    ("原料层 / 工具层",    C["warn_stroke"], C["tool_stroke"]),
]
for name, a, b in pairs:
    d = dist(a, b)
    check(d > 40, f"{name} 描边色太接近 {d:.1f}")
    print(f"  {name:22s} {a} vs {b}  {d:6.1f}")

# ============ 汇总 ============
bad = [m for ok, m in asserts if not ok]
print(f"\n共 {len(asserts)} 条断言")
if bad:
    print(f"失败 {len(bad)} 条：")
    for m in bad:
        print("  -", m)
    sys.exit(1)
print("全部通过")

svg = (f'<svg viewBox="0 0 680 {H}" width="100%" role="img" '
       f'xmlns="http://www.w3.org/2000/svg">\n'
       f'<title>知识库四层框架全貌图</title>\n'
       f'<desc>坐标由代码计算并断言，文字不溢出，嵌套包含关系成立</desc>\n'
       f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" '
       f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
       f'<path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" '
       f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
       f'</marker></defs>\n' + "\n".join(out) + "\n</svg>")

p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frame.svg")
open(p, "w", encoding="utf-8").write(svg)
print(f"\n已写出 {p}  viewBox 0 0 680 {H}")
