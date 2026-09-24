# 播客技能包

`ai-podcast` 是 AI 单人播客入口。按当前输入接续，已有稿件、已确认声线或已生成段落不用从头重做。

| Skill | 职责 | 何时需要 |
|---|---|---|
| `ai-podcast` | 材料 → 稿件 → 本地声线 → 分段音频 → QA → 按授权分发 | AI 单人口播 |
| `recording` | 录音证据库、说话人核对、原声剪辑与内容资产 | 原声访谈或需要追溯录音证据 |
| `toni-voice` | 执行本地 Toni profile，核对资产和运行参数 | 明确指定 Toni |
| `brian-voice` | 执行本地 Brian profile，禁止混用 Toni 配置 | 明确指定 Brian |
| `broncin-style-writer` | 使用私人风格档案写作，不编造经历或旧观点 | 本人署名风格写作 |
| `lieflat-less-ai-tone` | 只修改命中规则的表达，保留事实、否定、限定与结构 | 成稿需要清理表达 |

只有一段录音用来建立声线，不必创建 recording 项目。只有文章和现成声线，也不必经过 recording。写作与声音是独立选择；文风不决定说话人身份。

## 安装与私人配置

通过 Lotus 安装器安装这些技能；仅更新已安装项时使用 `scripts/sync-codex-skills.ps1`。声音包与文风包按公开文件白名单更新，保留本地 profile、runtime、原声、提示文件和私人风格证据。相同文件重复安装不会改写已有备份；后续版本更新会备份当时被替换的文件。

公开仓库不分发 Toni/Brian 的可复刻声音资产，也不分发个人 Flomo 语料。没有这些本地配置时，专用适配器应停止并说明缺项。新使用者从 `ai-podcast` 的示例 runtime 和自己获准的人工原声建立独立 profile，不沿用他人的姓名或批准状态。

## 本次检查修正

- 合成前检查所有输出及附属文件，阻止覆盖输入文稿、任务清单、配置与声音资产；同一输出使用排他锁。
- 数值参数拒绝 NaN、无穷和不合法范围；固定声线核对身份前缀、模型代码版本、资产哈希与设备信息。
- 缓存指纹包含执行脚本及运行环境；修改实现、声音或参数后使用新的输出名，不覆盖既有母带。
- 发布清单核对候选文件、账号、平台和动作；拒绝篡改、重复路径与链接文件。授权必须来自实际用户指令，不能由脚本自行产生。
- 安装与同步保留私人文件；文案清理规则不得删掉否定、范围、列表成员或加强原本不确定的判断。

## 可重跑检查

在仓库根目录运行：

```text
python -B skills/ai-podcast/scripts/self_test.py
python -B scripts/test-podcast-contracts.py
python -B scripts/test-voice-packages.py
pwsh -NoProfile -File scripts/test-skill-sync.ps1
bash scripts/test-installers.sh
```

安装测试需要 PowerShell 和 Bash；Recording 脚手架测试需要 PowerShell。测试使用临时目录，不运行真实平台发布。

2026-09-24：上述检查通过，六个入口通过 Skill 结构校验。Windows CUDA 上三个合成入口分别生成约 5.35、6.31、5.35 秒短样；WAV 解码、有限样本、非静音、峰值、哈希与重跑复用均通过。技术短样不等于人工听感确认；没有在本次检查中上传任何播客。

已知验证边界见 [ai-podcast 验证范围](../skills/ai-podcast/references/validation.md)。Mac 实机、任意新说话人、长稿内容完整性和平台审核仍需具体项目验证，不能由一次脚本检查代替。
