# SKU 商品事实与批准资产

商品最终图使用 `scripts/sku_gate.py`。该门禁核验商品事实审批、人物与当前商品原图哈希、必须保留的特征、任务提示词和生成回执，再以逐项审核结果发布 `approved/` 资产。脚本不能自动识别所有版型、商标和面料错误；审核人必须对照原图看清关键部位。没有商品负责人批准的事实单只能留在草案状态。

从 Skill 的 `assets/sku-contract.example.json` 复制模板到当前项目，填入该项目的两张真实参考、哈希、SKU ID、版本、来源证据、未知项和创作要求。只有商品负责人实际审查后，才能填写 `approval.status=APPROVED`、审核人和日期；不要从其他客户复制批准记录。人物参考只锁身份，商品参考锁当前款的可见事实。看不清的小字、背面或配件列为未知，不让模型自行补造；销售关键项未知时先补资料。

下面的 `SKILL_DIR`、`PROJECT_DIR` 均为执行者替换的本机路径：

```text
python "SKILL_DIR/scripts/sku_gate.py" prepare --spec "PROJECT_DIR/sku.json" --job-dir "PROJECT_DIR/image-consistency/job-1" --model MODEL_ID --size 1024x1536 --quality high
python "SKILL_DIR/scripts/sku_gate.py" generate --job-dir "PROJECT_DIR/image-consistency/job-1"
```

查看准备好的 `prompt.txt` 再运行生成；生成前程序会重新检查事实单、原图和提示词是否改变。已有候选或回执阻止再次生成，生成失败先查回执和恢复路径。

审核时参考 Skill 的 `assets/sku-quality-review.example.json`，将候选图哈希、真实审核人、每一必保留特征的 PASS/FAIL/NEEDS_REVIEW 与观察证据写到项目内 `quality-review.json`。未证实事实不得被说成已确认。只有全部 PASS 可执行：

```text
python "SKILL_DIR/scripts/sku_gate.py" release --job-dir "PROJECT_DIR/image-consistency/job-1" --review "PROJECT_DIR/image-consistency/job-1/quality-review.json"
python "SKILL_DIR/scripts/sku_gate.py" verify --job-dir "PROJECT_DIR/image-consistency/job-1"
```

分镜、视频和发布任务引用 `verify` 返回的批准图路径、SKU 版本与哈希。审核人字段是项目流程记录，不是加密身份认证。客户应在自己的资产权限体系中控制谁可修改事实单及审核记录。
