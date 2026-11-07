#!/usr/bin/env python3
"""可选：从 raw/detail.json 选 720p mp4 档位，带 Referer 下载视频（无需 Cookie）。

用法：python3 -I download_video.py <输出目录> [文件名，默认 参考视频.mp4]
"""
import json
import os
import subprocess
import sys

out = sys.argv[1]
name = sys.argv[2] if len(sys.argv) > 2 else "参考视频.mp4"
with open(os.path.join(out, "raw", "detail.json")) as f:
    a = json.load(f)["aweme_detail"]

rates = a["video"].get("bit_rate") or []
short = lambda b: min(b["play_addr"].get("width", 0), b["play_addr"].get("height", 0))
mp4 = [b for b in rates if b.get("format") == "mp4"]
pick = sorted([b for b in mp4 if short(b) >= 720], key=short)[:1] or mp4[:1] or rates[:1]
if not pick:
    sys.exit("detail.json 里没有可下载的视频档位")
url = pick[0]["play_addr"]["url_list"][0]
dst = os.path.join(out, name)
subprocess.run(["curl", "-sL", "-e", "https://www.douyin.com/", "-o", dst, url], check=True)
print(f"{dst} ({os.path.getsize(dst) // 1024} KB, {pick[0]['play_addr'].get('width')}x{pick[0]['play_addr'].get('height')})")
