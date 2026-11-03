# diagram-layout-discipline

[简体中文](README.md) | **English**

**Three hard rules for SVG diagrams: text must not overflow its box, nested containers must stay visually distinguishable, and anything with order, branching, hierarchy or quantity must be drawn rather than described. Ships a text-width measurement script.**

![Python](https://img.shields.io/badge/python-3.9%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-yellow)
![spec](https://img.shields.io/badge/agentskills.io-spec%20valid-2E7D32)

## Install

```bash
npx skills add zhanguoliang715/diagram-layout-discipline
```

Or as a Claude Code plugin:

```bash
claude plugin marketplace add zhanguoliang715/diagram-layout-discipline
claude plugin install diagram-layout-discipline@diagram-layout-discipline
```

## Why rules instead of suggestions

Every rule here came from a rejected diagram, not from taste:

| What you have seen | Root cause | Rule |
|---|---|---|
| a child box hanging out of its parent | parent height typed in by hand and miscalculated | **compute coordinates in code**; derive parent height from children |
| text pressed against the border | CJK width estimated by eye, always underestimated | **measure text width** (`scripts/measure_text.py`) |
| two nested boxes look like one | inner and outer stroke use adjacent shades of the same hue | **stroke RGB distance > 150** |
| a seven-step flow written as a paragraph | something drawable was described | **order / branching / hierarchy / quantity must be drawn** |

The criterion is simple: **once text overflows, the reader cannot tell which box it belongs to, and the diagram stops carrying meaning.** This is not an aesthetics issue.

## Width model

```
CJK / full-width punctuation ≈ 1.00 em
Latin letters / digits / half-width punctuation ≈ 0.55 em
space ≈ 0.28 em
```

Deliberately an **overestimate**: a false "may overflow" costs one re-measure; a missed overflow costs a rejected diagram.

## Boundaries

- **Structural diagrams only** — not illustration, not photography, not UI visual design.
- **Guarantees no overlap and no ambiguity, not beauty.**
- **Re-measure when the font changes** — the model is per-em estimation, not real font metrics.

## Docs

- [Beginner handbook](docs/新手手册.md)
- [Technical doc](docs/技术文档.md)
- `scripts/gen_skeleton.py` — reusable skeleton with built-in assertions

## License

MIT.
