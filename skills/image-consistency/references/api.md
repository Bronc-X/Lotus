# API 与跨项目运行

## 运行环境

Python 3.10+，依赖见 Skill 根目录 `requirements.txt`。优先使用当前项目可用的 Python 环境；需要安装时在项目自己的虚拟环境安装依赖，不依赖某台机器的应用目录。

以下命令中的 `SKILL_DIR` 和 `PROJECT_DIR` 是需要由执行者替换的路径占位符，不是脚本内建变量。从实际加载的 SKILL.md 所在目录确定 `SKILL_DIR`，从当前项目确定 `PROJECT_DIR`。路径带空格时引用完整参数。

```text
python -m pip install -r "SKILL_DIR/requirements.txt"
python "SKILL_DIR/scripts/media_api.py" --help
```

脚本路径可来自全局 Skill，输入/输出应传当前项目的绝对路径；无需将整个 Skill 再复制到每个项目。跨机器迁移整个 Skill 文件夹，重新准备环境和本企业配置。

## 配置与协议

配置由已授权的启动器或企业凭据系统注入当前进程：

| 环境变量 | 用途 |
|---|---|
| MEDIA_API_BASE_URL | 服务地址，包含约定版本前缀；不带密钥或查询参数 |
| MEDIA_API_KEY | 当前企业授权密钥 |

不要把真实密钥写进命令、任务单、Skill、日志或聊天；不要打印全部环境变量。仅有继承的变量不代表可以替其他企业使用，先依据当前任务的授权上下文判断。缺少配置时告知缺少的变量名和安全注入方式。

支持同步 OpenAI 兼容图片协议：`GET /models`、JSON `POST /images/generations`、multipart `POST /images/edits`（多个 `image[]`），响应为 `data[0].b64_json` 或 `data[0].url`。不支持异步任务轮询或视频提交；也不保证任意标注兼容的服务都满足这些字段。

```text
python "SKILL_DIR/scripts/media_api.py" models
```

模型使用服务实际返回且本项目验证过的 ID，不根据显示名推断底层权重。用户未要求替换时，优先采用当前项目已验收的模型。

## 双参考编辑

```text
python "SKILL_DIR/scripts/media_api.py" --timeout 300 edit --model MODEL_ID --prompt-file "PROJECT_DIR/image-consistency/job/prompt.txt" --reference "PROJECT_DIR/inputs/identity.png" --reference "PROJECT_DIR/inputs/product.jpg" --size 1024x1536 --quality high --output "PROJECT_DIR/image-consistency/job/output/look-v1.png"
```

`--timeout` 在子命令之前；`--reference` 可重复且有顺序。替换路径、模型、尺寸和质量为任务实际值；服务不支持的可选参数不要发送。第三参考需加入第三个 `--reference` 并同步修改提示词，另做质量验证。

可选 `--params-file` 加载兼容参数 JSON，不能覆盖显式参数或凭据。任务单与质量记录均由执行者维护，脚本不会自动读取它们。

无参考分支已实现但没有真实服务质量验证：

```text
python "SKILL_DIR/scripts/media_api.py" --timeout 300 generate --model MODEL_ID --prompt-file "PROJECT_DIR/image-consistency/job/prompt.txt" --output "PROJECT_DIR/image-consistency/job/output/baseline-v1.png"
```

## 回执与恢复

图片同名 `.receipt.json` 记录模型、请求参数、提示词/输入/输出哈希、真实尺寸、状态与尝试次数；实际文件后缀取决于返回格式。完整提示词另存当前项目以便重跑，回执不包含其明文。

| 状态或 submission_outcome | 下一步 |
|---|---|
| TECHNICAL_SUCCESS | 打开图片，进行内容审核；不等于最终批准 |
| NOT_SUBMITTED | 修复本地配置、参考或输出名后再提交 |
| REJECTED | 检查明确拒绝原因与供应商记录，不假定未扣费 |
| UNKNOWN | 先核对已提交任务与扣费，不自动重试 |
| OUTPUT_UNAVAILABLE | 优先恢复本次结果，再判断是否需要新提交 |

退出码：0 技术成功，2 本地拒绝或明确接口拒绝等失败，3 结果未知或生成后产物不可用。以回执具体状态为准。一次命令只生成一张，不覆盖图片/回执；批量任务逐条使用唯一输出名。

模型已返回结果后若下载或写盘失败，用原输出路径恢复同一次结果：

```text
python "SKILL_DIR/scripts/media_api.py" recovery-info --output "PROJECT_DIR/image-consistency/job/output/look-v1.png"
python "SKILL_DIR/scripts/media_api.py" recover --output "PROJECT_DIR/image-consistency/job/output/look-v1.png"
```

恢复命令不调用付费生成 POST。私有恢复文件留在原输出目录，不进入分享包；Windows 由当前用户 DPAPI 保护，换用户或换机器时不能直接解密。若供应商的临时下载 URL 已过期且无任务查询/刷新能力，只能拿私有记录中的任务标识向供应商对账，不能承诺自动恢复。

## 离线检查

```text
python -B -m unittest discover -s "SKILL_DIR/tests" -p test_media_api.py -v
```

这些测试只使用内存模拟与本机回环服务器，不调用供应商或消耗生成额度。它们验证提交/失败/回执行为，不验证图片内容质量。
