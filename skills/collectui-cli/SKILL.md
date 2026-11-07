---
name: collectui-cli
description: 通过已配置的 collectui/shadcn 查看、安装和集成 ReUI、React Bits Pro 或 Motion 组件、页面块与模板；React Bits 的专业流程从此入口路由。
---

# 全局组件库 CLI

涉及 React Bits / React Bits Pro 的组件、页面块、模板或 Agent Kit 时，先读取 [React Bits Pro 集成指南](../react-bits-pro/SKILL.md)，保留其权限层级、导入、布局和验证要求。该指南作为内部参考，不需要单独唤起隐藏入口。认证继续通过现有 collectui 全局配置注入；上游本地 `.env.local` 示例不覆盖这里已验证的集中配置。

用户已授权在多个项目复用这三个库的 CLI 配置。全局命令为 `shadcn` 和 `collectui`；ReactBits 有 `@reactbits-starter` 与 `@reactbits-pro` 两个 registry。

- 在目标项目使用 `collectui add <组件名称> --yes`。它会先合并缺少的 registry，再调用 shadcn。也可用 `collectui view <组件名称>` 查看组件，或用 `collectui setup` 单独配置项目。
- 用 `-c <项目目录>` 指定项目。未初始化的前端项目先运行 `shadcn init`；初始化选项按当前项目决定，不自动新建另一套项目。
- 密钥已集中保存在当前用户的全局配置中。`collectui` 会把密钥注入子进程，不必复制到新项目。`collectui status` 只显示是否已配置。不要输出、提交或打包密钥。
- 用户原有的 registry、框架、别名、主题和项目密钥应保留。遇到 registry 地址冲突时停止并核实，不覆盖。
- 只有用户需要组件时才安装，不把测试组件自动装进每个项目。按该项目的已有命令进行必要验证。
- CLI 下载密钥与专属 MCP 密钥不同；CLI 使用不依赖 ReUI 或 Motion MCP 的启用状态。

已验证的组件标识：`@reui/blog-3`、`@reactbits-starter/globe-tw`、`@motion/hero-parallax-layers`。它们只是可选示例，不是项目默认组件。
