#!/usr/bin/env python3
"""合并 raw/ 里主路线与兜底路线抓到的所有分页，按 cid 去重，做完整性校验，输出评论全文。

用法：python3 -I build_report.py <输出目录>        # raw 文件在 <输出目录>/raw/
输出：comments_top.json · comments_replies.json · 评论全文.md；完整性结果打印到 stdout
退出码：0 = 全部抓齐；2 = 有楼没抓全（会列出 cid，可用兜底路线补抓后重跑）
"""
import glob
import json
import os
import sys
import time

out = sys.argv[1]
raw = os.path.join(out, "raw")


def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


top, replies = {}, {}
for path in sorted(glob.glob(os.path.join(raw, "top_*.json")) + glob.glob(os.path.join(raw, "ui_top_*.json"))):
    for c in (load(path) or {}).get("comments") or []:
        top[c["cid"]] = c
for path in sorted(glob.glob(os.path.join(raw, "reply_*.json")) + glob.glob(os.path.join(raw, "ui_reply_*.json"))):
    for r in (load(path) or {}).get("comments") or []:
        replies[r["cid"]] = r

detail = (load(os.path.join(raw, "detail.json")) or {}).get("aweme_detail") or {}
stats = detail.get("statistics") or {}

by_parent = {}
for r in replies.values():
    by_parent.setdefault(r.get("reply_id"), []).append(r)

missing = []
for c in top.values():
    want = c.get("reply_comment_total") or 0
    got = len(by_parent.get(c["cid"], []))
    if got < want:
        missing.append((c["cid"], want, got, (c.get("text") or "")[:30]))


def body(c):
    t = (c.get("text") or "").replace("\n", " / ")
    if c.get("image_list"):
        t += "（附图）"
    if c.get("sticker"):
        t += "（表情包）"
    return t or "（空）"


def meta(c):
    when = time.strftime("%Y-%m-%d", time.localtime(c.get("create_time") or 0))
    return f"赞{c.get('digg_count', 0)}·{c.get('ip_label', '')}·{when}"


with open(os.path.join(out, "comments_top.json"), "w") as f:
    json.dump(list(top.values()), f, ensure_ascii=False)
with open(os.path.join(out, "comments_replies.json"), "w") as f:
    json.dump(list(replies.values()), f, ensure_ascii=False)

with open(os.path.join(out, "评论全文.md"), "w") as f:
    f.write(f"# 评论全文：{(detail.get('desc') or '').splitlines()[0][:40] if detail.get('desc') else detail.get('aweme_id', '')}\n\n")
    if detail:
        a = detail.get("author") or {}
        f.write(f"- 作者：{a.get('nickname', '')} ｜ 发布：{time.strftime('%Y-%m-%d', time.localtime(detail.get('create_time') or 0))} ｜ 时长：{(detail.get('duration') or 0) // 1000}s\n")
        f.write(f"- 赞 {stats.get('digg_count')} ｜ 收藏 {stats.get('collect_count')} ｜ 转发 {stats.get('share_count')} ｜ 评论 {stats.get('comment_count')}\n")
    f.write(f"- 抓取：{time.strftime('%Y-%m-%d %H:%M')} ｜ 一级 {len(top)} 条 + 回复 {len(replies)} 条\n\n")
    for c in sorted(top.values(), key=lambda c: -(c.get("digg_count") or 0)):
        f.write(f"- **[{meta(c)}] {c['user']['nickname']}**：{body(c)}\n")
        for r in sorted(by_parent.get(c["cid"], []), key=lambda r: r.get("create_time") or 0):
            to = r.get("reply_to_username") or ""
            f.write(f"  - [{meta(r)}] {r['user']['nickname']}{' → ' + to if to else ''}：{body(r)}\n")

total = len(top) + len(replies)
print(f"一级 {len(top)} ｜ 回复 {len(replies)} ｜ 合计 {total} ｜ 视频显示评论数 {stats.get('comment_count', '未知')}")
if missing:
    print(f"未抓全的楼 {len(missing)} 个：")
    for cid, want, got, text in missing:
        print(f"  {cid} 应有 {want} 实得 {got} ｜ {text}")
    sys.exit(2)
print("所有楼中楼已抓齐")
