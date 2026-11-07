---
name: hypit-kling-face-reproduction
description: 用 Hypit 管理原视频和五张独立实拍人像，通过可灵网页尝试人脸替换、收集真实回执与视频，并恢复原声和检查同步；适用于视频人脸复刻及身份未替换的失败判定，身份效果须单独验收。
---

# Hypit × 可灵人脸复刻

用 Hypit 的真实 Build 管理输入、等待、回执和 Result，用当前 Agent 可用的浏览器工具操作可灵。包内 Provider 只访问本地文件，不登录网页、不调用私有接口、不提交云任务，也不提供专用身份锁定能力。

“全能参考”五图视频编辑缺乏目标身份锁定保障。五张图上传齐全、云任务完成或 Build/Result complete 都不能证明换脸成功；必须检查输出是否采用目标五官。用户或视觉检查否决身份时，换脸任务仍未完成。不要在同一入口只加强提示词就重复整段付费；先核对可用的专用身份或局部编辑工具，或在费用明确获授权后做短样片/关键帧身份验收，再讨论整段。具体失败分支与匿名案例见 [身份未替换时](references/browser-and-qc.md#身份未替换时)。

依赖 Python≥3.11（仅标准库）、已安装且满足其 Node 版本要求的 Hypit、FFmpeg/FFprobe（libx264、PNG及可选比较用 drawtext）。本地技术测试使用 Hypit 0.2.17；其他版本先运行隔离测试，不自动升级。比较标题需要本机可用的中文字体，可传 `--font`，本包不分发字体。

## 准备工程

查看原片关键动作及五张照片，确认属于同一个目标人物。默认五图顺序为正面、画面向左45°、向右45°、向左90°、向右90°；照片分工以用户实际素材为准，不合成三视图、不凭空补角度。素材分工应是原片定义动作、表情、口型、身体和场景，五图定义同一目标身份；这是输入意图，不能据此认定输出采用了目标脸。

五图是这个模板的预置范围，不代表所有换脸都必须五张。用户采用不同参考数量时调整实际端口并重新验证，不复制照片凑数。

用参数提供安装与素材，路径不写进 Skill。初始化器接受 `--hypit-cli`（源码目录、`bin/hypit.mjs` 或可执行入口），也可查找 `HYPIT_CLI` 或 PATH 中的 `hypit`。不会安装依赖、申请账号或使用新凭据。执行 `--help` 查看参数：

```text
python scripts/init_project.py --project <新工程> --hypit-cli <Hypit入口> --source <原片> --source-upload <兼容原片> --front <正面> --left45 <左45> --right45 <右45> --left90 <左90> --right90 <右90>
```

`sourceUpload` 是同一原片的上传兼容副本；无需转换时可与原片使用同一文件。转容器不等于转码，文件改扩展名不等于兼容。只在页面限制或实际解码失败时制作副本，核对内容和时长；不为过时的模型限制擅自裁片。初始化后原片、上传副本、五张独立图分别形成实际图输入，逐一冻结资源和 SHA256。五图不能只带入一张。

`assets/prompt-template.txt` 以目标鼻梁、鼻尖、鼻翼、眼型、眼距和脸轮廓重建为优先，排除“只修肤色仍用原脸”。按实际 UI 标签调整 `--video-tag` 和五个 `--image-tags`；通过 `--subject`、`--preserve` 指定任务，不把本次客户衣着或头套写成通用默认。改提示词后重新 `check/plan` 并建立新本地 Build，取消尚未云提交的旧等待 Build；不要改已冻结请求冒充原始输入。

## 本地等待与网页生成

用包装器从工程目录运行同一已配置的 Hypit：

```text
python scripts/hypit.py --project <工程> -- check build.svrun
python scripts/hypit.py --project <工程> -- plan build.svrun --runtime hypit.runtime.json
python scripts/hypit.py --project <工程> -- build build.svrun --runtime hypit.runtime.json --json
```

初始化已执行 `runtime use hypit.runtime.json`。`work=unknown` 时先核对当前 workspace 和 Runtime 选择；用 `runtime status`、同一 Build 的 `status --runtime` 和 Worker 日志判断，别先重提任务。Build 写入 `exchange/<job-id>/request.json` 后只是等待页面操作，不是云端已提交。

浏览器步骤见 [browser-and-qc.md](references/browser-and-qc.md)。根据当前页面选择支持原视频编辑的模式，核对真实平台、模型、素材标签及计费；Kling 与 Seedance 不混称。上传请求中的一个 `uploadVideo` 和全部五张 `identities`，逐项检查页面实际接收数量。付费提交前确认本次账号、模型、用途和实际费用已获授权；本地排队不授予付费权限。只提交一次，保存界面实际状态与可验证的编号；不因等待、下载超时或浏览器附件错误重新付费生成。

外部过程用 `scripts/receipt.py` 写入同一个 job，状态限于实际观察：

```text
python scripts/receipt.py --project <工程> --job <job-id> --status running --model <真实模型标签> --creation-resource-id <实际界面资源编号>
```

平台任务 ID 未验证时留 `null`；界面卡片资源编号仅记 `creationResourceId`。Hypit 的 OperationReceipt 只用 `{id: "kling-ui-local:<job-id>"}`，这是本地人工作业编号；不要写缺少 `id` 的任意厂商字段对象。

## 下载、原声与检查

下载后先判断是否来自这次生成。多个“最终版”按实际内容、视频码流、回执和哈希识别，不按文件名或修改时间猜。下载失败时恢复已提交的同一任务；用户手动取回的文件可接收，但经聊天工具重封装的文件记 `user-supplied-remux`，不能声称等于平台原下载字节。

```text
python scripts/complete.py --project <工程> --job <job-id> --video <已确认的下载MP4> --model <真实模型标签> --provenance browser-download
python scripts/hypit.py --project <工程> -- status <同一build-id>
python scripts/hypit.py --project <工程> -- get <同一build-id> --output edit.video --to output/edited.mp4
python scripts/finalize.py --generated <工程>/output/edited.mp4 --source <工程>/assets/source.mp4 --output <工程>/output/final.mp4 --parent-build <同一build-id> --parent-job <job-id>
```

`complete.py` 保留已有费用、提交与来源回执，校验文件容器和 SHA256，异步 Provider 随后收集成真实 Result。脚本不会触发新云任务。输入为 MOV 时原片资产名以 `project.json` 为准。

`finalize.py` 的音频始终取自 `--source` 原片，视频时钟取自可选的 `--timing-source`，省略时使用原片。脚本逐帧检查实际 PTS；VFR 原片不能用平均帧率直接定时长，必须提供按原始 PTS 重采样的 CFR 副本，例如增加 `--timing-source <工程>/assets/sourceUpload.mp4`。显式 timing-source 仍为 VFR 时会拒绝。QC 分别记录原片、时钟副本、生成片与最终片的哈希和时钟依据。默认只允许≤5%的整体 retime；不以相同总时长声称动作逐帧一致。保留生成分辨率、像素格式和色彩标签，H.264 CRF16，无美颜锐化；优先复制原声，记录真实音画时长与逐音频 packet 哈希。差异、转码失败和视觉待检分别记录，不虚构通过。查看每秒联系图和关键转头/遮挡/口型段，确认五官身份、头套边界、肤质及原场景。最终 MP4 是 `edit.video` Result 的本地派生产物；QC 记录父 Build、原始输入与派生输出哈希及命令，不把派生片冒充新生成或另一个 Result。`media:Video` 的 authored Record 不能直接当作可实现 Logical Output 提交；本包不提供第二次 final Build。

可选左右比较用 `scripts/compare_sync.py --left <左视频> --right <右视频> --output <对比MP4> --left-label <真实左侧名称> --right-label <真实右侧名称>`，规则见 [browser-and-qc.md](references/browser-and-qc.md#左右比较)。导出后播放检查，交付只保留所需成片和必要记录。

## 本地验证范围

运行 `python scripts/test_local.py --hypit-cli <已装Hypit入口>` 可在隔离工程中生成合成媒体 fixture，执行真实 Hypit Build→等待→本地回执→Result→导出→原声/QC；不访问网页或云端，也不能证明换脸视觉质量。VFR 边界可单独运行 `python scripts/test_vfr.py`，仅验证两秒合成媒体，不接触 Hypit Runtime。当前实际执行范围与未验证项见 [validation.json](references/validation.json)。
