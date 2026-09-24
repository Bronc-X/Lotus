---
name: brian-voice
description: 使用用户指定的 Brian 原声制作播客、视频画外音和中英文口播；适用于调用 brian-voice 或明确要求 Brian 声线。Brian 是独立说话人，不是 Toni 或用户本人。
---

# Brian Voice

使用本地已登记并获准的 Brian 原声与声线配置制作独立音频。不要替换 Toni 的技能、默认声线或资产。

## 公开包与本地配置

本包只提供执行规则和脚本，不携带 Brian 原声、声音提示、批准试听或机器配置。安装本包不会获得 Brian 的声音。执行前须有获准的本地 `voice.json`、`runtime.json` 和 `assets/`；缺少时明确报告，不能用其他声音冒充。要建立自己的声音时使用 `$ai-podcast` 的新 profile 流程。安装更新须保留这些本地私有文件。

## 声音与来源

- 先读 `voice.json` 和 `runtime.json`。来源、原声区间、实际参考文本与资产哈希均以 `voice.json` 为准；中文录音可以用于跨语言克隆，但不代表英文听感已验证。
- `narration` 用于平叙；`question` 可用于提问、追问或强调。按语义选择，不机械交替。参考文本必须对应 Brian 实际说出的字词，不能沿用 Toni 对相似稿件的转写。
- 用户已选定这份来源，并要求本地生成 Brian 版本；同一来源和本地合成范围内不重复索取声线授权。上传、公开发布或对外发送按当前任务授权执行。
- 这是参考声音克隆，不是专属微调模型。`listening_verified_languages` 只登记实际试听通过的语言；不得把成功生成、ASR 通过或用户选源写成合成听感批准。
- 若 `voice.json` 的声音提示仍待编码，先从已登记的原声 WAV 与对应文本创建 OmniVoice 提示，再记录真实 `.pt` 哈希。不要使用 Toni 的提示文件或把合成成品再编码成原声参考。

## 制作

已有定稿时直接使用；需要改写时按当前任务要求进行。不要擅自增加主持人身份、亲身经历、品牌开场或背景音乐。为比较不同声音制作同篇稿件时，保留相同正文，并另存实际朗读稿。

空行分段，保持句意完整。长稿应在自然语义边界拆分，避免一段包含过多内容导致省略、重说。画外音沿用镜头顺序；计时段落最多 30 秒，更长段落在完整句边界拆开。

```powershell
# $skillRoot 为本 SKILL.md 所在目录。
pwsh -NoProfile -File "$skillRoot/scripts/run.ps1" -Check
pwsh -NoProfile -File "$skillRoot/scripts/run.ps1" -TextFile $scriptPath -Language zh -OutputFile $wavPath
pwsh -NoProfile -File "$skillRoot/scripts/run.ps1" -JobsFile $jobsPath
```

多段、双语或逐镜头任务可使用 JSON 清单，路径相对于清单文件：

```json
{"jobs":[{"language":"zh","output":"outputs/brian.wav","chunks":[
  {"text":"第一段正文。","reference":"narration"},
  {"text":"接下来要解决什么问题？","reference":"question"}
]}]}
```

`reference` 默认 `narration`；按需为片段添加 `duration_seconds`，或为任务设置 `speed`、`gap_seconds`。默认 24 kHz 单声道、32 步、起始种子 42、CUDA float16，逐段断点续做。内容和配置相同才可复用缓存；变更后使用新输出文件名。

现有本地模型与依赖通过 `runtime.json` 定位。不下载替代模型、不修改共享运行环境；GPU 不可用时保留完成段落并报告，不静默切换服务或声线。若另有合成进程正在使用 GPU，协调串行执行，避免同时加载模型。

## 验证与交付

交付连续音频、实际朗读稿，以及脚本生成的时间映射与哈希。检查时长、非静音、削波及内容完整；正式长稿用本地 ASR 重点核对专名、数字、英文和漏句，发现错漏只重做相关段落。ASR 不验证声纹或自然度，听感结论须有实际试听证据。

向用户提供可播放结果和成品路径；不要把来源 QA 或未试听状态写成完成验收。此技能不包含自动上传或发布。

## 输出与续做保护

输出会同时占用同名 `.wav`、`.json`、`.txt`、临时文件和 `.parts` 缓存目录，必须与输入稿件、任务清单和配置分开。脚本会在写入前检查冲突；不要绕过报错来覆盖源文件。相同输出使用 `.lock` 排他锁，进程异常退出后先核对原进程已结束，再处理遗留锁。

脚本实现、运行环境、声音或参数变化会使旧缓存失效；此时换一个输出文件名继续，保留旧母带。技术生成成功仍需内容核对与实际试听，不能自动继承其他声线或设备的批准。
