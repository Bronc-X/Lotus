# 录声与跨设备运行

## 可复用基线与设备选择

当前适配接口：OmniVoice 源码 `08be0b4ccbac3e13e374e86fbfead4b4cac343e2`，模型 `c5fdb5ccb189668d56333f77ba2629f4cd7535f4`。使用已有声线时以它的当前 profile 为准，不自动升级或降低采样步骤。脚本校验代码版本、profile 声明的模型版本和声音资产哈希；模型目录必须是该版本的已核实下载，runtime 中填写版本字符串本身不能证明模型字节正确。

| 电脑 | runtime.device | dtype | 行为 |
|---|---|---|---|
| Windows/Linux 无 NVIDIA GPU | cpu | float32 | 本地慢速生成，先测速，不要求购买 GPU |
| Apple Silicon Mac | mps | float32 起步 | OmniVoice 原生 MPS 路线，音频 tokenizer 由上游放 CPU；本 Skill 尚无 Mac 实机验收 |
| Intel Mac | cpu | float32 | 先检查所选 Python/PyTorch 是否有当前系统架构的可用包；不能安装时不宣称可运行 |
| NVIDIA GPU | cuda:0 | float16 | 单段一批，保留已批准参数 |
| 任意支持的设备 | auto | auto | 启动时按 CUDA→MPS→CPU 选择，写入结果；中途不静默换设备 |

MPS 内存不足或算子报错时保留记录，给新任务显式设 cpu、float32 和新输出路径再试。Intel Mac 缺兼容依赖或电脑内存不足时，可在用户已有且授权的远程电脑上运行同一 profile；不默认上传原声到公共 Space 或租用收费 GPU。没有任何可用运行环境时交付稿件及任务包，准确报告音频尚未生成。

## 环境安装

先查现成环境和模型，不重复下载。新电脑使用独立 Python 3.11/3.12 venv。命令中的 `python` 均指该 venv 的解释器；Windows 路径为 `.venv/Scripts/python.exe`，Mac/Linux 为 `.venv/bin/python`，无需 PowerShell。

```text
python -m venv .venv
# 在新 venv 中：Windows/Linux CPU 选择 CPU wheel 索引
python -m pip install torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cpu
# Apple Silicon 改用以下命令，不用 CUDA/CPU 专用索引
python -m pip install torch==2.8.0 torchaudio==2.8.0
git clone https://github.com/k2-fsa/OmniVoice.git
git -C OmniVoice checkout 08be0b4ccbac3e13e374e86fbfead4b4cac343e2
python -m pip install -e OmniVoice
```

只执行对应设备的一条 torch 安装命令。NVIDIA 按 [PyTorch 官方安装选择器](https://pytorch.org/get-started/locally/) 和实际显卡选择兼容 wheel，先核对版本；不改用户的共享 AI 环境。CPU 电脑不直接 `uv sync`：上游 Windows/Linux 源配置会选择 CUDA wheel。安装后 `python -m pip check`，确认 `torch`/`torchaudio` 匹配。记录实际版本用于重跑。

模型首次下载（需要网络和数 GB 磁盘；克隆代码不会带权重）：

```text
hf download k2-fsa/OmniVoice --revision c5fdb5ccb189668d56333f77ba2629f4cd7535f4 --local-dir models/OmniVoice
```

配置复制自 `assets/runtime.example.json`；路径相对 runtime 文件，填入真实源码与模型目录。`python_executable` 不是自动启动器，调用命令自身必须使用正确 Python。生成脚本离线加载，缺模型会报错，不暗中下载或调用付费 API。模型安装后记录来源/revision 和文件校验清单；修改模型后使用新 profile/输出路径。

## 人工原声 → profile

让说话人在安静、少反射的房间用稳定距离录 30–60 秒自然表达；含普通叙述、追问、强调即可。录音内容由本人逐字说出，避免音乐、第二个人、远场和过载。更多样本的价值是挑出干净且表达合适的片段，不是模型一次吃越长越好。

从原录音选择完整句子的 3–10 秒，转单声道 PCM WAV。保留原始文件，参考逐字稿人工校对。需要 FFmpeg 时用当前环境已有可执行程序，例如：

```text
ffmpeg -i source.m4a -ss 10.2 -t 9.9 -ac 1 -ar 24000 -c:a pcm_s16le reference.wav
python <skill>/scripts/clone_voice.py --runtime runtime.json --reference reference.wav --transcript reference.txt --voice-id my-voice-v1 --language zh --output voices/my-voice-v1
```

切点来自实际录音，不照抄示例数值。音量小先区分增益低与信噪比差；放大不会去掉混响。低信噪比应重录。程序创建新目录、原声副本、prompt、来源哈希、精确转录和候选 profile，不覆盖既有版本。

生成短样通过基本运行检查后，再生成可比较的 40–60 秒试听；用户选定后在本地 profile 记录选择原话、样本哈希、语言、参数与 `listening_verified_languages`。不得程序自行填“用户已批准”。多种提示用独立 `narration` / `question` 资产，按语义指定；当前 Toni 两份提示直接复用，不需要再编码。

## profile → 连续播客

```text
python <skill>/scripts/synthesize.py --runtime runtime.json --voice-profile voices/my-voice-v1/voice.json --check
python <skill>/scripts/synthesize.py --runtime runtime.json --voice-profile voices/my-voice-v1/voice.json --text-file short-probe.txt --language zh --output audio/probe.wav
python <skill>/scripts/synthesize.py --runtime runtime.json --voice-profile voices/my-voice-v1/voice.json --jobs-file jobs.json
```

复用 Toni 时 `--voice-profile` 指向当前 toni-voice 的私有 `voice.json`；用它的 runtime 复制出 CPU/Mac 配置，补 `model_revision` 并只替换设备、精度和机器路径。原文件保持不变。

`elapsed_seconds / duration_seconds` 是此次短样的实时率，首次含加载成本。用它估算长稿等待时间并说明误差；不是对所有电脑的速度承诺。默认每段 1 批、32 步、种子 42+段序。正常语速分段，完整句边界优先；大段拆成约 10–25 秒便于局部修复。

任务模板见 `assets/jobs.example.json`。也可用 `chunks: [{"text":"...","reference":"narration","duration_seconds":5}]` 替代 text_file；reference 需在 profile 内存在。只有配镜头明确指定时用 duration，单段 ≤30 秒，误差检查 ≤0.1 秒。任务里设 speed/gap_seconds 可改变语速和段间间隔；变更配置/文本后使用新输出路径。

WAV 旁会有 `.txt`、`.json` 及 `.parts/`；元数据记录实际段落时间、设备、精度、声线版本、耗时、输入指纹和输出哈希。同样输入恢复时校验缓存；不匹配就报错，不混用旧片段。定时段保留原长；普通段只裁首尾静音，保留内部停顿。默认整条 RMS -20 dBFS、峰值 ≤-1 dBFS，不能把它称为 LUFS 标准化。

发布转码示例（以平台当时规范为准）：

```text
ffmpeg -i audio/episode-v1.wav -map_metadata -1 -c:a libmp3lame -b:a 192k release/episode-v1.mp3
ffprobe -v error -show_format -show_streams release/episode-v1.mp3
```

另检查 MP3 实际时长和听感，剔除工程绝对路径等不应随成品发布的标签。母版不覆盖。

依据：[OmniVoice 官方 README 与 Python API](https://github.com/k2-fsa/OmniVoice)、[固定源码 MPS tokenizer 路由](https://github.com/k2-fsa/OmniVoice/blob/08be0b4ccbac3e13e374e86fbfead4b4cac343e2/omnivoice/models/omnivoice.py)、[模型](https://huggingface.co/k2-fsa/OmniVoice)。部署时核对依赖支持，原生 Mac 性能仍需目标机实测。
