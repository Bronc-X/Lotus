# Lotus

Lotus 为 **Codex、Claude Code 和 DSH next** 提供全局工作规则、任务型 skills 和 `/` 菜单配置。

## 让 AI 安装或更新

把下面这段交给正在使用的编码助手：

```text
请从 https://github.com/Bronc-X/Lotus.git 安装或更新 Lotus 到长期保存目录。识别当前宿主是 Codex、Claude Code 还是 DSH next，运行 scripts/install-profile.py --host 对应宿主，按 profiles/local-latest.json 安装 skills 并设置 / 菜单入口。检查全局规则、技能文件和菜单实际可用；需要外部运行组件时按对应 Skill 的说明配置，修复检查失败后重试。
```

## 按宿主安装

需要 Git 和 Python 3.11 或以上版本。先下载仓库：

```bash
git clone https://github.com/Bronc-X/Lotus.git
cd Lotus
```

只运行当前宿主对应的命令：

| 宿主 | 安装命令 | 全局规则 | Skills |
|---|---|---|---|
| Codex CLI / Codex App | `python scripts/install-profile.py --host codex` | `~/.codex/AGENTS.md` | `~/.codex/skills/` |
| Claude Code | `python scripts/install-profile.py --host claude-code` | `~/.claude/CLAUDE.md` | `~/.claude/skills/` |
| DSH next | `python scripts/install-profile.py --host dsh-next` | `~/.dsh/AGENTS.md` | `~/.dsh/skills/` |

macOS / Linux 若使用 `python3`，替换命令中的 `python`。设置了 `CODEX_HOME`、`CLAUDE_CONFIG_DIR` 或 `DSH_HOME` 时，安装到对应目录。

预览将要修改的文件数量：

```bash
python scripts/install-profile.py --host codex --dry-run
```

安装器只更新包内文件，保留本地额外文件；覆盖前将原文件保存到宿主目录的 `backups/lotus-profile-时间/`。安装后打开新会话，在输入框输入 `/` 检查技能入口。

### Codex

安装器会把 [配置清单](profiles/local-latest.json) 中的 skill 启停和插件开关合并到 `config.toml`，保留模型、API、MCP、权限等其他设置。内置插件由 Codex 提供；写入开关不会复制插件运行时或安装第三方插件。

Codex 的 `agents/openai.yaml`、内置图片工具、Goal 和桌面工具依赖宿主支持。

### Claude Code

安装器将菜单状态写入 Skill frontmatter。内部路由保留在磁盘上，使用 `user-invocable: false` 隐藏独立 `/` 入口。Codex 的插件开关和 `agents/openai.yaml` 不作为 Claude Code 插件配置使用。

### DSH next

安装器写入 DSH next 的全局规则与 skills 目录。DSH next 的文件系统 skill 提供器支持 `<name>/SKILL.md`，通过 frontmatter 控制用户与模型调用。

DSH next 的插件通过自身的配置与插件管理器安装。仓库中的 Codex 插件开关不能直接导入 DSH next；依赖 Codex 专有工具的 Skill，需要按说明使用宿主可用能力或补齐外部组件。此处的安装检查覆盖文件与菜单配置，不代表所有外部服务均已连通。

## 当前 `/` 菜单

[profiles/local-latest.json](profiles/local-latest.json) 保存本机 2026-11-07 的入口选择和插件开关。这里的“入口”指在对话框输入 `/` 可以唤起的技能。

| 任务 | 入口 |
|---|---|
| 检索与代码库 | `anysearch`、`agent-reach`、`codebase-memory-mcp`、`codex-history-bridge` |
| 开发与检查 | `gstack`、`mini-investigate`、`security-auditor`、`workflow`、`subagent`、`goal` |
| 界面与图解 | `frontend-design`、`taste-skill`、`diagram-design`、`shadcn-preset-refactor`、`collectui-cli`、`gsap`、`ai-progress-workspace` |
| 写作与解释 | `copywriting`、`humanwriter`、`broncin-style-writer`、`lieflat-less-ai-tone`、`feynman`、`executive-sow-pricing` |
| 录音与声音 | `recording`、`ai-podcast`、`toni-voice`、`brian-voice` |
| 图片与视频 | `image-consistency`、`agent-video-pipeline`、`one-prompt-video`、`onetake`、`openchatcut`、`orca-motion`、`orca-transition-skill`、`video-shotcraft`、`seedance-20`、`semantic-video-redaction`、`hypit-kling-face-reproduction`、`hypit-kling-five-view-replica`、`douyin-comments` |

`gstack` 是套件的统一入口，按任务读取规划、排查、浏览器、测试、审查或交付的内部适配器。子入口保留为内部文件。官方运行组件来自 [garrytan/gstack](https://github.com/garrytan/gstack)，不随本仓库复制。

`image-2` 保留在包内，按当前配置停用。`copy-editing` 保留为写作技能的内部参考。宿主自带的系统技能和插件技能由宿主管理。

个人声线、私人文风语料、账号和机器运行配置需要在本地配置；已有文件在更新时保留。播客配置见 [docs/podcast-skills.md](docs/podcast-skills.md)。

第三方 Skill 保留各自许可；[onetake](skills/onetake/LICENSE) 使用 PolyForm Noncommercial。视频模板的第三方音频按 [音频来源清单](skills/video-shotcraft/assets/audio/ATTRIBUTION.md) 获取。

## 插件

本机启用的 Codex 插件开关记录在 [profiles/local-latest.json](profiles/local-latest.json)：

- `visualize`、`codex-app-tools`、`browser`、`unified-computer-use`、`chrome`、`computer-use`：`openai-bundled`
- `documents`、`pdf`、`spreadsheets`、`presentations`、`template-creator`：`openai-primary-runtime`

Lotus 自带的可选 Codex 插件市场位于 [.agents/plugins/marketplace.json](.agents/plugins/marketplace.json)，目前仅包含 `build-ios-apps`。需要 iOS 工作流时，在 Codex 中安装：

```bash
codex plugin marketplace add /path/to/Lotus
codex plugin add build-ios-apps@lotus
```

Claude Code 和 DSH next 使用各自的插件系统；Lotus 跨宿主共享的是工作规则与 Skill 文件。

## 更新

在 Lotus 目录执行：

```bash
git pull
python scripts/install-profile.py --host codex
```

使用 Claude Code 或 DSH next 时，将 `codex` 替换为 `claude-code` 或 `dsh-next`。

仅刷新本机已安装的 Codex Skill 文件：

```powershell
./scripts/sync-codex-skills.ps1
```

该命令保留本机菜单开关，不安装尚未存在的 Skill。

## 官方 gstack 与项目模板

原有安装器仍可安装官方 gstack 运行时及其 profile，并同时安装 Claude Code 与 Codex 的全局规则：

```powershell
./install.ps1 -Global
```

```bash
bash ./install.sh --global
```

可选 gstack profile：`core`、`design`、`review`、`deploy`、`full`。它们决定官方运行组件的安装与暴露范围；使用当前单入口菜单时，在运行后再执行对应宿主的 `install-profile.py`。

Windows 上官方 gstack 完整运行时需要 Git for Windows 的 Bash、Bun 和 Node。缺少依赖或下载失败时，旧安装器会保留已有运行时或生成 bootstrap 入口，补齐后重新安装。

项目模板支持 `nextjs`、`vite`、`html`。在目标项目目录运行：

```powershell
/path/to/Lotus/install.ps1 -Project nextjs
```

```bash
bash /path/to/Lotus/install.sh --project nextjs
```

项目模板写入 `AGENTS.md`；Claude Code 项目可将其作为 `CLAUDE.md` 的引用。全局安装不自动修改项目文件。

## 验证

安装器与配置检查：

```bash
python scripts/test-profile-install.py
```

Windows 技能同步检查：

```powershell
./scripts/test-skill-sync.ps1
```

原有跨平台安装器检查：

```bash
bash scripts/test-installers.sh
```
