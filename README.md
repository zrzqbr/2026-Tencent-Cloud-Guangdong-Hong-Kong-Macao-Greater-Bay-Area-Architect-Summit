# 2026 腾讯云粤港澳大湾区架构师峰会 PPT 模板 Skill

这是峰会专用的 **PPT 模板、品牌限定、旧稿迁移与验收 Skill**。

它不是独立 PPT 生成器。请与自己常用的 PPT 生成/编辑 Skill、内容研究工具、图表工具、图片工具或 PDF 工具一起使用：其他工具负责选题、大纲、叙事、页面结构和 PPT 制作；本 Skill 负责把结果适配到 2026 峰会模板，并检查品牌、字体、颜色、Logo、迁移完整性和文字重叠。

第 4 页以后不限定结构，不要求套用模板样例里的卡片、圆形编号、三栏、图表或图片布局。

## 新版模板映射

官方源模板有 13 页，但最终演讲稿不能直接原样输出：

| 源模板页 | 作用 | 最终稿规则 |
| --- | --- | --- |
| 第 1 页 | 主 KV | 最终第 1 页，完全不变 |
| 第 2 页 | 56 个 SVG 图标素材 | 只作素材库，不进入最终稿 |
| 第 3 页 | 演讲标题页 | 最终第 2 页 |
| 第 4 页 | 讲师介绍页 | 最终第 3 页；有真实资料就填，没有就留空背景 |
| 第 5-12 页 | 版式样例 | 仅供参考，不限定结构 |
| 第 13 页 | Thank-you 页 | 最后一页，完全不变 |

演讲者自己的总结、Q&A 或联系方式放倒数第二页，最终感谢页始终是最后一页。

最终稿第 1-3 页是不可占用的固定开场序列：首页主 KV、标题页、嘉宾自我介绍/头像页。大纲的第一项内容、目录或迁移后的第一张正文，都必须从最终第 4 页开始。标题页和嘉宾页只能替换模板规定字段，不能改结构、移动对象或换成其他版式。

## 典型用法

生成新 PPT：

> 使用我常用的 PPT 生成 Skill 完成内容和页面制作，同时使用 `$create-gba-architect-summit-slides` 作为 2026 腾讯云粤港澳大湾区架构师峰会的模板、品牌和验收层。

迁移旧 PPT/PDF：

> 使用 `$create-gba-architect-summit-slides` 把这个旧 PPT/PDF 迁移到峰会模板。保留所有内容、数据、备注、链接和可编辑元素，替换旧背景、字体、颜色和品牌皮肤，不要把整页截图当成迁移结果。

只检查合规：

> 使用 `$create-gba-architect-summit-slides` 审查这套 PPT 是否符合峰会固定页、腾讯体、文字颜色、背景、Logo 安全区和防重叠要求，不修改内容。

## 一键预检与迁移计划

支持 `.ppt`、`.pptx`、`.pdf`、`.html`、`.md` 源文件：

```bash
python3 scripts/summit_adapter.py \
  --source /absolute/path/source.pptx \
  --output-dir /absolute/path/migration-work
```

输出：

- `adapter-report.json`：页数、页面分类、对象清单、字体/颜色替换候选、背景/遮罩、越界、Logo 区、文字框交叉和图表兼容性。
- `migration-map.json`：源页到目标页的映射。
- `element-migration-ledger.json`：PPTX 元素级迁移台账初稿。
- `companion-instructions.md`：交给常用 PPT Skill 执行的明确规则。

这个命令只做 dry-run，不会修改源文件，也不会代替 PPT 生成 Skill 自动创作内容。

## PPT/PDF 迁移原则

- PPTX：逐个保留文本框、形状、连接线、图片、表格、图表、超链接和备注，不把整页渲染图塞回目标稿。
- 如果源 PPT 已经包含规范的首页、标题页、嘉宾头像页和最终感谢页，迁移时原位保留；正文只从头像页之后开始。
- 旧 `.ppt`：保留原件，先转换副本为 `.pptx`，对照渲染后再迁移。
- PDF：尽量重建可编辑文字、表格和图形；只有无法恢复的单个对象才保留高清图，并记录不可编辑限制。
- HTML/Markdown：保留标题层级、正文、图片、代码、链接和来源顺序，由配套 PPT Skill 决定分页与版式。
- 不虚构讲师资料、头像、Logo、数据、结论或引用。

详细流程见 [migration-workflow.md](references/migration-workflow.md) 和 [element-migration-quality.md](references/element-migration-quality.md)。

## 品牌硬规则

- 标题、章节标题、重点姓名和大数字：`腾讯体 W7`，通常为 `#FD9D50`。
- 正文、说明、讲师职务、图表标签：`腾讯体 W3`，通常为 `#FFFFFF`。
- Latin、East Asian、Complex Script 三个字体字段都要写入同一个准确腾讯体名称。
- 每页使用批准背景；背景里已有官方标识，不重复添加、不重绘、不改色、不遮挡。
- 所有内容避开 `brand-manifest.json` 定义的 Logo 禁入区。
- 字体替换后必须重新渲染，修复重叠、裁切、异常换行和过小字号。
- 色块和图表颜色只使用品牌清单允许的范围，不做激进全局换色。

机器可读的唯一品牌清单是 [brand-manifest.json](assets/brand-manifest.json)，详细人工规则见 [template-contract.md](references/template-contract.md)。

## 调色板工具

```bash
python3 scripts/brand_palette.py --prompt
python3 scripts/brand_palette.py --validate '#FD9D50' --json
python3 scripts/brand_palette.py --nearest '#F6A05A' --json
python3 scripts/brand_palette.py --chart
```

近似色使用 CIEDE2000 计算，只提供替换建议，不代表允许无差别全局换色。

## 保守修复

先 dry-run：

```bash
python3 scripts/safe_repair_deck.py \
  --input /absolute/path/input.pptx \
  --report /absolute/path/repair-report.json
```

写入新副本：

```bash
python3 scripts/safe_repair_deck.py \
  --input /absolute/path/input.pptx \
  --output /absolute/path/repaired-copy.pptx \
  --report /absolute/path/repair-report.json
```

脚本只负责字体名、直接文字颜色、图表字体/系列颜色和可选图表轴 ID 兼容修复。固定页插入、母版/背景迁移、内容重排和元素级迁移仍由配套 PPT Skill 完成。源文件永远不会被覆盖。

## 最终验收

所有 PPT：

```bash
python3 scripts/validate_deck_brand.py /absolute/path/deck.pptx
```

迁移 PPTX 还要运行：

```bash
python3 scripts/validate_element_migration.py \
  --source /absolute/path/source.pptx \
  --destination /absolute/path/deck.pptx \
  --ledger /absolute/path/element-migration-ledger.json \
  --migration-map /absolute/path/migration-map.json
```

自动检查通过不等于视觉合格。还必须使用配套 PPT Skill 做溢出检查，逐页渲染并人工检查文字重叠、裁切、Logo 遮挡、图表标签和最终感谢页。

## 更新模板资产

```bash
python3 scripts/extract_template_assets.py \
  --template /absolute/path/new-template.pptx \
  --rendered-thanks /absolute/path/rendered-slide-13.png \
  --output-dir /absolute/path/stage
```

脚本会分阶段提取六套背景、固定页、56 个 SVG 图标、文字几何和兼容性报告。确认哈希与清单一致后才使用 `--apply`，不会直接修改新模板原件。

## 目录

- `SKILL.md`：Codex 实际执行规则。
- `assets/brand-manifest.json`：品牌与模板机器清单。
- `assets/0815-architect-summit-template.pptx`：新版官方模板。
- `assets/fixed-pages/`：最终稿固定页资产。
- `assets/backgrounds/`：批准背景。
- `assets/icons/`：源模板第 2 页提取的可选 SVG 素材。
- `assets/color-blocks/`：批准色块。
- `references/`：模板、迁移、字体、排版和自动化规范。
- `scripts/`：预检、提取、修复、渲染和双重验收工具。
