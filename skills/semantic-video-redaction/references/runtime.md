# 换电脑与安装

把整个 `semantic-video-redaction` 文件夹放入目标电脑的 Codex 技能目录：优先 `$CODEX_HOME/skills`，未设置时使用用户目录下 `.codex/skills`。保留 `SKILL.md`、`agents`、`scripts`、`references` 和 `assets`。压缩包仅用于搬运 Skill；不搬运旧虚拟环境、视频、截图、任务坐标或个人路径。

## 基础工具

先检查现有 Python、FFmpeg、FFprobe。推荐 Python 3.12；启动脚本接受 3.11–3.13，但本包的真实视频回放仅实测过 3.12。不要把其他 Python 版本能启动当成模型兼容已验证。

缺少系统工具时，用目标电脑已有的软件管理器安装，核对真实安装结果：

| 系统 | 常见安装方式 |
|---|---|
| Windows | `winget install --id Python.Python.3.12 --exact`；`winget install --id Gyan.FFmpeg --exact` |
| macOS / Homebrew | `brew install python@3.12 ffmpeg` |
| Debian / Ubuntu | 用发行版包管理器安装 Python、venv 支持和 `ffmpeg`；核对该发行版的 Python 版本，必要时另行安装 3.12 |

安装后检查 `python --version`、`ffmpeg -version`、`ffprobe -version`。Windows 有时需在新终端刷新 PATH。无管理器时使用 [Python](https://www.python.org/downloads/) 和 [FFmpeg](https://ffmpeg.org/download.html) 的正式下载入口，按系统选择安装方式。没有系统安装权限时可使用用户目录内的可信发行包并配置当前进程 PATH，不需要迁移原机器的绝对路径。

## 项目独立运行环境

以下命令从 Skill 文件夹运行；在其他位置运行时传入脚本实际路径。`work/redaction-runtime` 是当前任务的运行目录，可换位置。

```text
python scripts/bootstrap.py --runtime work/redaction-runtime --diagnose
python scripts/bootstrap.py --runtime work/redaction-runtime
```

脚本优先复用本机 `uv`，没有时使用标准库 `venv` 和 pip。依赖固定在 `scripts/requirements.txt`，不安装到系统 Python。`nudenet==3.4.2` 包内带 `320n.onnx` 权重，无需再次克隆仓库或申请凭据。

- Windows 运行解释器：`work/redaction-runtime/Scripts/python.exe`。
- macOS / Linux：`work/redaction-runtime/bin/python`。

下文以 `PY` 表示这个解释器的实际路径；它是命令示意，不是要求设置系统环境变量。

启动脚本实际执行一次空白图像推理，记录依赖版本、模型 SHA-256、CPU provider 和检查结果到运行目录的 `environment.json`。本版模型 SHA-256 的实测值为 `c15d8273adad2d0a92f014cc69ab2d6c311a06777a55545f2c4eb46f51911f0f`。版本相同但哈希改变时先调查来源，不直接沿用旧验证结论。

默认使用 `onnxruntime` CPU 版。没有 NVIDIA GPU 也可以运行；不默认安装 CUDA、PyTorch、SAM 或大型视觉语言模型。确实替换识别器时，记录该模型的类别、来源、版本、权重哈希和输入输出接口，重新跑视频样本；不能把下载模型等同于完成识别。

## 离线安装（仅需要时）

在与目标电脑**相同 OS、CPU 架构、Python 版本**的联网环境准备 wheelhouse：

```text
python -m pip download -r scripts/requirements.txt -d wheelhouse
```

在目标电脑运行：

```text
python scripts/bootstrap.py --runtime work/redaction-runtime --wheelhouse wheelhouse
```

此模式传入 `--no-index`，找不到匹配 wheel 时明确失败。Python 和 FFmpeg 也要提前准备。不要跨 Windows/macOS/Linux 复制虚拟环境或假定同一组 wheel 通用。公开依赖和模型的许可证随原发行包保留；本 Skill 不打包权重和私密素材。

## 失败定位

- 找不到 ffprobe：FFmpeg 安装不完整或 PATH 未刷新，修复后重新诊断。
- `No matching distribution`：核对 Python、系统架构和锁定版本；不要静默升级依赖。若必须改版本，记录变更并重跑模型推理、跟踪和短片导出。
- 模型文件缺失或 ONNX 推理失败：核对包和权重哈希，重新安装当前任务环境，不把失败解释成“没有目标”。
- 内存不足或片段太长：按镜头和连续目标分成较短任务，分别复核；不要用减少检测帧或只抽查来隐藏缺口。
