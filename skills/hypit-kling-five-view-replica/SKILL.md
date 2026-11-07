---
name: hypit-kling-five-view-replica
description: 复用用户指定的11秒五视图换脸成片流程，用五张独立实拍、该次实际提示词和Hypit＋可灵视频编辑生成替换视频，并按需制作左右同步对比。
---

# 五视图成片复刻

本 Skill 对应用户指定的约11秒左右对比成片。右侧是五张实拍照片提供目标面部身份的生成版；左侧是用户提供的上一版生成视频，画面标题“原始视频”不表示它是摄像机原片。样本以视频编码负载哈希绑定，见 [reference-case.json](references/reference-case.json)。复用这次实际执行的路径与提示词；未记录的随机种子和人脸权重不能补写，也不承诺再次云生成得到逐像素相同结果。

## 输入与准备

需要：摄像机原片、同一目标人的五张独立实拍照片，以及制作对比时使用的左侧基准片。照片顺序固定为正面、画面向左45°、向右45°、向左90°、向右90°。本案例没有先合成三视图、没有拼图代替五张上传。素材路径由当前任务提供，案例哈希仅用于确认是否复用原素材；换素材时建立新工程，不改历史记录。

依赖 Python≥3.11、已安装的 Hypit及其Node环境、FFmpeg/FFprobe。脚本自包含，不依赖另一份 Skill。先检查原片关键转头和五图角度。若原片无需转换即可上传，直接使用；需要兼容副本时保留全片内容、PTS节奏及原声，不把格式改名当作转码。本例原片为HEVC 544×960、30fps、325帧，上传副本为H.264 720×1270、同为30fps/325帧。

从本 Skill 目录运行；路径参数由当前环境替换：

```text
python scripts/init_project.py --project <新工程> --hypit-cli <已安装Hypit入口> --source <摄像机原片> --source-upload <上传兼容副本> --front <正面实拍> --left45 <左45实拍> --right45 <右45实拍> --left90 <左90实拍> --right90 <右90实拍> --prompt-file assets/reference-prompt.txt
python scripts/hypit.py --project <工程> -- build build.svrun --runtime hypit.runtime.json --json
```

初始化器已执行check、plan及runtime选择。复用归档提示词 [reference-prompt.txt](assets/reference-prompt.txt)，不要用其他视频任务的改写版替换它。该提示词针对戴蓝色头套、额头包裹的主角；换场景时仅替换主体及保留项、实际素材标签，保存差异后再建立Build。五张实拍共同定义脸，原视频提供动作、表情、口型、身体、场景和手机成像条件。

## Hypit与可灵生成

Build写出exchange请求后，保留同一个job。请求中原片、上传副本及五张照片分别冻结；页面只上传一个uploadVideo和全部五张identities。Hypit的本地Provider管理等待、回执和Result；实际云生成由可灵网页完成。

本次实际参数：Kling 4.0、视频编辑的全能参考模式、1080p、自适应、页面约11秒、1条。逐项确认五图顺序和@视频1、@图片1至@图片5标签。历史费用为158灵感值，不是未来费率或新预算。按当前页面费用取得本次授权后只提交一次；不知道的种子、参考强度、蒙版参数保持未记录。网页恢复与下载规则见 [browser-and-qc.md](references/browser-and-qc.md)。

```text
python scripts/receipt.py --project <工程> --job <job-id> --status running --model <页面实际模型> --creation-resource-id <实际卡片编号>
```

生成完成后下载同一条结果。平台taskId未经验证就留null，卡片编号只记creationResourceId。下载失败时继续取回已有结果，不重新付费生成。用户经聊天工具提供的文件需记录实际来源，不声称其完整文件字节等于平台原下载。

```text
python scripts/complete.py --project <工程> --job <job-id> --video <本次已确认生成片> --model <页面实际模型> --provenance <browser-download或user-supplied-remux>
python scripts/hypit.py --project <工程> -- status <同一build-id>
python scripts/hypit.py --project <工程> -- get <同一build-id> --output edit.video --to output/edited.mp4
```

## 单条成片与左右比较

本参考的左右比较使用两段原始接收的生成片，均为1084×1912、24fps、265帧；逐帧n对n摆放，未做变速。单条“恢复原声”版是另一派生产物，按摄像机原片时钟输出30fps、325帧；不要把它混进24fps的样本对比，造成错误对齐。

制作用户指定样式的对比：左侧传入用户指定的基准片，右侧传入未经恢复时钟变速的output/edited.mp4。先核对左右确实同帧率、帧数和动作起点。基准片缺失时询问该文件，不能截取合成对比视频的左半边冒充摄像机原片，也不能为补左侧另开云生成。

```text
python scripts/compare_sync.py --left <用户指定基准片> --right <工程>/output/edited.mp4 --output <对比MP4> --left-label 原始视频 --right-label 生成视频 --height 1912 --font <本机中文字体>
```

上述标签用于复现本样本；新任务按左右真实身份命名。脚本保留比例，生成2168×1984的双栏画面，仅用左侧音轨，保留AI标记。它会拒绝不同帧率、帧数及不规则PTS；遇到不匹配先按实际动作事件检查和明确归一化，不靠同总时长宣称同步。背景/身体的粗对齐诊断不能证明表情逐帧相同。

需要独立的保留摄像机原声版时再运行：

```text
python scripts/finalize.py --generated <工程>/output/edited.mp4 --source <工程>/assets/source.mp4 --output <工程>/output/final.mp4 --parent-build <build-id> --parent-job <job-id>
```

原片为VFR时额外传入按原始PTS重采样的CFR副本作为--timing-source；音频始终取--source。默认最多5%整体retime；保留生成分辨率、肤质和色彩，核对原声编码packet哈希。本地派生MP4绑定父Build及输入输出哈希，不再提交虚构final Build。

## 检查与交付

按开始、中段、结尾及转头段检查目标鼻型、眼型、脸轮廓、耳前与头套边界，连续播放检查肤质、漂移、口型和动作节奏。比较版检查标签、左右顺序、头部与背景事件、首尾帧、单一音轨。上传了五张照片、Build完成或文件可播放，均不能代替目标脸的效果验收；不达标时先记录具体片段与偏差，不自动再次付费。

交付用户要求的单片或对比片即可。当前包绑定历史成片与技术证据；本次封装没有重新提交云生成。复用的机械脚本本地验证范围见 [validation.json](references/validation.json)，本次成片匹配和封装检查见 [case-validation.json](references/case-validation.json)。不将合成fixture的通过写成人脸视觉验证。
