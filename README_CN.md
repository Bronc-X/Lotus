# Lotus

> AGENT的全局应用规则-Lotus。
> 起初，每次新建项目，都要做一系列重复的prompt的录入，skill的导入，不够优雅，效率拖沓，忘记build才是打开编程器的唯一目的。
> 现在，你拥有了Lotus，只需编写一次你的工程"宪法"，即可部署到所有平台。
> Lotus，全局管理Agent的智能docker。

Lotus 持续采用**最新、最安全、最稳定的全局 Agent 管理机制**。通过将规则注入到你本地机器上各 AI 工具的全局配置中，Lotus 同时管控**所有**项目中 AI 助手的行为——无需重复编写 prompt 指令，也无需为每个项目做繁琐的前期配置。

现在，Lotus 还把 **官方 [garrytan/gstack](https://github.com/garrytan/gstack)** 视为 gstack 运行时的唯一真源。一次全局安装会同时完成两件事：

1. 把 Lotus 的全局规则注入各个 AI 工具的全局配置。
2. 将官方 gstack clone / update 到 `~/.gstack/repos/gstack`，为支持的平台执行上游 setup，并开启自动更新。

**平台兼容性说明：**

| 平台 | 全局自动注入 | 备注 |
|---|---|---|
| Claude Code | ✅ 完全自动 | `~/.claude/CLAUDE.md` + 官方 gstack 运行时 |
| Antigravity / Gemini CLI | ✅ 完全自动 | `~/.gemini/GEMINI.md` 自动加载 |
| Codex CLI | ✅ 完全自动 | `~/.codex/AGENTS.md` + 官方 gstack 运行时 |
| OpenCode | ✅ 完全自动 | `~/.config/opencode/AGENTS.md` + 官方 gstack 运行时 |
| Aider | ✅ 完全自动 | `~/.aider.conf.yml` |
| Windsurf | ⚠️ 需手动粘贴 | 见下方步骤 |
| Cursor | ⚠️ 需手动粘贴 | 见下方步骤 |

<details>
<summary>📋 Windsurf 手动配置步骤（点击展开）</summary>

1. 打开 Windsurf
2. 点击右上角的 **自定义图标**
3. 在弹出面板中找到 **Rules（规则）** 
4. 点击 **「+ Global」** 按钮
5. 将 `core/AGENTS.md` 的完整内容复制粘贴进去
6. 保存即可，此后每次使用 Cascade 都会自动加载
</details>

<details>
<summary>📋 Cursor 手动配置步骤（点击展开）</summary>

1. 打开 Cursor
2.  进入 **Cursor Settings**
3. 在左侧找到 **General** → 找到 **「Rules for AI」** 输入框
4. 将 `core/AGENTS.md` 的完整内容复制粘贴进去
5. 保存即可，此后每个项目的 AI 对话都会自动携带这些规则

> 💡 如果你还需要项目级规则，可以在项目根目录创建 `.cursor/rules/` 文件夹，放入 `.mdc` 格式的规则文件。Lotus 的 `install.ps1 -Project` 命令会自动帮你生成。

</details>

## 🧬 第一性原理：为什么 Lotus 有效

别再追逐每一条花哨的 AI 新闻了。那种焦虑完全没有必要。

从底层来看，所有 LLM——GPT、Claude、Gemini——本质上都在做同一件事：将你的文本转化为**高维向量嵌入（Embedding）**，经过 Transformer **注意力层**处理后，**预测最可能的下一个 token**。理解这一个机制，就能改变一切：

1. **精准度 = 注意力聚焦度**：AI 输出的质量取决于模型的注意力机制能否在向量空间中精准锁定你的意图。Lotus 通过注入**高度结构化、无歧义的规则**，给注意力层提供清晰的高信噪比目标。模糊的 prompt 会分散注意力；Lotus 格式化的规则像激光一样聚焦它。
2. **上下文窗口 = 唯一的瓶颈**：每个模型的上下文窗口都是有限的。真正的技能不是"知道更多 prompt"——而是**管理好窗口中放什么**。Lotus 使用 Hub-and-Spoke 架构，保持全局规则精简通用，项目细节单独分层，确保你不会把宝贵的 context token 浪费在重复指令上。
3. **持久化 > 重复劳动**：没有 Lotus，每次新开会话你都要重新解释你的标准。有了 Lotus，你的规则在对话开始之前就已经被**预加载到操作系统层面**。AI 每次都会先读取你的宪法，自动的，无须提醒。

## ✨ 为什么选择 Lotus？

- 🧠 **思维模式，而非脚本**：Lotus 教会你的 AI *如何思考*，像一个资深架构师、产品经理和 QA 一样。它执行"[GStack](https://github.com/garrytan/gstack) 工作流"（CEO 评审 → 架构评审 → 编码 → 全局审查。感谢 [GStack](https://github.com/garrytan/gstack)，它帮助了我很多）。
- 🌍 **一次编写，处处运行**：一个单一的真理源（`core/AGENTS.md`）自动适配并安装到 Claude Code、Antigravity、Cursor、Windsurf、Copilot 等所有平台。
- 🚧 **零静默失败**：内置质量门禁保证你生成的代码包含正确的用户反馈、加载状态和美学一致性。
- ⚡ **无缝唤醒调用（`@` 和 `/`）**：在对话中随时使用平台原生触发器唤醒特定的专家角色和架构评审。
- 🗑️ **反插件膨胀**：市面上 95% 的插件和 skill 几周后就会沦为过时的，不再被人提及的几十行代码段。Lotus 反其道行之——每个 skill 都经过**人工精选、实战验证，保持最小够用**。我们只发布那些经得住真实生产工作流考验的技能。
- 🔄 **持续更新，前沿追踪**：Lotus 是一个**活的协议**，不是静态的配置文件。我们主动追踪 **Claude Code、Codex CLI 以及顶级开源 Agent 框架**的最新发布，将其中最安全、最经得起验证的模式融入 `core/AGENTS.md`，让你的规则永不过时。
- 🧘 **天然抗焦虑**：每周都有新框架？又一个"颠覆性"插件？放轻松。LLM 就是基于向量的 token 预测器。真正重要的只有两件事：**注意力精准度**（清晰的规则）和**上下文管理**（精简的指令）。Lotus 帮你搞定两者。你只管造你的产品。

## 🚀 零基础快速上手（小白专用）

从没用过终端命令？没关系。
如果你正在开始一个新项目或者刚拿到一台全新的电脑，只需将以下提示语**原封不动地复制粘贴**到你的 AI 助手中（如 Cursor、Claude、Antigravity），它会帮你自动完成全部安装！

> "这是一个全新项目目录。请在本地执行以下初始化步骤：
> 1. 将 `https://github.com/Bronc-X/Lotus.git` 克隆到系统的一个临时目录中。
> 2. 判断我的操作系统。运行临时仓库中的安装脚本，将 `nextjs` 模板应用到我当前目录（Windows: `install.ps1 -Project nextjs`，Mac/Linux: `install.sh --project nextjs`）。
> 3. 为确保在这台新机器上全局保留我们的工作流，也运行全局安装标志（Windows: `install.ps1 -Global`，Mac/Linux: `install.sh --global`）。
> 4. 完成后，删除刚才克隆的临时仓库。
> 5. 仔细阅读当前目录中新生成的 `AGENTS.md` 和 `.agents/rules/`，了解我的编码标准和设计语言。准备好了告诉我。"

*（注意：根据你的项目类型，将 `nextjs` 替换为 `vite` 或 `html`。）*

### 以后新建项目怎么用 Lotus？

全局安装完成后，Lotus 的核心规则（工作流、质量门禁等）已经自动驻留在你所有 AI 工具的全局配置中了，**不需要每次唤醒**。

对 Codex 来说，这表示 Lotus 会写入 `~/.codex/AGENTS.md`，然后由 Codex 在你打开任意本地仓库时自动继承这些规则。这里是“继承加载”，不是“把文件同步到每个项目目录”，所以如果你只执行了全局安装，项目根目录里**不会**自动出现新的 `AGENTS.md`。

对 Claude、Codex 和 OpenCode 来说，Lotus 还会把官方 gstack 运行时托管在 `~/.gstack/repos/gstack`。它是全局的、可更新的，不再依赖 Lotus 仓库里那份静态快照。

但如果你需要为新项目添加**项目级模板**（设计系统、技术栈约束），只需在新项目目录里运行一次：

```powershell
# Windows
C:\Dev\Lotus\install.ps1 -Project nextjs
```
```bash
# macOS / Linux
~/Dev/Lotus/install.sh --project nextjs
```

就这样。全局规则始终生效，项目模板按需叠加。

## 🔌 手动安装

### 第 0 步：将 Lotus 克隆到一个永久目录

选一个 Lotus 将长期存放的目录（以后在这里 `git pull` 更新）：

**Windows (PowerShell):**
```powershell
git clone https://github.com/Bronc-X/Lotus.git C:\Dev\Lotus
```
**macOS / Linux:**
```bash
git clone https://github.com/Bronc-X/Lotus.git ~/Dev/Lotus
```

### 第 1 步：全局安装（配置你所有的 IDE）

这会将 Lotus 规则注入到你机器上每个受支持的 AI 工具的全局配置中。

同时，它还会把**官方 gstack 上游**安装到 `~/.gstack/repos/gstack`，为 Claude/Codex/OpenCode 执行官方 setup，并开启 gstack 自动更新，让 skill 运行时始终跟着上游走。

对 Codex 而言，全局安装目标是 `~/.codex/AGENTS.md`。这一步不会改动你的本地项目目录。如果你希望项目里看得到 `AGENTS.md` 和 `.agents/rules/`，还需要在该项目目录里继续执行第 2 步。

**官方 gstack 运行时依赖：** `git`、`bash`、`bun`，以及 Windows 下的 `node`。

> ⚠️ **安全设计**：如果你已经有现有的配置文件（如 `CLAUDE.md`、`GEMINI.md`、`.aider.conf.yml`），安装器会在覆盖前自动创建 `.bak` 备份。你随时可以恢复。

**Windows (PowerShell):**
```powershell
C:\Dev\Lotus\install.ps1 -Global
```
**macOS / Linux:**
```bash
~/Dev/Lotus/install.sh --global
```

### 第 2 步：新项目初始化（可选）

在你新建的空白项目文件夹中，注入你首选的技术栈模板：

**Windows (PowerShell):**
```powershell
cd C:\Users\YourName\Projects\MyNewApp
C:\Dev\Lotus\install.ps1 -Project nextjs
```
**macOS / Linux:**
```bash
cd ~/Projects/MyNewApp
~/Dev/Lotus/install.sh --project nextjs
```

*（可用模板：`nextjs`、`vite`、`html`）*

## 🎯 工具唤醒机制（技能库）

你不需要记住复杂的 prompt；只需记住几个简单的命令。你可以在需要的时候动态**唤醒**特定的专家角色。

> 💡 **为什么这么少？** 我们刻意保持技能数量精简。这里的每个技能都经过了数月的真实项目迭代验证。如果一个技能不能持续产生价值，它会被**移除**，而不是"废弃"。始终坚持质量优先于数量。

**如何唤醒：**
触发语法取决于你使用的是可视化 IDE 还是命令行代理：
* **可视化 IDE（Cursor / Windsurf）**：使用斜杠命令 `/name`（例如 `/gstack`）。
* **命令行代理（Claude Code / Antigravity / Aider）**：使用 @ 提及格式 `@name`（例如 `@gstack`）。

### 可用唤醒列表：

#### Lotus 核心技能（跨所有平台可用）

1. **[`@gstack` / `/gstack`](https://github.com/garrytan/gstack)**
   * **功能**：Lotus 现在把它委托给全局安装的官方 gstack 运行时。`/office-hours`、`/plan-eng-review`、`/review`、`/investigate`、`/qa`、`/ship` 等工作流能力都以上游实现为准。
2. **[`@test-driven-development` / `/test-driven-development`](https://github.com/Bronc-X/Lotus/blob/main/skills/test-driven-development.md)**
   * **功能**：严格执行红绿重构（Red-Green-Refactor）。在编写业务逻辑之前强制要求 AI 先写出必定失败的测试。这是对抗 AI 幻觉的终极武器。
3. **[`@frontend-design` / `/frontend-design`](https://github.com/Bronc-X/Lotus/blob/main/skills/frontend-design.md)**
   * **功能**：Vercel Labs 级前端审美边界。屏蔽通用“AI 感”布局，强制明确设计锚点（如 Brutalist, Editorial 等），并在编写 CSS/React 之前应用设计可行性分析（DFII）。
4. **[`@debugging-strategies` / `/debugging-strategies`](https://github.com/Bronc-X/Lotus/blob/main/skills/debugging-strategies.md)**
   * **功能**：用科学的 Debug 循环取代枯燥的盲猜。强制 AI 提出假设，编写探测代码证伪，只有在根因确立后才提供修复方案。
5. **[`@security-auditor` / `/security-auditor`](https://github.com/Bronc-X/Lotus/blob/main/skills/security-auditor.md)**
   * **功能**：深度的 DevSecOps 审查。扫描 OWASP Top 10 漏洞、越权风险、原型链污染及弱密码学算法。建议提 PR 前执行。
6. **[`@feynman` / `/feynman`](https://github.com/Bronc-X/Lotus/blob/main/skills/feynman.md)**
   * **功能**：强制 AI 使用费曼技巧。用绝对通俗易懂的语言拆解复杂 Bug 或底层机制，然后再尝试修复。
7. **[`@polanyi-tacit` / `/polanyi-tacit`](https://github.com/Bronc-X/Lotus/blob/main/skills/polanyi-tacit.md)**
   * **功能**：唤醒深度分析模式。AI 会刻意寻找架构妥协、"防御性"代码块以及隐藏在表象下的组织技术债务。
8. **[`@auto-build` / `/auto-build`](https://github.com/Bronc-X/Lotus/blob/main/skills/auto-build.md)**
   * **功能**：静默执行 `npm install`、运行 `npm run build` 并检查编译错误，全程无需征求你的许可。
9. **[`@btw` / `/btw`](https://github.com/Bronc-X/Lotus/blob/main/skills/btw.md)**
   * **功能**：旁路快问模式。在不中断主线任务的情况下提出一个临时问题，AI 用 3-5 句话回答，不修改任何文件，然后无缝回到主线任务。

#### 源自 Claude Code 的原生斜杠命令（Lotus 复刻/适配到其他平台）

10. **[`@powerup` / `/powerup`](https://github.com/Bronc-X/Lotus/blob/main/skills/powerup.md)**
   * **什么时候用**：你刚开始用 AI 编程，或者觉得自己只用到了 AI 能力的 10%。
   * **功能**：相当于 Claude Code 版的「多邻国闯关」。一共分 **10 关**，从基础对话到后台任务管理等。
11. **[`@insights` / `/insights`](https://github.com/Bronc-X/Lotus/blob/main/skills/insights.md)**
   * **什么时候用**：你想看看自己的使用习惯有没有可以优化的地方。
   * **功能**：生成一份过去 **30 天**你使用 AI 的习惯交互报告，告诉你由于高频短视行为卡住的摩擦点。
12. **[`@loop` / `/loop`](https://github.com/Bronc-X/Lotus/blob/main/skills/loop.md)**
   * **什么时候用**：你有一些需要定期、反复执行的检查任务（比如每 5 分钟看一下部署状态）。
   * **功能**：设置一个会话内的定时循环任务。像一个小闹钟持续静音运行。
13. **[`@subagent` / `/subagent`](https://github.com/Bronc-X/Lotus/blob/main/skills/subagent.md)**
   * **什么时候用**：任务太复杂或需要并行处理。
   * **功能**：创建和管理**子 Agent（Subagent）**。拥有独立的上下文窗口以避免主干内容被塞爆。

## 🏗️ 架构（Hub-and-Spoke 中心辐射模型）

```text
Lotus/
├── core/                ← 🔶 核心真理（通用工作流、质量门禁）
├── skills/              ← 🔶 唤醒技能（@gstack、@feynman 等）
├── templates/           ← 🔶 技术栈（Next.js、Vite）与设计语言
└── install scripts      ← 🤖 自动生成各平台 IDE 适配器
```

## 🛡️ 安全性

Lotus 会触碰你的全局 IDE 配置文件。我们对此非常认真：

- **自动备份**：在覆盖任何已有文件（`CLAUDE.md`、`GEMINI.md`、`.aider.conf.yml` 等）之前，安装器会自动在同目录创建 `.bak` 备份。不会有任何内容被静默丢失。
- **只写规则文件**：Lotus 只向配置目录写入静态 Markdown 文件。它**不会**安装可执行文件、守护进程、浏览器插件或后台进程。
- **零网络调用**：安装脚本完全离线运行。无遥测、无数据分析、无外传请求。唯一的网络操作是 `git clone` / `git pull`，由你自己控制。
- **完全可逆**：要完全卸载 Lotus，只需删除注入的文件（如 `~/.claude/CLAUDE.md`、`~/.gemini/GEMINI.md`）或从 `.bak` 备份恢复。没有注册表、没有系统服务、没有任何隐藏残留。

## 🔄 更新哲学

Lotus **不是一个"设了就忘"的配置**。它是一个活的、持续演进的协议。

- **主力追踪目标**：[Claude Code](https://docs.anthropic.com/en/docs/claude-code)、[Codex CLI](https://github.com/openai/codex)，以及顶级开源贡献者的实战 Agent 框架。
- **我们追踪什么**：新的全局规则注入机制、更安全的权限模型、改进的上下文窗口策略，以及经过验证的工作流模式。
- **我们淘汰什么**：炒作驱动的功能、不稳定的 API，以及任何增加复杂度却没有可衡量价值的东西。
- **第一性原理过滤器**：在采纳任何新模式之前，我们会问：*这能帮助注意力更精准地锁定吗？这能减少上下文浪费吗？* 如果两者都不是，就不纳入。
- **如何保持最新**：只需 `git pull` 并重新运行安装器。你所有 IDE 上的全局规则会在几秒内刷新。

```bash
# 一条命令保持最新
cd /path/to/Lotus && git pull && ./install.sh --global
```
```powershell
# Windows 等效命令
cd C:\Dev\Lotus; git pull; .\install.ps1 -Global
```

## 📌 持久性：一次配置，永久生效

一旦 Lotus 全局安装完成，**你创建的每一个新项目都会自动继承你的规则**。不需要复制粘贴。不需要"记得添加配置文件"。规则存在于每个 AI 工具的操作系统级全局配置中，所以它们始终生效——无论你是在开一个全新的 Next.js 应用、调试一个遗留代码库，还是在同事的机器上结对编程。

在 Codex 里，“自动继承”指的是应用会自动读取 `~/.codex/AGENTS.md`，而不是 Lotus 会把 `AGENTS.md` 实体复制到你磁盘上的每一个仓库里。

对支持的平台来说，官方 gstack 运行时同样是全局常驻的。Lotus 会把它托管在 `~/.gstack/repos/gstack`，并在每次全局安装时重新执行上游 setup，所以这里的“永久生效”既包括规则，也包括运行时本身。

如需项目级别的覆盖（设计系统、技术栈），只需使用 `install.ps1 -Project <模板名>` 在上层叠加即可。全局规则不受影响。
