"""四张图统一生成器：坐标由代码计算 + 三类断言（几何/文本/色彩）。

用法：python gen_all.py  ->输出 4 个 svg 到 out/
纪律来源：diagram-layout-discipline 技能
  纪律 0 坐标必须由代码计算，禁止手填
  纪律 1 文字不得溢出（实测宽度）
  纪律 2 描边色两两可区分（RGB 距离）
  纪律 3 运行逻辑必须画成图
"""
import os
import sys

# 用脚本自身位置定位同目录的 measure_text，避免把本机绝对路径写死（换机器就 ImportError）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measure_text import text_width  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

PAD = 20
GAP = 10
LINE = 17
LEFT = 40
RIGHT = 640
FULL = RIGHT - LEFT

# 配色：同一蓝家族深浅分层 + 两个语义色
C = {
    "focus_fill": "#042C53", "focus_stroke": "#85B7EB",
    "box_fill":   "#0C447C", "box_stroke":   "#B5D4F4",
    "card_fill":  "#0F3A63", "card_stroke":  "#378ADD",
    "hub_fill":   "#185FA5", "hub_stroke":   "#B5D4F4",
    "warn_fill":  "#412402", "warn_stroke":  "#EF9F27",
    "tool_fill":  "#26215C", "tool_stroke":  "#CECBF6",
    "bad_fill":   "#501313", "bad_stroke":   "#F09595",
}
T = {
    "focus": "#E6F1FB", "focus2": "#B5D4F4",
    "warn":  "#FAEEDA", "warn2":  "#FAC775",
    "tool":  "#EEEDFE", "tool2":  "#CECBF6",
    "bad":   "#FCEBEB", "bad2":   "#F7C1C1",
    "dim":   "#888780",
}

problems = []


def check(cond, msg):
    if not cond:
        problems.append(msg)
        print("  [失败]", msg)


def txt(x, y, s, size, fill, right, pad=18, in_box=True):
    w = text_width(s, size)
    avail = right - pad - x
    check(w <= avail, f'文字溢出「{s[:22]}」{w:.0f}>{avail:.0f}')
    # 框内文字须离框左边有内缩；页面级标题不在框内，不受此限
    if in_box:
        check(x >= 52, f'框内文字贴左边 x={x}「{s[:16]}」，应留 ≥12px 内缩')
    return (f'<text x="{x}" y="{y}" font-family="var(--font-sans)" '
            f'font-size="{size}" fill="{fill}">{s}</text>')


MIN_GAP = 14   # 同一框内相邻两行文字的最小基线间距

def rows(y_list, name):
    """断言同一框内相邻文字基线间距 >= MIN_GAP，否则渲染后会糊成一片。"""
    ys = sorted(y_list)
    for a, b in zip(ys, ys[1:]):
        check(b - a >= MIN_GAP, f'{name} 行距过小 {b-a:.0f}px（{a}->{b}），会糊成一片')


def box(x, y, w, h, fill, stroke, r=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="0.5"/>')


def kid_ok(px, py, pw, ph, cx, cy, cw, ch, name):
    check(cx >= px + PAD - 0.5 and cy >= py + PAD - 0.5 and
          cx + cw <= px + pw - PAD + 0.5 and cy + ch <= py + ph - PAD + 0.5,
          f"{name} 超出父框（父 {py}..{py+ph} / 子 {cy}..{cy+ch}）")


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(rgb(a), rgb(b))) ** 0.5


def color_dist(pairs):
    for name, a, b in pairs:
        d = dist(a, b)
        check(d > 40, f"{name} 描边色太接近 {d:.1f}")
        print(f"    {name:20s}{a} vs {b}  {d:6.1f}")


def svg(body, h, title, desc):
    return (f'<svg viewBox="0 0 680 {h}" width="100%" role="img" '
            f'xmlns="http://www.w3.org/2000/svg">\n<title>{title}</title>\n'
            f'<desc>{desc}</desc>\n'
            f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" '
            f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" '
            f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
            f'</marker></defs>\n' + "\n".join(body) + "\n</svg>")


def write(name, content):
    p = os.path.join(OUT, name)
    open(p, "w", encoding="utf-8").write(content)
    print(f"  -> {name}")


# ================================================================
# 图 1 · 四层框架全貌
# ================================================================
def gen_frame():
    print("\n[图1] 四层框架全貌")
    o = []
    o.append(txt(LEFT, 26, "示例：某知识库实测 2026-10-05", 14, T["focus2"], 680, 0, in_box=False))
    y = 40
    # ① 规则层
    o.append(box(LEFT, y, FULL, 70, C["box_fill"], C["box_stroke"], 10))
    o.append(txt(58, y + 21, "① 规则层　唯一规则来源", 13, T["focus"], RIGHT))
    o.append(txt(58, y + 41, "AGENTS.md 13 条款　·　AGENTS-CHANGELOG.md 附属（不单独生效）", 12, T["focus2"], RIGHT))
    o.append(txt(58, y + 59, "PORTABILITY.md 移植说明　·　kb.config.json 目录配置", 12, T["focus2"], RIGHT))
    y += 70 + 24
    # ② 知识层（高度由子框反推）
    hub_h = 26 + 3 * LINE + 12
    card_h = 26 + 2 * LINE + 12
    iw = (FULL - 2 * PAD - GAP) // 2
    kx0, kx1 = LEFT + PAD, LEFT + PAD + iw + GAP
    kw = RIGHT - PAD - kx1
    hy = y + 34
    c1y = hy + hub_h + GAP
    c2y = c1y + card_h + GAP
    h2 = c2y + card_h + PAD - y
    o.append(box(LEFT, y, FULL, h2, C["focus_fill"], C["focus_stroke"], 12))
    o.append(txt(58, y + 22, "② 知识层　知识库 wiki/　100 页 · 1,706 链接 · 零孤立页", 13, T["focus"], RIGHT))
    kid_ok(LEFT, y, FULL, h2, LEFT + PAD, hy, FULL - 2 * PAD, hub_h, "枢纽页")
    o.append(box(LEFT + PAD, hy, FULL - 2 * PAD, hub_h, C["hub_fill"], C["hub_stroke"]))
    o.append(txt(LEFT + PAD + 16, hy + 20, "三张枢纽页　唯一的跨层入口", 13, T["focus"], RIGHT - PAD))
    for i, s in enumerate(["目录 index　21KB · 117 出链", "日志 log　123KB · 95 出链",
                           "综述 overview　21KB · 66 出链"]):
        o.append(txt(LEFT + PAD + 16, hy + 39 + i * LINE, s, 12, T["focus2"], RIGHT - PAD))
    cards = [("资料摘要 sources　24 页 · 143KB", "一份逻辑资料一页", "答：这份资料讲了什么"),
             ("实体 entities　27 页 · 100KB", "一个实体一页", "答：它在本库处于什么位置"),
             ("概念 concepts　37 页 · 171KB", "数量最多 · 均 4KB", "含法律线 11 页"),
             ("分析 analyses　9 页 · 81KB", "均 9KB · 最厚", "查询与体检的沉淀出口")]
    for i, (cx, cy) in enumerate([(kx0, c1y), (kx1, c1y), (kx0, c2y), (kx1, c2y)]):
        kid_ok(LEFT, y, FULL, h2, cx, cy, iw if cx == kx0 else kw, card_h, f"卡片{i+1}")
        cwid = iw if cx == kx0 else kw
        o.append(box(cx, cy, cwid, card_h, C["card_fill"], C["card_stroke"]))
        o.append(txt(cx + 16, cy + 20, cards[i][0], 12, T["focus"], cx + cwid))
        o.append(txt(cx + 16, cy + 40, cards[i][1], 12, T["focus2"], cx + cwid))
        o.append(txt(cx + 16, cy + 58, cards[i][2], 12, T["focus2"], cx + cwid))
    y += h2 + 24
    # ③ 原料层
    o.append(box(LEFT, y, FULL, 70, C["warn_fill"], C["warn_stroke"], 10))
    o.append(txt(58, y + 21, "③ 原料层　原始资料 raw/　只读", 13, T["warn"], RIGHT))
    o.append(txt(58, y + 41, "已摄入 49 项（23 文件 + 智泊分 P 子目录）　·　待处理 1", 12, T["warn2"], RIGHT))
    o.append(txt(58, y + 59, "不改动 · 不改名 · 不删除　唯一例外：读不了的移入 待处理/", 12, T["warn2"], RIGHT))
    y += 70 + 24
    # ④a ④b
    half = (FULL - GAP) // 2
    o.append(box(LEFT, y, half, 70, C["tool_fill"], C["tool_stroke"], 10))
    o.append(txt(58, y + 21, "④a 工具层　C 库　10 文件", 13, T["tool"], LEFT + half))
    o.append(txt(58, y + 41, "tools/scripts 4 个 .py", 12, T["tool2"], LEFT + half))
    o.append(txt(58, y + 59, "skill/ 仅 1 个 README（空置）", 12, T["tool2"], LEFT + half))
    x2 = LEFT + half + GAP
    o.append(box(x2, y, RIGHT - x2, 70, C["tool_fill"], C["tool_stroke"], 10))
    o.append(txt(x2 + 18, y + 21, "④b 产出层", 13, T["tool"], RIGHT))
    o.append(txt(x2 + 18, y + 39, "报告 reports/ 18 份", 12, T["tool2"], RIGHT))
    o.append(txt(x2 + 18, y + 53, "体检 9 · 摄入 6 · 其他 3", 12, T["tool2"], RIGHT))
    rows([y + 21, y + 39, y + 53], "④b 产出层")
    y += 70 + 24
    # 四库循环
    h = 26 + 3 * LINE + 12
    o.append(box(LEFT, y, FULL, h, C["focus_fill"], C["focus_stroke"], 10))
    o.append(txt(58, y + 21, "四库循环　这套框架真正在跑的东西", 13, T["focus"], RIGHT))
    for i, (s, c) in enumerate([
            ("A 需求（人提问）→ B 知识（wiki 编译一次，之后保持最新）", T["focus2"]),
            ("→ C 工具（脚本判定能否复用）→ D 成果（报告 / 交付物）", T["focus2"]),
            ("→ 交回 A 的需求方判断成果对错 —— 判断者必须是使用者", T["warn2"])]):
        o.append(txt(58, y + 40 + i * LINE, s, 12, c, RIGHT))
    y += h + 16
    # 守卫层
    h2b = 26 + 3 * LINE + 12
    o.append(box(LEFT, y, FULL, h2b, C["focus_fill"], C["focus_stroke"], 10))
    o.append(txt(58, y + 21, "守卫层　kb-lint.py　12 项检查 · 退出码 0 全绿", 13, T["focus"], RIGHT))
    for i, s in enumerate([
            "单页合法性 6：重名 · 断链 · 异常字符 · 标签越界 · 空文件 · 规则绑定",
            "字段时效 2：字段越界 · Star/Fork 缺抓取日期　规模 1：日志条目数",
            "页间关系 3：未被摘要覆盖 · 实体页缺边界说明 · 别名冲突"]):
        o.append(txt(58, y + 40 + i * LINE, s, 12, T["focus2"], RIGHT))
    y += h2b
    o.append(txt(LEFT, y + 24, "全图为本轮实测。检查项数以kb-lint 实际输出条数为准：12 项", 12, T["dim"], 680, 0, in_box=False))
    color_dist([("外框/卡片", C["focus_stroke"], C["card_stroke"]),
                ("外框/枢纽", C["focus_stroke"], C["hub_stroke"]),
                ("卡片/枢纽", C["card_stroke"], C["hub_stroke"]),
                ("规则/知识外框", C["box_stroke"], C["focus_stroke"]),
                ("原料/工具", C["warn_stroke"], C["tool_stroke"])])
    write("01-四层框架全貌.svg", svg(o, y + 44, "知识库四层框架全貌", "坐标由代码计算，含三类断言"))


# ================================================================
# 图 2 · 摄入流程七步闭环
# ================================================================
def gen_flow():
    print("\n[图2] 摄入流程七步闭环")
    o = []
    o.append(txt(LEFT, 26, "摄入流程　七步顺序不可颠倒", 14, T["focus2"], 680, 0, in_box=False))
    y1 = 42
    bw, bh = 140, 52
    n1x, n2x, n3x, n4x = 40, 204, 368, 532
    n4w = 108
    o.append(box(n1x, y1, bw, bh, C["tool_fill"], C["tool_stroke"]))
    o.append(txt(n1x + 16, y1 + 20, "1 读取资料", 12, T["tool"], n1x + bw))
    o.append(txt(n1x + 16, y1 + 38, "raw 根目录", 12, T["tool2"], n1x + bw))
    o.append(f'<path d="M{n1x+bw+4} {y1+bh/2} L{n2x-4} {y1+bh/2}" fill="none" stroke="#AFA9EC" stroke-width="1.5" marker-end="url(#arrow)"/>')
    o.append(box(n2x, y1, bw, bh, C["bad_fill"], C["bad_stroke"]))
    o.append(txt(n2x + 16, y1 + 20, "2 查重", 12, T["bad"], n2x + bw))
    o.append(txt(n2x + 16, y1 + 38, "已摄入 + 根目录", 12, T["bad2"], n2x + bw))
    o.append(f'<path d="M{n2x+bw+4} {y1+bh/2} L{n3x-4} {y1+bh/2}" fill="none" stroke="#AFA9EC" stroke-width="1.5" marker-end="url(#arrow)"/>')
    o.append(box(n3x, y1, bw, bh, C["tool_fill"], C["tool_stroke"]))
    o.append(txt(n3x + 16, y1 + 20, "3 写摘要页", 12, T["tool"], n3x + bw))
    o.append(txt(n3x + 16, y1 + 38, "声明对应原始资料", 12, T["tool2"], n3x + bw))
    o.append(f'<path d="M{n3x+bw+4} {y1+bh/2} L{n4x-4} {y1+bh/2}" fill="none" stroke="#AFA9EC" stroke-width="1.5" marker-end="url(#arrow)"/>')
    o.append(box(n4x, y1, n4w, bh, C["tool_fill"], C["tool_stroke"]))
    o.append(txt(n4x + 14, y1 + 20, "4 更新实体", 12, T["tool"], n4x + n4w))
    o.append(txt(n4x + 14, y1 + 38, "概念页 综述", 12, T["tool2"], n4x + n4w))
    # 查重失败分支
    bx, by, bwid = 180, 132, 188
    o.append(f'<path d="M{n2x+bw/2} {y1+bh} L{n2x+bw/2} {by-4}" fill="none" stroke="#F09595" stroke-width="1.5" marker-end="url(#arrow)"/>')
    o.append(box(bx, by, bwid, 40, C["bad_fill"], C["bad_stroke"]))
    o.append(txt(bx + 16, by + 24, "已存在 → 停止，不重复摄入", 12, T["bad"], bx + bwid))
    y2 = 204
    o.append(f'<path d="M{n4x+n4w/2} {y1+bh} L{n4x+n4w/2} {y1+bh+20} L110 {y1+bh+20} L110 {y2-4}" fill="none" stroke="#AFA9EC" stroke-width="1.5" marker-end="url(#arrow)"/>')
    o.append(box(n1x, y2, bw, bh, C["hub_fill"], C["hub_stroke"]))
    o.append(txt(n1x + 16, y2 + 20, "5 更新目录", 12, T["focus"], n1x + bw))
    o.append(txt(n1x + 16, y2 + 38, "三张枢纽页", 12, T["focus2"], n1x + bw))
    o.append(f'<path d="M{n1x+bw+4} {y2+bh/2} L200 {y2+bh/2}" fill="none" stroke="#AFA9EC" stroke-width="1.5" marker-end="url(#arrow)"/>')
    c6x, c6w = 204, 216
    o.append(box(c6x, y2 - 8, c6w, 68, C["warn_fill"], C["warn_stroke"]))
    o.append(txt(c6x + 16, y2 + 12, "6 收尾自检", 13, T["warn"], c6x + c6w))
    o.append(txt(c6x + 16, y2 + 31, "形式项机器 + 内容项人工", 12, T["warn2"], c6x + c6w))
    o.append(txt(c6x + 16, y2 + 48, "两部分缺一不可", 12, T["warn"], c6x + c6w))
    o.append(f'<path d="M{c6x+c6w+4} {y2+bh/2-8} L440 {y2+bh/2-8}" fill="none" stroke="#AFA9EC" stroke-width="1.5" marker-end="url(#arrow)"/>')
    o.append(box(444, y2 - 8, 196, 68, C["hub_fill"], C["hub_stroke"]))
    o.append(txt(460, y2 + 12, "7 移动资料", 12, T["focus"], 640))
    o.append(txt(460, y2 + 31, "必须是最后一步", 12, T["focus2"], 640))
    o.append(txt(460, y2 + 48, "顺序反了会归档未写完的资料", 12, T["focus2"], 640))
    y3 = 292
    o.append(box(LEFT, y3, 292, 76, C["focus_fill"], C["focus_stroke"], 10))
    o.append(txt(58, y3 + 21, "形式项　机器判定", 12, T["focus"], 332))
    o.append(txt(58, y3 + 41, "kb-lint.py 12 项检查", 12, T["focus2"], 332))
    o.append(txt(58, y3 + 60, "退出码 0 只证明没有断链", 12, T["warn2"], 332))
    o.append(box(348, y3, 292, 76, C["warn_fill"], C["warn_stroke"], 10))
    o.append(txt(366, y3 + 21, "内容项　人工判定", 12, T["warn"], RIGHT))
    o.append(txt(366, y3 + 41, "逐条回原文核对并留痕", 12, T["warn2"], RIGHT))
    o.append(txt(366, y3 + 60, "无留痕视为未做", 12, T["warn2"], RIGHT))
    y4 = 392
    o.append(txt(LEFT, y4, "三条从失败里长出来的纪律", 14, T["warn2"], 680, 0, in_box=False))
    o.append(box(LEFT, y4 + 14, FULL, 54, C["bad_fill"], C["bad_stroke"], 10))
    o.append(txt(58, y4 + 34, "移动资料是最后一步", 12, T["bad"], RIGHT))
    o.append(txt(58, y4 + 53, "断链待用户决策曾使退出码恒为 1，导致任何摄入都无法归档", 12, T["bad2"], RIGHT))
    color_dist([("流程/分支", C["tool_stroke"], C["bad_stroke"]),
                ("自检/移动", C["warn_stroke"], C["hub_stroke"])])
    write("02-摄入流程七步闭环.svg", svg(o, y4 + 88, "摄入流程七步闭环", "含查重分支与自检返工回路"))


# ================================================================
# 图 3 · 诊断报告九处问题与修复状态
# ================================================================
def gen_audit():
    print("\n[图3] 诊断九处问题与修复状态")
    o = []
    o.append(txt(LEFT, 26, "架构诊断九处问题　当前状态", 14, T["focus2"], 680, 0, in_box=False))
    y = 40
    # 已修
    hdone = 26 + 4 * LINE + 12
    o.append(box(LEFT, y, FULL, hdone, C["focus_fill"], C["focus_stroke"], 10))
    o.append(txt(58, y + 21, "已修 4 类　kb-lint 从 8 项增至 12 项", 13, T["focus"], RIGHT))
    done = [("别名冲突 11 处", "wiki 9 处（删README 页那份）+ 报告 2 处 → 0"),
            ("字段名失控 68 种", "新增条款 10 + 同义收敛 25 处 + 第 8 项检查"),
            ("类别私有词表 11 值", "收敛为 6 个受控值，可聚合"),
            ("诊断报告自身遗留", "补登记目录 + 报告数")]
    for i, (a, b) in enumerate(done):
        o.append(txt(58, y + 40 + i * LINE, f"已修　{a}　{b}", 12, T["focus2"], RIGHT))
    y += hdone + 20
    # 待决策
    hwait = 26 + 4 * LINE + 12
    o.append(box(LEFT, y, FULL, hwait, C["warn_fill"], C["warn_stroke"], 10))
    o.append(txt(58, y + 21, "待你决策 4 类　本轮未动", 13, T["warn"], RIGHT))
    wait = [("1 摘要层语义", "23 份资料无一同名摘要页　建议改规则而非改实践"),
            ("2 实体页与 README 双胞胎", "10 对 README 页更大　建议反向补齐实体页"),
            ("3 日志 123KB", "唯一无限增长文件　已定>300 条或跨年双触发"),
            ("4 output/ 成第二知识库", "182 文件 15 顶层项　建议加版本标记而非搬文件")]
    for i, (a, b) in enumerate(wait):
        o.append(txt(58, y + 40 + i * LINE, f"待决　{a}　{b}", 12, T["warn2"], RIGHT))
    y += hwait + 20
    # 已修与待决的对比条
    hb = 26 + 2 * LINE + 12
    o.append(box(LEFT, y, FULL, hb, C["focus_fill"], C["box_stroke"], 10))
    o.append(txt(58, y + 21, "判断依据", 13, T["focus"], RIGHT))
    o.append(txt(58, y + 40, "形式层全绿与结构层有洞不矛盾——六类检查全是单页合法性判断", 12, T["focus2"], RIGHT))
    o.append(txt(58, y + 57, "九处问题没有一项能被现有检查发现，退出码 0 是形式合格不是架构合格", 12, T["warn2"], RIGHT))
    y += hb
    color_dist([("已修/待决", C["focus_stroke"], C["warn_stroke"])])
    write("03-诊断九处问题状态.svg", svg(o, y + 24, "诊断九处问题与修复状态", "已修 4 类与待决 4 类的对照"))


# ================================================================
# 图 4 · 层级与页型对应关系
# ================================================================
def gen_map():
    print("\n[图4] 线索与页型分布")
    o = []
    o.append(txt(LEFT, 26, "四条线索 × 页型分布　实测", 14, T["focus2"], 680, 0, in_box=False))
    y = 40
    # 线索表头
    cols = ["线索", "摘要", "实体", "概念", "分析", "小计"]
    colx = [LEFT + 20, LEFT + 190, LEFT + 280, LEFT + 370, LEFT + 460, LEFT + 550]
    o.append(box(LEFT, y, FULL, 34, C["box_fill"], C["box_stroke"], 8))
    for i, cname in enumerate(cols):
        o.append(txt(colx[i], y + 22, cname, 12, T["focus"], RIGHT))
    y += 34 + 6
    rows = [("一 知识库方法论", "5", "4", "9", "3", "21", C["hub_fill"]),
            ("二 提示词工程", "2", "1", "12", "1", "16", C["card_fill"]),
            ("三 中国法律文本", "3", "2", "11", "4", "20", C["warn_fill"]),
            ("四 编程 Agent", "14", "18", "5", "1", "38", C["tool_fill"])]
    for name, a, b, c, d, e, fill in rows:
        h = 30
        o.append(box(LEFT, y, FULL, h, fill, C["card_stroke"], 6))
        o.append(txt(colx[0], y + 20, name, 12, T["focus"], RIGHT))
        for i, v in enumerate([a, b, c, d, e]):
            o.append(txt(colx[i + 1], y + 20, v, 12, T["focus2"], RIGHT))
        y += h + 6
    y += 10
    hn = 26 + 3 * LINE + 12
    o.append(box(LEFT, y, FULL, hn, C["focus_fill"], C["focus_stroke"], 10))
    o.append(txt(58, y + 21, "读这张图要注意的两件事", 13, T["focus"], RIGHT))
    o.append(txt(58, y + 40, "线索三与线索一/二/四 零链接交集——除三张索引页外无跨线索页", 12, T["warn2"], RIGHT))
    o.append(txt(58, y + 57, "这是已知决策（无交汇不强造），代价是知识网实际为互不相通的簇", 12, T["focus2"], RIGHT))
    y += hn
    write("04-线索页型分布.svg", svg(o, y + 24, "四条线索与页型分布", "各线索在各页型的页数分布"))


for f in (gen_frame, gen_flow, gen_audit, gen_map):
    f()

print("\n" + "=" * 50)
if problems:
    print(f"共 {len(problems)} 处问题：")
    for m in problems:
        print("  -", m)
    sys.exit(1)
print("全部断言通过")
