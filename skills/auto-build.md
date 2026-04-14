---
description: 自动安装依赖与构建 (Auto Install & Build)
---
// turbo-all

此工作流用于项目初始化或大范围更新后，静默进行高危命令（安装与构建）的自动化执行。

1. 强制安装项目依赖：运行命令 `npm install`
2. 执行生产环境级别的应用构建：运行命令 `npm run build`
