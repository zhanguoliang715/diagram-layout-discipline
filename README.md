# diagram-layout-discipline

**画 SVG 图表的三条硬纪律：文字不许溢出边框、嵌套容器必须一眼能分清、能画的逻辑不许用文字描述。附一个量字宽的脚本，不用眼睛估。**

![Python](https://img.shields.io/badge/python-3.9%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-yellow)
![spec](https://img.shields.io/badge/agentskills.io-spec%20valid-2E7D32)

## 为什么需要"纪律"而不是"建议"

这三条都来自被退回的实例，不是凭感觉定的：

| 你见过的现象 | 根因 | 规则 |
|---|---|---|
| 子框的下半截跑到父框外面 | 容器高度手填，算错了 | **坐标由代码计算**，容器高度由子框反推 |
| 文字压到边框上 | 汉字宽度靠眼睛估，估必然偏小 | **文字宽度必须实测** |
| 两层框看不出从属 | 内外层用了同一色相相邻档 | **描边 RGB 距离须 > 150** |
| 七步流程写成一段话 | 能画的用了文字 | **有先后/分支/层级/数量，必须画图** |

判据很简单：**文字溢出后，读者无法判断它属于哪个框，图的语义直接失效。** 这不是美观问题。

## 里面有什么

| 文件 | 用途 |
|---|---|
| `SKILL.md` | 四条纪律的完整说明与反例 |
| `scripts/measure_text.py` | 量一段中英混排文本在给定字号下的宽度；刻意高估，宁可报"可能溢出"也不漏报 |
| `scripts/gen_skeleton.py` | 可复用骨架：`text()` 自动断言不溢出、`parent_child_ok()` 断言包含关系、`dist()` 断言描边色距 |
| `scripts/gen_all.py` | 四张示例图 + 三类断言的全流程演示 |

## 用插件安装（一条命令，已实测）

```bash
claude plugin marketplace add zhanguoliang715/diagram-layout-discipline
claude plugin install diagram-layout-discipline@diagram-layout-discipline
```

> 本机 git 若报 `CRYPT_E_NO_REVOCATION_CHECK`（证书吊销列表查不到），命令前加 `GIT_SSL_NO_VERIFY=1`。
> 这是本机 TLS 配置问题，与仓库无关；换台机器通常直接可用。

不想装插件也行，下面的手动方式是等价的。

## 上手

```bash
git clone https://github.com/zhanguoliang715/diagram-layout-discipline.git
cp -r diagram-layout-discipline ~/.workbuddy/skills/
cd diagram-layout-discipline/scripts
python gen_skeleton.py     # 退出码 0 且打印「全部通过」才算数
python measure_text.py "知识库摄入流程" 14 300 20
```

**不要从零手写坐标**：改 `gen_skeleton.py` 里的数据，让代码算。

## 宽度模型（为什么能替代字体度量）

```
汉字 / 全角标点 ≈ 1.00 em
拉丁字母 / 数字 / 半角标点 ≈ 0.55 em
空格 ≈ 0.28 em
```

刻意**高估**：宁可误报"可能溢出"，也不漏报。漏报的代价是图被打回，误报的代价只是再量一次。

## 边界

- **只管结构图**，不管插画、摄影、UI 视觉。
- **断言保证不压边、不混淆，不保证好看**。审美是另一回事。
- **换字体后要重量**。宽度模型是按字号估算的，不等同于具体字体的实际度量。

## 最常见的三个错

1. **眼睛估宽度**。估窄 20% 是常态。
2. **用 `getbbox()[2]` 当文字宽度**。它含左侧 bearing，会偏大；应用 `font.getlength()`。
3. **断言从来没失败过**。这说明判据可能压根没生效——必须造一个坏样本，确认它会报错。

## 文档

| 想看什么 | 去哪 |
|---|---|
| 第一次用，怎么一步步做 | [docs/新手手册.md](docs/新手手册.md) |
| 断言实现、失败模式、已知限制 | [docs/技术文档.md](docs/技术文档.md) |
| 完整纪律与反例 | [SKILL.md](SKILL.md) |

## License

[MIT](LICENSE)
