# 2026 腾讯云粤港澳大湾区架构师峰会 PPT 模板 Skill

这是一个用于 **2026 腾讯云粤港澳大湾区架构师峰会** 的 PowerPoint 模板与品牌适配 Skill。

## 先说清楚：它不是 PPT 生成器

这个 Skill 不负责独立完成选题、调研、大纲、叙事、版式设计和 PPT 文件生成。

它更像一层“模板适配 + 品牌规范 + 验收门禁”：

- 你的常用 PPT 生成 Skill、演示文稿工具或编辑工具负责内容和 PPT 制作。
- 本 Skill 负责将输出适配为峰会模板，并检查品牌规范是否合格。
- 第 4 页以后保留内容结构自由，不强制使用样例中的卡片、圆形编号、三栏或图表结构。

## 可以配合哪些 Skill

可以和以下能力一起使用：

- PPT / PowerPoint 生成或编辑 Skill
- 内容研究、行业分析和大纲 Skill
- 图表、数据可视化 Skill
- 图片生成或图片处理 Skill
- PDF 读取、OCR 和文档转换工具

典型调用方式：

> 使用我常用的 PPT 生成 Skill 做一套技术分享，同时使用 `$create-gba-architect-summit-slides` 作为 2026 峰会模板和品牌验收层。

## 旧 PPT / PDF 迁移

如果原来已有一个不是峰会模板制作的 `.ppt`、`.pptx` 或 `.pdf`，可以使用本 Skill 进行迁移：

1. 逐页读取原始 PPT 或 PDF，提取标题、正文、数据、图表、图片、备注、来源和链接。
2. 将原始封面中的主题名称、副标题和讲师信息映射到峰会固定第 2 页。
3. 使用峰会固定第 1 页主 KV。
4. 使用峰会固定第 3 页原始模板背景，不额外添加内容。
5. 从第 4 页开始迁移原 PPT/PDF 的正文内容，保留原有信息结构，但不复制旧模板的视觉皮肤。
6. 替换旧背景、旧母版装饰、旧页码、旧模板 Logo 和旧主题色。
7. 适配峰会背景、Logo 禁入区、腾讯体 W7/W3、标题橙金色、正文白色和批准的色块系统。
8. 对每个源页面和目标页面进行对照检查，避免文字、数字、图表或来源丢失。

PDF 是扁平化文件。能恢复为可编辑文字、表格、图形的内容会尽量重建；无法恢复编辑性的图表或复杂图像，会保留清晰的高分辨率图像，并记录其不可编辑限制。不会用整页 PDF 截图代替完整迁移。

详细规则见 [`references/migration-workflow.md`](references/migration-workflow.md)。

## 固定前三页

| 页面 | 规则 |
| --- | --- |
| 第 1 页 | 原始主 KV 完全不变，只保留整页背景 |
| 第 2 页 | 放置主题名称、副标题、讲师字段，使用固定位置、字号、字体和颜色 |
| 第 3 页 | 使用原模板背景，不添加标题、照片、Logo、线条或占位内容 |

第 2 页的核心文字规范：

- 主标题：腾讯体 W7，88 pt，`#FD9D50`
- 副标题：腾讯体 W7，54 pt，`#FD9D50`
- 讲师字段：腾讯体 W3，28 pt，`#FFFFFF`

## 品牌规范

- 标题和展示文字使用腾讯体 W7。
- 正文、说明、图表标签和注释使用腾讯体 W3。
- 普通标题使用橙金色 `#FD9D50`。
- 中文和英文说明正文使用白色 `#FFFFFF`。
- 使用深海蓝背景、橙金色强调和规定的蓝色、绿色语义色块。
- Logo 使用背景中已经嵌入的官方图形，不重新绘制、复制、改色或遮挡。
- 每页使用批准的峰会背景，并为 Logo 和右下角峰会标识保留禁入区。

完整规范见：

- [`references/template-contract.md`](references/template-contract.md)
- [`references/brand-guidelines.md`](references/brand-guidelines.md)
- [`references/text-color-system.md`](references/text-color-system.md)
- [`references/color-block-system.md`](references/color-block-system.md)

## 三种使用方式

### 1. 生成新 PPT

让常用 PPT Skill 负责内容和版式，本 Skill 负责模板适配和验收。

### 2. 迁移旧 PPT / PDF

让 PPT/PDF 读取和编辑工具负责内容提取，本 Skill 负责固定页映射、背景替换、字体颜色适配和品牌验收。

### 3. 只做合规检查

不改动内容，只检查已有 PPT 是否符合峰会模板：

```bash
python3 scripts/validate_deck_brand.py /absolute/path/to/deck.pptx
```

校验失败即视为不能交付，需修复后重新检查。

## 目录说明

- `SKILL.md`：Codex 实际使用的 Skill 指令
- `agents/openai.yaml`：Skill 在 Codex 中的显示信息
- `assets/fixed-pages/`：固定前三页背景资产
- `assets/backgrounds/`：批准的峰会背景
- `assets/color-blocks/`：批准的色块资产
- `references/`：模板契约、品牌规范、文字规范、色块规范和迁移流程
- `scripts/validate_deck_brand.py`：PPT 品牌验收脚本

