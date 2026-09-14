# Lotus 全量 Skill 优化对照

日期：2026-09-14

## 范围与结果

- 全量审查仓库原有 38 个入口：28 个 Lotus 核心入口（包含 gstack 兼容说明）及 10 个仓库插件入口。
- 新增 7 个 Lotus 维护的 Codex gstack 适配入口；共检查 45 个入口。适配入口替换调用规则，不声称与上游全部流程逐条等价。
- 本机同步 31 个已安装技能、86 个文件。未安装可选插件不安装；官方内置、外部插件缓存和无关个人技能不修改。
- gstack 上游运行组件保留，其他未覆盖的上游专项入口不改写；已有启用/禁用设置保留。
- 原有 38 个入口合计：2,002 → 961 行（减少约 52%）；90,551 → 60,410 字符（减少约 33%）。新增适配入口单列，不混入同口径统计。
- 行数忽略末尾空行，字符数统一 LF。这些是入口文本量，不是实测 Token、费用或全会话节省比例。按需读取的参考资料仍会增加上下文。

## 主要行为变化

| 问题 | 优化后 |
|---|---|
| 关键词泛化、主动抢占任务 | 描述聚焦具体触发条件；修复、审查、发布分别限定范围 |
| 小 Bug 需要多张表、三文件/三假设门槛 | 以证据和任务范围推进，不按任意计数提前停止 |
| 状态不变就询问继续；每轮汇报 | 状态不变是正常等待，只在可行动变化或用户要求时通知 |
| 默认安装、升级、自动索引、付费回退 | 与当前任务分离，只有已授权设置或资源使用才执行 |
| 方案微调强制全套 PPT/Word | 只修改指定内容，完整方案才使用完整要求矩阵 |
| iOS 无模拟器就要求用户手动操作 | 运行在范围内时自主启动合适模拟器；缺少 macOS/Xcode 则如实说明 |
| gstack 重型前言、强制采访/评审链 | 常用入口精简为任务范围与判断标准，保留专门运行时 |
| 安全审查扩展到监控、培训、合规建设 | 只审查相关信任边界，修复和外部测试需要相应授权 |

录音的来源哈希、人物/原声/发布授权、受限片段隔离；报价的计算口径、来源与费用排重；历史恢复的备份、provider 隔离和凭据保护均保留。监控、隐式触发、发布权限未因精简而放宽到任务范围外。

## 本机典型入口对照

| 本机目录 | 原行数 | 新行数 | 原字符数 | 新字符数 |
|---|---:|---:|---:|---:|
| recording | 116 | 51 | 3171 | 2980 |
| executive-sow-pricing | 103 | 45 | 10243 | 3290 |
| codex-history-bridge | 92 | 34 | 3445 | 2372 |
| mini-investigate | 141 | 18 | 4691 | 1160 |
| agent-reach | 137 | 27 | 4562 | 1734 |
| gstack | 235 | 16 | 14775 | 815 |
| gstack-ship | 2572 | 16 | 160880 | 1333 |
| gstack-investigate | 641 | 11 | 42662 | 946 |
| gstack-office-hours | 1817 | 11 | 113905 | 788 |
| gstack-browse | 718 | 11 | 41582 | 925 |
| gstack-review | 1111 | 11 | 69610 | 821 |
| gstack-qa | 1335 | 12 | 71460 | 894 |
| taste-skill | 113 | 26 | 5653 | 1839 |

上表包含原本较长的本地版本，因此与仓库的“上一轮已精简版本”是不同基线，不可混算。copy-editing 等不属 Lotus 的个人技能本次未纳入。

## 原有 38 个入口逐项对照

| 入口路径 | 原行数 → 新行数 | 原字符数 → 新字符数 | 当前触发描述 |
|---|---:|---:|---|
| plugins/build-ios-apps/skills/ios-app-intents/SKILL.md | 77 → 77 | 4544 → 4586 | Expose app actions or entities through App Intents, Shortcuts, Siri, Spotlight, widgets, or controls. |
| plugins/build-ios-apps/skills/ios-debugger-agent/SKILL.md | 51 → 13 | 2563 → 1141 | 使用 XcodeBuildMCP 构建、运行或排查 iOS 模拟器中的应用。 |
| plugins/build-ios-apps/skills/ios-ettrace-performance/SKILL.md | 14 → 14 | 1105 → 1105 | Capture and interpret iOS Simulator ETTrace profiles for latency and CPU-heavy stacks. |
| plugins/build-ios-apps/skills/ios-memgraph-leaks/SKILL.md | 76 → 76 | 3890 → 4015 | Capture and inspect iOS memgraphs for leaks, retain cycles, or memory growth. |
| plugins/build-ios-apps/skills/ios-simulator-browser/SKILL.md | 52 → 51 | 2992 → 3046 | Mirror iOS Simulator and hot-reload SwiftUI previews in the Codex browser. |
| plugins/build-ios-apps/skills/swiftui-liquid-glass/SKILL.md | 90 → 13 | 3663 → 997 | 实现或审查明确采用 iOS 26+ Liquid Glass 的 SwiftUI 界面。 |
| plugins/build-ios-apps/skills/swiftui-performance-audit/SKILL.md | 107 → 17 | 4950 → 1352 | 诊断 SwiftUI 卡顿、过度更新、主线程负载或渲染性能问题。 |
| plugins/build-ios-apps/skills/swiftui-ui-patterns/SKILL.md | 96 → 20 | 7267 → 1557 | 实现 SwiftUI 屏幕的导航、状态归属、布局或交互组件。 |
| plugins/build-ios-apps/skills/swiftui-view-refactor/SKILL.md | 14 → 14 | 1157 → 1157 | Refactor large SwiftUI views and clarify data flow or Observation ownership without changing behavior. |
| plugins/lotus-daloopa/skills/daloopa/SKILL.md | 37 → 38 | 1903 → 2311 | 使用 Daloopa 数据制作财务模型、财报分析或投资研究材料。 |
| skills/agent-reach/SKILL.md | 130 → 27 | 4178 → 1734 | 读取指定 URL、平台原生内容、GitHub、视频字幕或 RSS。 |
| skills/agent-training-loop.md | 24 → 25 | 1359 → 1325 | 用户明确要求迭代修复可复现 Bug 时，按新证据推进并验证。 |
| skills/ai-progress-workspace/SKILL.md | 26 → 26 | 1655 → 1587 | 为长运行 AI 任务实现真实事件驱动的进度界面和可编辑产物。 |
| skills/anysearch/SKILL.md | 46 → 46 | 2440 → 2361 | 检索实时网页事实、新闻或股票、CVE、DOI 等结构化标识符。 |
| skills/baseline-packager.md | 68 → 16 | 2446 → 872 | 把用户要求保留的已验证行为固化为可重跑的回归基线。 |
| skills/brandkit/SKILL.md | 26 → 26 | 1700 → 1590 | 设计品牌标识、视觉体系或品牌展示板。 |
| skills/btw.md | 43 → 8 | 760 → 353 | 用户用 btw 或 @btw 临时插问时，短答后返回主线。 |
| skills/codebase-memory-mcp/SKILL.md | 87 → 17 | 3286 → 1089 | 用已有代码图谱查询跨文件调用链、依赖或影响面；或按要求配置索引。 |
| skills/codex-history-bridge/SKILL.md | 34 → 34 | 2475 → 2372 | 查找本地 Codex 旧对话，或诊断恢复时的 provider 与配置错误。 |
| skills/executive-sow-pricing/SKILL.md | 43 → 45 | 3260 → 3290 | 为 AI/FDE 项目编写面向决策者的工作范围与报价方案。 |
| skills/feynman.md | 16 → 16 | 798 → 778 | 向非技术听众用白话和例子解释复杂机制。 |
| skills/frontend-design/SKILL.md | 21 → 21 | 1399 → 1283 | 设计或改进仪表盘、表单、表格等功能型网页界面。 |
| skills/goal.md | 85 → 15 | 3209 → 884 | 用户明确要求管理持久 Codex goal 时使用。 |
| skills/gsap.md | 69 → 18 | 1891 → 1077 | 实现或排查项目中明确采用 GSAP 的动画。 |
| skills/gstack.md | 24 → 24 | 858 → 1142 | 需 gstack 调研、评审、调试、QA 或发布流程时打开总入口。 |
| skills/image-2/SKILL.md | 113 → 11 | 2797 → 1130 | 用户要求 GPT Image 2 位图生成、参考图变体或图片编辑时使用。 |
| skills/insights.md | 60 → 11 | 822 → 817 | 根据用户指定的工作记录复盘重复摩擦与改进机会。 |
| skills/ios-codex-preview/SKILL.md | 78 → 13 | 3042 → 1260 | 在可用的 macOS/Xcode 环境搭建或修复 iOS 模拟器网页预览。 |
| skills/loop.md | 62 → 13 | 892 → 1018 | 用户用 loop 或 @loop 要求定期检查任务状态时使用。 |
| skills/mini-investigate.md | 135 → 18 | 4649 → 1160 | 修复范围清楚、可局部验证的小型软件 Bug。 |
| skills/polanyi-tacit.md | 20 → 20 | 808 → 799 | 分析复杂代码中未明说的业务约束与隐性惯例。 |
| skills/recording/SKILL.md | 51 → 51 | 3092 → 2980 | 将录音整理为可追溯内容母库，并制作用户选定的内容资产。 |
| skills/security-auditor/SKILL.md | 20 → 20 | 1474 → 1367 | 执行明确要求的安全审查，或调查具体漏洞与信任边界风险。 |
| skills/shadcn-preset-refactor/SKILL.md | 14 → 14 | 997 → 921 | 将指定 shadcn preset 应用于现有前端，保留业务行为。 |
| skills/subagent.md | 16 → 16 | 998 → 979 | 用户明确要求并行委派时拆分独立子任务并汇总。 |
| skills/taste-skill/SKILL.md | 26 → 26 | 1961 → 1839 | 设计或重设计需要鲜明视觉方向的营销网站、作品集或编辑型页面。 |
| skills/test-driven-development/SKILL.md | 22 → 22 | 1410 → 1338 | 用户或项目明确要求测试先行时，执行红绿重构。 |
| skills/workflow/SKILL.md | 29 → 29 | 1861 → 1798 | 将用户要求固化的已验证执行记录整理为可复用工作流或 Skill。 |

ETTrace 与 SwiftUI view-refactor 入口已具备精确范围和按需路由，检查后保留，没有为凑修改数量改写。其专业符号化、测量和行为保留约束仍有效。

## 新增 7 个 gstack 适配入口

| 入口 | 行数 | 字符数 | 触发条件 |
|---|---:|---:|---|
| adapters/gstack/gstack/SKILL.md | 16 | 815 | 用户明确使用 gstack 或询问其工作流选择时路由。 |
| adapters/gstack/gstack-browse/SKILL.md | 11 | 925 | 使用已安装的 gstack 浏览器检查网页、交互或渲染结果。 |
| adapters/gstack/gstack-investigate/SKILL.md | 11 | 946 | 定位原因不明、反复出现或跨模块的软件故障。 |
| adapters/gstack/gstack-office-hours/SKILL.md | 11 | 788 | 用户要求梳理产品需求、商业假设或方案取舍时使用。 |
| adapters/gstack/gstack-qa/SKILL.md | 12 | 894 | 按用户要求验证网页流程并修复发现的范围内问题。 |
| adapters/gstack/gstack-review/SKILL.md | 11 | 821 | 审查用户指定的代码差异或 PR，查找可证实的缺陷与回归风险。 |
| adapters/gstack/gstack-ship/SKILL.md | 16 | 1333 | 执行用户明确要求的提交、推送、PR 或版本交付步骤。 |

## 验证与边界

已通过：

- 45 个入口的 frontmatter 字段检查；33 个目录型技能通过官方 quick_validate（另 12 个为 Lotus 平铺入口，由安装器转换）。
- 所有入口 Markdown 引用的本地目标存在；UI YAML 可解析。
- 安装器回归测试：正常安装、上游失败、部分安装回退、Daloopa 单入口、适配入口覆盖与全局规则一致。
- 隔离同步测试：原文件备份哈希一致；私人 runtime、无关技能、config 不变；保留 UI 图标和隐式调用策略；重复同步幂等；不安装缺失技能。
- 本机同步后文件哈希检查与幂等检查通过；config.toml、AGENTS.md 与同步前逐字节一致。
- Codex 实际重新扫描成功，recording、executive-sow-pricing、codex-history-bridge 及七个适配入口都返回新版描述且可用。

未声称已完成：每个专业工作流的端到端业务运行或跨模型 A/B 实验。没有为了测试执行真实发布、付费 API、生产操作或 macOS 模拟器任务。运行组件未修改，语义效果仍应通过后续真实任务验证；不承诺最小 Token 或最大能力。

## 维护方式

Windows 仅更新已安装入口：`scripts/sync-codex-skills.ps1`。脚本备份所有被替换文件；根据备份 manifest 可按相对路径恢复旧文件，新增文件另行核对，不要整目录覆盖当前配置。

全局安装器在成功安装 gstack 后应用已有入口的 Lotus 适配正文，保留上游运行组件与 UI 设置。独立运行上游升级可能恢复生成的长提示词；重新运行 Lotus 同步即可恢复适配。

## 官方依据

- [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)：精准触发、渐进加载、移除过时脚手架、按任务读取文档、安全流程授权与完成边界。
- [Build skills](https://learn.chatgpt.com/docs/build-skills)：名称/描述先加载，使用时读取正文，描述保持明确的适用范围。

这是一套按官方原则维护的 Lotus 配置，不是 OpenAI 发布或认证的完整配置包。
