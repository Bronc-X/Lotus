# Lotus

> AGENT的全局应用规则-Lotus。
> 起初，每次新建项目，都要做一系列重复的prompt的录入，skill的导入，不够优雅，效率拖沓，忘记build才是打开编程器的唯一目的。
> 现在，你拥有了Lotus，只需编写一次你的工程"宪法"，即可部署到所有平台。
> Lotus，全局管理Agent的智能docker。

Lotus 持续采用**最新、最安全、最稳定的全局 Agent 管理机制**。通过将规则注入到你本地机器上各 AI 工具的全局配置中，Lotus 同时管控**所有**项目中 AI 助手的行为——无需重复编写 prompt 指令，也无需为每个项目做繁琐的前期配置。

**平台兼容性说明：**

| 平台 | 全局自动注入 | 备注 |
|---|---|---|
| Claude Code | ✅ 完全自动 | `~/.claude/CLAUDE.md` 自动加载 |
| Antigravity / Gemini CLI | ✅ 完全自动 | `~/.gemini/GEMINI.md` 自动加载 |
| Codex CLI | ✅ 完全自动 | `~/.codex/AGENTS.md` 自动加载 |
| OpenCode | ✅ 完全自动 | `~/.config/opencode/AGENTS.md` |
| Aider | ✅ 完全自动 | `~/.aider.conf.yml` |
| Windsurf | ⚠️ 需手动粘贴 | 见下方步骤 |
| Cursor | ⚠️ 需手动粘贴 | 见下方步骤 |

<details>
<summary>📋 Windsurf 手动配置步骤（点击展开）</summary>

1. 打开 Windsurf
2. 点击右上角的 **自定义图标**（书本图标）
3. 在弹出面板中找到 **Rules（规则）** 选项卡
4. 点击 **「+ Global」** 按钮
5. 将 `core/AGENTS.md` 的完整内容复制粘贴进去
6. 保存即可，此后每次使用 Cascade 都会自动加载

> ⚠️ Windsurf 全局规则有 **6,000 字符上限**。如果内容超限，只保留核心原则和意图路由部分即可。

</details>

<details>
<summary>📋 Cursor 手动配置步骤（点击展开）</summary>

1. 打开 Cursor
2. 点击右上角的**齿轮图标** → 进入 **Cursor Settings**
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

- 🧠 **思维模式，而非脚本**：Lotus 教会你的 AI *如何思考*，像一个资深架构师、产品经理和 QA 一样。它执行"[GStack](https://github.com/jxnl/gstack) 工作流"（CEO 评审 → 架构评审 → 编码 → 全局审查。感谢 [GStack](https://github.com/jxnl/gstack)，它帮助了我很多）。
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

#### Lotus 自研技能（跨所有平台可用）

1. **[`@gstack` / `/gstack`](https://github.com/Bronc-X/Lotus/blob/main/skills/gstack.md)**
   * **功能**：触发精英级多角色开发者工作流。AI 会在编写代码前，在产品经理、架构师、构建者和 QA 之间显式切换角色，确保系统完整性。
2. **[`@feynman` / `/feynman`](https://github.com/Bronc-X/Lotus/blob/main/skills/feynman.md)**
   * **功能**：强制 AI 使用费曼技巧。用绝对通俗易懂的语言拆解复杂 Bug 或底层机制，然后再尝试修复。
3. **[`@polanyi-tacit` / `/polanyi-tacit`](https://github.com/Bronc-X/Lotus/blob/main/skills/polanyi-tacit.md)**
   * **功能**：唤醒深度分析模式。AI 会刻意寻找架构妥协、"防御性"代码块以及隐藏在表象下的组织技术债务。
4. **[`@auto-build` / `/auto-build`](https://github.com/Bronc-X/Lotus/blob/main/skills/auto-build.md)**
   * **功能**：静默执行 `npm install`、运行 `npm run build` 并检查编译错误，全程无需征求你的许可。
5. **[`@btw` / `/btw`](https://github.com/Bronc-X/Lotus/blob/main/skills/btw.md)**
   * **功能**：旁路快问模式。灵感来自 Claude Code 原生的 `/btw` 命令。在不中断主线任务的情况下提出一个临时问题，AI 用 3-5 句话回答，不修改任何文件，然后无缝回到主线任务。跨所有平台可用，不仅限于 Claude Code。

#### 源自 Claude Code 的原生斜杠命令（Lotus 复刻/适配到其他平台）

以下命令原本是 Claude Code CLI 的独有功能。Lotus 将它们的**核心行为逻辑**提炼为 skill 文件，使其他平台的用户也能获得相似的体验。

6. **[`@powerup` / `/powerup`](https://github.com/Bronc-X/Lotus/blob/main/skills/powerup.md)**
   * **什么时候用**：你刚开始用 AI 编程，或者觉得自己只用到了 AI 能力的 10%。
   * **功能**：相当于 Claude Code 版的「多邻国闯关」。一共分 **10 关**，每关大约 2 分钟，20 分钟就能通关。从最基础的"怎么和代码库对话"、"怎么撤销 AI 的操作"，到进阶的"怎么把任务放到后台跑"、"怎么让 AI 记住你的偏好"、"怎么创建子 Agent"、"怎么用手机远程控制"——每一关都是 Anthropic 帮你划好的重点。与其到处找零散教程，不如先把这十关打通。在 Claude Code 中直接输入 `/powerup` 即可启动；在其他平台触发 `@powerup` 会获得同等内容的文字版教学。
7. **[`@insights` / `/insights`](https://github.com/Bronc-X/Lotus/blob/main/skills/insights.md)**
   * **什么时候用**：你已经用了一段时间，想看看自己的使用习惯有没有可以优化的地方。
   * **功能**：生成一份过去 **30 天**你使用 AI 编程的习惯报告。这份交互式 HTML 报告会告诉你：最常用的命令是什么、哪些操作模式高度重复、哪里经常卡住或反复 debug。更妙的是，它还会推荐一些可以自定义的命令或现成的 Skill 来消除这些摩擦点。**这是回顾你来时的路，非常有正反馈！** 在 Claude Code 中输入 `/insights` 即可生成报告；在其他平台触发 `@insights` 会引导 AI 对当前项目的历史对话做类似的回顾与建议。
8. **[`@loop` / `/loop`](https://github.com/Bronc-X/Lotus/blob/main/skills/loop.md)**
   * **什么时候用**：你有一些需要定期、反复执行的检查任务（比如每 5 分钟看一下部署状态、持续监控 PR 变化）。
   * **功能**：设置一个会话内的定时循环任务。你给出间隔时间和一个指令（例如 `/loop 5m 检查部署状态`），AI 就会像一个小闹钟一样定期自动执行。这个循环是会话内的——关掉终端就停了，不会变成一个系统级的后台守护进程，非常安全可控。在 Claude Code 中直接使用 `/loop <间隔> <指令>`；在其他平台触发 `@loop` 后 AI 会用平台原生能力模拟类似的定期提醒与执行。
9. **[`@subagent` / `/subagent`](https://github.com/Bronc-X/Lotus/blob/main/skills/subagent.md)**
   * **什么时候用**：你的任务太复杂了，一个 AI 顾不过来；或者你想让 AI 并行处理多件事。
   * **功能**：创建和管理**子 Agent（Subagent）**。每个子 Agent 都有自己独立的上下文窗口、独立的系统提示、独立的工具权限。你可以让一个子 Agent 专门负责搜索代码库、另一个专门跑测试、主 Agent 只负责写核心逻辑——互不干扰。这是解决"上下文窗口挤爆"的终极方案：把噪音隔离到子进程里，主线保持干净。在 Claude Code 中使用 `/agents` 管理；在其他平台触发 `@subagent` 会引导 AI 用多轮对话模拟类似的任务拆分与隔离模式。

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

如需项目级别的覆盖（设计系统、技术栈），只需使用 `install.ps1 -Project <模板名>` 在上层叠加即可。全局规则不受影响。
