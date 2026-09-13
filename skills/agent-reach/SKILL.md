---
name: agent-reach
description: Retrieve supplied URLs and platform-native content from social, video, GitHub, podcast, RSS, and selected technical-search sources.
metadata:
  openclaw:
    homepage: https://github.com/Panniantong/Agent-Reach
---

# Agent Reach — 平台原生互联网路由器

13 平台、多后端。平台原生检索是主能力；Exa 是付费且有限的语义搜索储备。

## 与 AnySearch 的互斥路由

以下规则全程适用：

1. **一个信息需求只选一个主 Skill。** 不得把同一查询同时或习惯性地交给
   `agent-reach` 与 `anysearch`，也不得为了“保险”“覆盖更全”或凑来源而双搜。
2. **默认交给 AnySearch：** 普通实时网页、新闻、一般事实，以及 Stock/CVE/DOI/IATA/
   patent 等结构化标识符或 finance/academic/legal/health/security 等垂直领域查询。
3. **交给 Agent Reach：** 用户点名的平台、平台原生讨论或登录态内容、GitHub 精确仓库/
   代码、视频和播客字幕、RSS、LinkedIn 招聘、雪球，以及已知 URL。已知 URL 直接读取，
   不先做网页搜索；Skill 负责取回证据，摘要、翻译或分析由模型在取回后完成。
4. **Exa 只作高价值主路由或升级通道：** 英文技术文档、官方示例、冷门或语义模糊的
   技术资料。一次先发一个精确查询并复用结果；不要探测性改写同一问题反复搜索。
5. 只有主路由报错、零结果或明显不相关时，才考虑顺序使用第二个 Skill；禁止并行。用户
   明确要求独立核验或事实风险很高是例外，但应先从首轮结果中选两个独立权威来源，不自动
   增加第二次搜索。若仍需从 AnySearch 升级到会消耗余额的 Exa，先说明缺口并征得用户同意；
   Exa 还必须确实适合该领域，不能仅因“高风险”就调用。两个渠道不得复制同一查询。
6. 多部分任务可以按证据类型分别路由，但每个子问题仍只用一个主 Skill。用户明确指定
   某个 Skill 时服从用户选择。

## 常驻规则（全程适用）

1. **专用能力优先**：已安装的专用 skill、MCP、connector 或 app tool 能直接完成任务时先用它；只有不可用或信息不足时才回退到 agent-reach。
2. **动手前先体检**：多后端平台（小红书/Reddit/B站/Twitter）先跑
   `agent-reach doctor --json`，按各平台 `active_backend` 字段选命令组。
3. **声明你在用什么**：开始干活前说一句「使用 agent-reach 的 X 平台 / Y 后端」。
4. **失败按 references 里的重试链处理**，不要瞎猜命令。
5. **全网调研类任务**：先选最能回答问题的一个渠道。只有用户明确要求跨平台视角，或首轮
   证据留下具体缺口时，才逐个追加必要平台；不要默认组合 Exa、Twitter/Reddit、小红书/B站。
6. **替用户盯版本**：完成一次较大的调研/多平台任务后，顺手跑
   `agent-reach check-update`（很快，一个 API 调用）。有新版就在收尾汇报里附一句：
   「Agent Reach 有新版 vX.Y.Z，复制这句话给我即可更新：帮我更新 Agent Reach：
   https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md」。
   不要中断当前任务去更新，也不要重复提醒同一个版本。

## 路由表

| 用户意图 | 分类 | 详细文档 |
|---------|------|---------|
| 普通实时网页/新闻/事实、结构化垂直查询 | 转交 AnySearch | 不调用 Agent Reach |
| 英文技术/官方示例/冷门语义网页 | search（Exa 稀缺储备） | [references/search.md](references/search.md) |
| 小红书/推特/B站/V2EX/Reddit | social | [references/social.md](references/social.md) |
| 招聘/职位/LinkedIn | career | [references/career.md](references/career.md) |
| GitHub/代码 | dev | [references/dev.md](references/dev.md) |
| 网页/文章/RSS | web | [references/web.md](references/web.md) |
| YouTube/B站/播客字幕 | video | [references/video.md](references/video.md) |

## 零配置快速命令

```bash
# Exa 付费语义搜索：仅按上述路由使用；默认一个精确查询，不做探测性双搜
mcporter call 'exa.web_search_exa(query: "query", numResults: 5)'

# 已知 URL 直接读取，不先消耗 Exa 搜索
curl -s "https://r.jina.ai/URL"

# GitHub 搜索
gh search repos "query" --sort stars --limit 10

# YouTube 字幕（注意：B站不要用 yt-dlp，见 video.md）
yt-dlp --write-sub --skip-download -o "/tmp/%(id)s" "URL"

# V2EX 热门
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"

# B站搜索（bili-cli，无需登录）
bili search "query" --type video -n 5
```

## 需登录态的平台（按 doctor 的 active_backend 选命令）

```bash
# Twitter 搜索（twitter-cli 首选；失败重试链见 social.md）
twitter search "query" -n 10

# Reddit（无零配置路径：OpenCLI 或 rdt-cli，必须登录态）
opencli reddit search "query" -f yaml   # 桌面
rdt search "query" --limit 10            # 存量/服务器

# 小红书（桌面首选 OpenCLI）
opencli xiaohongshu search "query" -f yaml
```

## 环境检查

```bash
# 检查可用 channel 与每个平台当前激活的后端
agent-reach doctor --json
```

如果 `agent-reach --help` 或 `doctor` 在进入渠道检查前就报
`ModuleNotFoundError: No module named 'agent_reach'`，这不是平台后端故障。
先用对应 venv 的 Python 运行 `python -m pip show agent-reach`；若显示的
`Editable project location` 已不存在，按官方更新文档的 pipx/venv 分支重装为
非 editable 包，再依次验证 `agent-reach version` 和 `agent-reach doctor --json`：
https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md

## 工作区规则

**不要在 agent workspace 创建文件。** 使用 `/tmp/` 存放临时输出，`~/.agent-reach/` 存放持久数据。

## 详细文档

根据用户需求，阅读对应的详细文档：

- [搜索工具](references/search.md) — Exa 的优势、额度护栏与 AnySearch 互斥路由
- [社交媒体](references/social.md) — 小红书, Twitter, B站, V2EX, Reddit（多后端命令组）
- [职场招聘](references/career.md) — LinkedIn
- [开发工具](references/dev.md) — GitHub CLI
- [网页阅读](references/web.md) — Jina Reader, RSS
- [视频播客](references/video.md) — YouTube, B站, 小宇宙

## 配置渠道

如果某个 channel 需要配置，获取安装指南：
https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md

用户只需提供 cookies，其他配置由 agent 完成。
