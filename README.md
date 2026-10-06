# 短剧海报技能（duanjuhaibao）

给 AI 智能体用的「短剧海报」技能：从剧本 + 角色设定图出发，用两步法（设定图 → 姿势图 → 合成海报）生成短剧海报主视觉的 AI 提示词。

适用于任何支持 Agent Skills 规范的工具：Claude Code、Hermes Agent、Cursor、OpenCode、Codex 等。

## 安装

### 方式一：npx skills（通用，一条命令）

```bash
npx skills add andreamzhang/duanjuhaibao
```

### 方式二：Hermes Agent

```bash
hermes skills install "andreamzhang/duanjuhaibao/skills/short-drama-poster" --category content-production --yes
```

### 方式三：手动复制

把 `skills/short-drama-poster/` 整个文件夹复制到对应工具的 skills 目录：

- Claude Code：`~/.claude/skills/`
- Hermes Agent：`~/AppData/Local/hermes/skills/`（Windows）或 `~/.hermes/skills/`

## 技能内容

- **两步法工作流**：白底设定图 → 单人「海报专用姿势图」 → 姿势图 + 场景图合成海报（脸部相似度更稳）
- **硬性约定 17 条**：片名逐字符锁定（含标点）、主角层级写死、背景弱化、标题安全区、群像防「毕业照」、审美语言具体化，新增「先判断剧再设计海报（开题判断 + 构成模型）」「参考海报只借一个维度」
- **四本手册**（`references/`）：
  - `design-aesthetics.md` — 设计与审美（构图 / 色彩 / 光影 / 字体 / 类型惯例 / 空泛词翻译表）
  - `poster-layout.md` — 版式（排版）系统（网格 / 对齐 / 层级 / 间距 / 留白 / 电影海报规格，含 3:4 与 9:16 分区）
  - `character-composition.md` — 群像人物排版模式库（破呆五招 + 八式模式 + AI 防呆句）
  - `poster-concept.md` — 海报概念（开题判断 / 10 构成模型 + 决策树 / 短剧题材路由表 / 标题承载面与标题原型）
- **模板**（`templates/prompt-templates.md`）：姿势图（A）+ 海报合成（B）+ 无字底图（C）+ 标题层（D，分层兜底）
- **脚本**（`scripts/`）：
  - `compress_images.py` — 批量压缩超限图片（应对 ≤10MiB 上传限制）
  - `composite_layers.py` — 底图 + 标题层分层合成（screen/multiply/normal、网格定位，输出 grid.json）
  - `check_prompt.py` — 提示词预检（片名逐字、违禁词、空泛词）
- **示例**（`assets/`）：版式骨架示例、人物排版方案示例（HTML，浏览器直接打开）

## 适合谁用

做短剧 / 竖屏剧、需要用 AI（即梦·Seedream、GPT-image、Midjourney 等）生成海报封面的创作者。提示词针对即梦 / Seedream 优化，同样适用于其他图像模型。

## 更新记录

- **v1.1.0**：新增 `references/poster-concept.md`（开题判断 / 构成模型 / 决策树 / 题材路由 / 标题承载面）与硬性约定 16–17 条；新增分层兜底工具链（模板 C/D + `composite_layers.py`）与提示词预检 `check_prompt.py`；版式手册补齐 9:16 分区；审美手册补齐英文片名字体逻辑。

本仓库由 andreamzhang 维护。

## License

MIT © andreamzhang
