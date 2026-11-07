# douyin-comments

**抓取抖音单条视频完整评论区的 Agent Skill。** 抓取范围包括一级评论、全部楼中楼回复和视频详情，可选下载 720p 视频，最终输出一份按点赞排序的 `评论全文.md` 和原始 JSON。

请求在你自己已登录的 Chrome 页面里发出，签名交给页面自带的 SDK 计算。不需要 TikHub 之类的付费接口，不需要 Playwright，也不用逆向 a_bogus。

## 实测

| 视频 | 抓到 | 视频显示评论数 | 请求 / 耗时 | 验证码 |
| --- | --- | --- | --- | --- |
| 7 分钟 AI 工具视频 | 一级 83 + 回复 112 = 195 | 195 | 35 次 / 138 秒 | 无 |
| 46 分钟教程 | 一级 77 + 回复 58 = 135 | 135 | 63 次 / 252 秒 | 无 |

第一条与逐个手动点「展开回复」抓到的结果逐条比对，完全一致。手动方式用了约 6 分钟。

## 原理

抖音 Web 评论接口要带 a_bogus、msToken、uifid 等风控参数。如果只带 `device_platform` 和 `aid` 去调楼中楼接口，会立刻弹出文字点选验证码，请求一直挂起。原因是缺少页面正常请求里都有的那 30 多个公共参数。

所以这个 skill 不自己拼参数，而是**照抄页面的真实请求**：

1. `page_hook.js`：拦截页面自己发出的第一次评论请求，把它的 URL 和请求头记成模板。
2. `page_fetch.js`（主路线）：之后每次请求只替换 `aweme_id`、`cursor`、`comment_id` 三个参数，其余照抄。请求从页面内的 XHR 发出，由页面 SDK 补上签名。
3. `page_ui_expand.js`（兜底路线）：在评论区逐个点「展开 N 条回复」，由页面自己发请求，脚本只截获响应。这条路线慢，但不会触发风控。
4. `recv.py`：本机接收服务，页面把每一页响应 POST 到 `127.0.0.1` 落盘。
5. `build_report.py`：合并去重，逐楼核对回复数有没有抓全，再生成 `评论全文.md`。

请求节奏为每次间隔 2～4 秒，每 15 次额外停 8～15 秒。

## 依赖

- Claude Code，并连接 Claude in Chrome 浏览器扩展（在 Claude Code 里执行 `/chrome`）
- 已登录抖音的 Chrome
- Python 3（只用标准库）、curl

## 安装

```sh
git clone https://github.com/Pluviobyte/douyin-comments.git ~/.claude/skills/douyin-comments
```

也可以放到项目的 `.claude/skills/` 下。如果目标目录已存在，先检查里面的内容，不要直接覆盖。

## 使用

在 Claude Code 里给一个抖音视频链接，并说明要抓评论：

```text
抓一下这条视频的评论区 https://www.douyin.com/video/7xxxxxxxxxxxxxxxxxx
```

支持三种链接：`douyin.com/video/<id>`、带 `modal_id=<id>` 的主页链接，以及 `v.douyin.com` 短链。

产出默认写到当前项目的 `.internal/抖音评论/<aweme_id>/`：

```
raw/                  # 模板、每页原始响应、接收日志
comments_top.json     # 一级评论（去重）
comments_replies.json # 楼中楼回复（去重）
评论全文.md            # 按点赞排序，回复缩进在所属评论下面
参考视频.mp4           # 可选
```

完整流程见 [SKILL.md](SKILL.md)。

## 边界

- **不代点验证码。** 出现验证码时 skill 会停下，由你在 Chrome 里手动完成，然后继续。
- 只处理单条视频，不批量采集博主的全部作品，也不支持小红书和 B 站。
- 被删除、被折叠或仅作者可见的评论，接口不会返回，所以抓到的总数可能略少于视频显示的评论数。
- 上千条评论的视频：一级评论翻到约 500 条之后接口开始返回重复内容，被折叠的评论也拿不到，实测抓到 823 / 1067。
- 尚未实测：单个楼超过 20 条回复时的翻页。
- 仅用于个人研究和内容参考。请遵守抖音用户协议，控制频率，不要用于批量采集或商业分发。

## 致谢

整体思路参考了 [MediaCrawler](https://github.com/NanmiCoder/MediaCrawler)：公共参数集、uifid 请求头、先抓一级评论再逐楼抓回复、请求间留间隔。本仓库没有使用它的代码。
