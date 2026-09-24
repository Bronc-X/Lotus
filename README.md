# Lotus

## 让 AI 自己安装

如果你不想亲自碰命令行，把这段交给 AI 编码助手：

```text
请从 https://github.com/Bronc-X/Lotus.git 安装或更新 Lotus 到一个长期保存目录，然后运行适合当前系统的全局安装器。验证当前宿主的全局规则、Lotus skills 和默认 gstack 入口实际可用；只安装我需要的可选插件。安全的本地检查和修复可以直接执行。若检查失败，修复后重试；仍受阻时给出失败证据和下一步。
```

Lotus 为 Codex 和 Claude Code 提供一组精简的全局规则、任务型 skills 和可选插件。

它做三件事：

1. 把 Lotus 全局规则写入 Claude Code 与 Codex 的全局规则文件。
2. 安装 Lotus 自带 skills。
3. 从官方 [garrytan/gstack](https://github.com/garrytan/gstack) 安装并同步默认顶层 gstack skills。

Lotus 不内置 gstack 运行时快照；运行组件来自 `garrytan/gstack`。`adapters/gstack/` 为已安装的常用 Codex 入口提供精简调用规则，不替换上游二进制和脚本，也不自动启用隐藏技能。

仅同步本机已安装的 Lotus skills（不修改 API、模型、权限、插件缓存或菜单开关）：

```powershell
./scripts/sync-codex-skills.ps1
```

同步前会在 Codex 的 backups 目录保存被替换文件和恢复清单。仅更新已存在的技能，未安装的可选插件不会因此安装。独立运行上游 gstack 更新可能覆盖入口；之后重新同步即可恢复 Lotus 适配。

## 目标

- 只加载当前任务需要的规则和文档。
- 保留用户已有改动并限制修改范围。
- 允许 Agent 自主执行安全的本地实现和验证。
- 用实际运行结果定义完成，而不是停在第一版实现。

## Lotus 工作协议

Lotus 的全局规则真源在 [core/AGENTS.md](core/AGENTS.md)。全局安装会把它写入：

| 宿主 | 全局安装命令 | Lotus 写入位置 | 说明 |
|---|---|---|---|
| Claude Code | `install.ps1 -Global` / `install.sh --global` | `~/.claude/CLAUDE.md`、`~/.claude/skills` | 受托管 |
| Codex CLI / Codex App | `install.ps1 -Global` / `install.sh --global` | `~/.codex/AGENTS.md`、`~/.codex/skills` | 受托管 |

其他宿主不由 Lotus 安装器自动写入全局路径。如果该宿主支持手动全局规则，请直接导入 [core/AGENTS.md](core/AGENTS.md)。

### 核心规则

- 只读取任务相关的项目规则、Skill 和文档。
- 安全的本地读取、编辑、构建、测试和修复可直接执行。
- 保留已有改动，只修改当前目标所需范围。
- 重要删除、生产变更、外部发布、付费和新凭据使用仍需明确授权。
- 完成需要实现、运行相关检查、检查结果、修复失败并重新验证。

## 快速安装

选择一个长期保存 Lotus 的目录。以后更新 Lotus 时就在这里执行 `git pull`。

Windows PowerShell：

```powershell
git clone https://github.com/Bronc-X/Lotus.git C:\Dev\Lotus
C:\Dev\Lotus\install.ps1 -Global
```

macOS / Linux：

```bash
git clone https://github.com/Bronc-X/Lotus.git ~/Dev/Lotus
~/Dev/Lotus/install.sh --global
```

如果下载方式丢失了可执行权限：

```bash
bash ~/Dev/Lotus/install.sh --global
```

无人值守安装：

```powershell
C:\Dev\Lotus\install.ps1 -Global -Force
```

```bash
~/Dev/Lotus/install.sh --global --yes
```

全局安装会：

1. 写入 Claude Code 全局规则：`~/.claude/CLAUDE.md`
2. 写入 Codex 全局规则：`~/.codex/AGENTS.md`
3. 安装 Lotus 自带 skills。
4. 安装或更新官方 gstack 到 `~/.gstack/repos/gstack`。
5. 同步默认顶层 gstack skills 到 `~/.claude/skills` 和 `~/.codex/skills`。

如果已存在全局规则文件，安装器会先创建 `.bak` 备份，再覆盖。旧会话通常不会自动加载新规则，请重启宿主或打开新会话。

## 项目模板安装

全局安装不会在每个项目目录自动生成 `AGENTS.md`。Codex 会自动继承 `~/.codex/AGENTS.md`，Claude Code 会自动继承 `~/.claude/CLAUDE.md`。项目级模板是额外叠加层，只在你主动运行 `-Project` / `--project` 时写入当前项目。

Windows PowerShell：

```powershell
cd C:\Users\YourName\Projects\MyNewApp
C:\Dev\Lotus\install.ps1 -Project nextjs
```

macOS / Linux：

```bash
cd ~/Projects/MyNewApp
~/Dev/Lotus/install.sh --project nextjs
```

可用模板：

- `nextjs`
- `vite`
- `html`

## gstack profiles

默认 `core` profile 会暴露 5 个顶层 gstack skills：

- `gstack`
- `gstack-office-hours`
- `gstack-investigate`
- `browse`
- `gstack-ship`

`gstack-plan-ceo-review`、`gstack-plan-design-review` 和 `gstack-plan-eng-review` 保留在官方 gstack runtime 中供内部路由，但 Lotus 不再把它们放进顶层菜单；这一规则对 `full` profile 也生效。

可选 profile：

| Profile | 暴露内容 |
|---|---|
| `core` | 默认 5 个顶层 skills |
| `design` | `core` 加设计相关 skills |
| `review` | `core` 加 QA / review / health 相关 skills |
| `deploy` | `core` 加发布部署相关 skills |
| `full` | 暴露当前官方 gstack 全量顶层 skills，但仍隐藏 3 个 plan-review 入口 |

切换 profile：

```powershell
C:\Dev\Lotus\install.ps1 -Global -GstackProfile design
```

```bash
~/Dev/Lotus/install.sh --global --gstack-profile design
```

## Lotus 自带顶层 skills

这些是 Lotus 仓库托管和打包的跨平台顶层 skills。官方 gstack skills 由 `garrytan/gstack` 提供。全局安装或更新 Lotus 后，下面这些 skill 会写入受托管宿主的全局 skills 目录；重启宿主后即可用 `/skill-name` 调用。

| Skill | 用途 |
|---|---|
| `anysearch` | 当前网页事实、新闻和股票、CVE、DOI 等结构化标识符检索 |
| `agent-reach` | 用户给定 URL、GitHub、视频、RSS、播客和平台原生内容检索 |
| `codebase-memory-mcp` | 代码库记忆与图谱检索，支持索引、结构搜索、调用路径和架构追踪 |
| `ai-podcast` | AI 单人播客总入口：声线建立、稿件、分段合成、QA 与按授权分发 |
| `toni-voice` | 更新后的 Toni 配音流程；个人声线资产和机器配置需本地提供 |
| `brian-voice` | Brian 独立声线执行器；与 Toni 的 profile、资产和缓存分开 |
| `broncin-style-writer` | 按本地私人文风档案写作；公开包不含 Flomo 原文和私人证据 |
| `lieflat-less-ai-tone` | 按明确规则清理成稿表达，保留原意和结构 |
| `recording` | 将录音整理为可追溯内容母库，并生产播客、文章、视频、社交、知识库和商业资产 |
| `executive-sow-pricing` | 为 AI / FDE 项目制作老板可决策的 SOW、报价和 PPT / Word 交付物 |
| `codex-history-bridge` | 查找或恢复跨 ChatGPT 与第三方 provider 配置的本地 Codex 历史任务 |
| `workflow` | 把已跑通项目蒸馏成有证据、可版本化、可复用的工作流或 Skill |
| `test-driven-development` | 在用户或项目明确要求时执行红绿重构 |
| `frontend-design` | 功能型 Web 应用界面、响应式和交互状态实现 |
| `taste-skill` | 高质量营销网站、作品集和编辑型页面设计与实现 |
| `ios-codex-preview` | 为 iOS / SwiftUI 项目安装并验证 Codex 侧边浏览器实时预览 |
| `shadcn-preset-refactor` | 用 shadcn/create preset 做无损视觉改造 |
| `image-2` | GPT Image 2 生图与改图入口 |
| `gsap` | GreenSock 官方 GSAP 动画 skill 聚合入口，路由到 React、ScrollTrigger、Timeline、Plugins 等官方子 skill |
| `ai-progress-workspace` | 搭建带真实 AI 工具进度和结构化 artifact 的 Agent 产品 |
| `mini-investigate` | 小型 Bug 的最小根因定位、修复与验证 |
| `security-auditor` | 安全审查，覆盖鉴权、注入、依赖风险等 |
| `feynman` | 用费曼学习法解释复杂机制 |
| `polanyi-tacit` | 分析代码背后的隐性业务和组织约束 |
| `agent-training-loop` | 持续执行复现、检测、执行、检查直到收敛 |
| `baseline-packager` | 将已通过行为封装为 baseline / golden master 回归保护 |
| `insights` | 使用习惯回顾与优化建议 |
| `subagent` | 子 Agent 管理与并行任务编排 |
| `goal` | 长期任务目标管理，优先路由到宿主原生 Goal 能力 |

## AI podcast 与声音配置

使用 `$ai-podcast` 制作 AI 单人口播播客。已有稿件或已确认声线可以直接接续；首次使用从获准的人工原声建立本地 profile。以原声访谈剪辑为主时使用 `$recording`。两条路线按任务选择，无需每次串行运行所有技能。

`toni-voice`、`brian-voice` 是各自的声线适配器；`broncin-style-writer` 负责文风，`lieflat-less-ai-tone` 按需清理成稿。仓库不含个人原声、声音提示、私人文风语料、账号或机器配置；安装和同步保留这些本地文件。其他使用者通过通用入口配置自己有权使用的声音。

Windows CUDA 与 CPU 已有短样技术验证；Apple Silicon 的 MPS 路由仍需目标机实测。安装 Skill 不会自动下载模型、授予声音使用权或发布节目。分工、使用路径与检查命令见 [播客技能说明](docs/podcast-skills.md)。

## 安装后验证

全局安装后，请打开一个新的宿主会话，把下面提示词复制给 AI 助手：

```text
请验证 Lotus 已在当前宿主生效：检查对应的全局规则文件、Lotus skills 和默认 gstack 入口，确认规则包含按需加载、安全本地自主执行和完整完成标准。若缺失，修复安装并重试；仍失败时给出缺失路径、错误证据和下一步。说明当前会话是否需要重开才能加载新配置。
```

这段提示词只负责验证，不能让旧会话临时变成真正的全局会话。真正生效需要满足两个条件：

1. 安装器已经写入宿主全局规则文件和全局 skills。
2. 宿主开启了一个会读取这些文件的新会话。

## `/skill` 不显示时怎么排查

`AGENTS.md` 和 `CLAUDE.md` 只保存规则和路由说明，不保存 slash skill 本体。slash skills 还必须存在于宿主自己的全局 skills 目录：

- Codex: `~/.codex/skills`
- Claude Code: `~/.claude/skills`

如果 `/review`、`/qa` 或其他 gstack skills 没出现：

1. 重新运行 `install.ps1 -Global` 或 `install.sh --global`。
2. 确认 `~/.gstack/repos/gstack` 存在。
3. 确认宿主全局 skills 目录中存在对应目录。
4. 完全重启 IDE / App，让宿主重新扫描全局 skills。

如果 Windows 没有 Git Bash，安装器会写入 bootstrap skills。bootstrap skills 是真实菜单入口，但只负责提示如何补齐完整官方 gstack runtime。

## Windows 依赖说明

官方 gstack 完整运行时依赖：

- `git`
- `bash`
- `bun`
- Windows 下还需要 `node`

Windows 上的 `bash` 通常来自 [Git for Windows](https://git-scm.com/download/win)。

如果机器没有 Git Bash，或官方 gstack runtime 安装失败，`install.ps1 -Global` 仍会安装默认 5 个顶层 gstack bootstrap skills，保证核心 `/gstack-*` 菜单入口不缺失。安装 Git for Windows 并补齐依赖后，重新运行：

```powershell
C:\Dev\Lotus\install.ps1 -Global
```

## macOS / Codex App / Claude Code 说明

Codex App、Claude Code 和 IDE 启动的命令行有时不会加载你的 `.zprofile` / `.bashrc`，导致 `bun` 已安装但安装器找不到。Lotus 安装器会自动补充常见工具路径：

- `~/.bun/bin`
- `~/.local/bin`
- `/opt/homebrew/bin`
- `/usr/local/bin`

官方 gstack 在 macOS 上会尝试用 Homebrew 安装可选的 `coreutils`，只为了给少数命令增加 timeout 保护。Lotus 托管安装默认跳过这个可选步骤，避免全局安装卡在 Homebrew。确实需要该增强时，可以自己安装：

```bash
brew install coreutils
```

如果 GitHub 网络短暂抖动，安装器会重试官方 gstack 下载；本机已经有 `~/.gstack/repos/gstack` 时，会优先使用现有 checkout 完成 skills 同步。没有可用 checkout 时，安装器会写入 bootstrap slash skills，等网络恢复后重新运行全局安装即可替换成完整 runtime。

## Lotus 可选 Codex 插件

Lotus 也可以托管 Codex 插件市场文件。当前仓库内置统一的 Lotus marketplace：

- `.agents/plugins/marketplace.json`

其中包含：

| Plugin | 用途 |
|---|---|
| `lotus-daloopa` | 单一 `daloopa` 顶层入口，内部路由 9 个 Daloopa 金融分析工作流 |
| `build-ios-apps` | iOS / SwiftUI / Xcode / Simulator 调试与预览工作流，位于 `plugins/build-ios-apps` |

安装：

```powershell
codex plugin marketplace add C:\Dev\Lotus
codex plugin add lotus-daloopa@lotus
```

```bash
codex plugin marketplace add ~/Dev/Lotus
codex plugin add lotus-daloopa@lotus
```

需要 iOS 工作流时再安装 `build-ios-apps@lotus`。Daloopa 插件内部保留 `setup`、`build-model`、`bull-bear`、`capital-allocation`、`earnings-flash`、`earnings-prep`、`ib-deck`、`precedent-transactions` 和 `research-note`，但它们不会分别占用顶层菜单。

`codex-security` 是 Codex 官方专有插件，不把插件运行时代码复制进 Lotus。安全审查的 Lotus 自带顶层入口仍是 `/security-auditor`；更完整的官方扫描工作流请在 Codex App 中安装或启用 Codex Security 插件。

## 仓库结构

```text
Lotus/
├── core/                 # 全局规则真源
├── skills/               # Lotus 自带 skills
├── plugins/              # 可选 Codex 插件
├── templates/            # 项目级模板
├── scripts/              # gstack 托管安装脚本
├── install.ps1           # Windows 安装器
└── install.sh            # macOS / Linux 安装器
```

## 安全与可回滚

- 覆盖前备份：安装器覆盖 `CLAUDE.md` 或 `AGENTS.md` 前会创建 `.bak`。
- 项目不被隐式修改：`-Global` / `--global` 只写全局路径，不写当前项目目录。
- 项目模板显式写入：只有运行 `-Project` / `--project` 才会写当前目录。
- 可卸载：删除对应全局规则文件和 skills 目录，或恢复 `.bak` 即可。

## 更新

进入 Lotus 长期目录后执行：

```powershell
cd C:\Dev\Lotus
git pull
.\install.ps1 -Global
```

```bash
cd ~/Dev/Lotus
git pull
./install.sh --global
```

这会刷新 Lotus 全局规则、Lotus 自带 skills、官方 gstack runtime 和默认顶层 gstack skills。项目级文件不会被自动覆盖。

## GitHub Actions 报 `Watch Upstream GStack` 失败

Lotus 使用 GitHub Actions 定时检查 `garrytan/gstack` 上游是否更新。如果 Actions 没有创建 PR 的权限，GitHub 会报：

```text
GitHub Actions is not permitted to create or approve pull requests.
```

修复方式：

1. 打开 GitHub 仓库设置。
2. 进入 `Settings -> Actions -> General -> Workflow permissions`。
3. 选择 `Read and write permissions`。
4. 勾选 `Allow GitHub Actions to create and approve pull requests`。

当前 workflow 已做容错：如果权限没开，会写入 workflow summary，不再因为无法创建 PR 而持续刷失败通知。

## 范围

Lotus 提供可维护的默认规则和工作流，不替代项目自己的技术约束、测试或人工业务决策。
