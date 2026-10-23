# 当前部署：GitHub Actions + 仓库存储 + Secrets + Pages

- 仓库：https://github.com/zhouliangchen/TrendRadar
- 在线报告：https://zhouliangchen.github.io/TrendRadar/
- Actions：https://github.com/zhouliangchen/TrendRadar/actions/workflows/crawler.yml
- Secrets：https://github.com/zhouliangchen/TrendRadar/settings/secrets/actions
- 本地目录：`G:\GitHub\TrendRadar`

## 运行与存储

采用上游 v6.11.0，每小时第 33 分钟运行一次（GitHub 定时任务可能延迟），显示时区为 Asia/Shanghai。
保留默认 11 个热榜平台及关键词，报告模式 current。Hacker News 使用官方 RSS；雅虎财经源因试运行返回 404/429 暂停。
源码位于 master 分支；运行时从 data 分支恢复 SQLite 和历史报告，运行结束后提交回 data。
输出文件默认保留 30 天；旧版本仍可能存在于 Git 历史中，需长期关注仓库体积。
GitHub Pages 通过官方 Actions 工作流部署，仅上传 HTML 报告，不上传数据库。
本仓库和在线报告均为公开内容；密钥仅存放在 Actions Secrets。
无需购买服务器、对象存储或域名。AI 接口费用/额度由提供商计量。

## AI 分析

使用用户指定的智谱 Anthropic Messages 接口，配置均通过 Secrets 注入：

| Secret | 用途 |
| --- | --- |
| AI_API_KEY | 智谱 API Key |
| AI_MODEL | LiteLLM 模型名，`anthropic/GLM-5.3` |
| AI_API_BASE | `https://open.bigmodel.cn/api/anthropic` |
| AI_ANALYSIS_ENABLED | `true`，设 `false` 可停用 |
| AI_TRANSLATION_ENABLED | 可选；只有设 `true` 才翻译标题，默认关闭 |
| WEWORK_WEBHOOK_URL | 企业微信群消息推送完整 Webhook |
| WEWORK_MSG_TYPE | `markdown`（默认，可不填） |

AI 分析只有在 API Key 和模型名已配置时才启用；标题筛选仍使用默认关键词。
GLM-5.3 的输出额度设为 12000 token，超时 240 秒，避免推理占用额度后分析正文被截断。
消息推送按用户要求暂缓，`notification.enabled` 已关闭。后续启用时再配置企业微信 Webhook 并打开通知开关。

## 企业微信端配置

若“添加消息推送”只列出“企业内已发布的”项目，没有自定义创建入口，优先请企业管理员检查创建权限。
管理员登录企业微信后台，进入“应用管理 → 应用 → 消息推送”，将操作人加入“可创建消息推送的成员”并启用；随后重新打开群内配置窗口。
也可以请管理员直接为目标群新建一个专用的 TrendRadar 推送，并提供其 Webhook。

电脑端企业微信：打开接收报告的企业内部群，右键群聊 → 管理聊天信息 → 消息推送 → 自定义消息推送。
填写名称、简介与头像，复制 Webhook，保存机器人。旧版本通常是群设置 → 添加群机器人 → 新创建一个机器人。
将完整 Webhook 保存为仓库 Secret `WEWORK_WEBHOOK_URL`。
只有机器人创建者能查看 Webhook；若看不到添加入口，请联系企业管理员确认权限。

腾讯官方教程：https://intl.cloud.tencent.com/zh/document/product/1254/78645?lang=zh
管理员配置参考：https://www.h3c.com/cn/d_202606/2852119_30005_0.htm

## 签到续期

保留上游每 7 天手动续期的运行机制，超期会暂停抓取。
进入 Actions → Check In → Run workflow 即可续期并重新启用抓取。
本部署将签到改为更新时间戳，不再使用上游删除全部工作流运行记录的做法，便于保留试运行证据。

## 验证与排查

Get Hot News 包含 crawl 和 deploy 两个任务。crawl 必须生成当天有效 SQLite、非空抓取记录与新 HTML 才能发布。
任务摘要记录抓取数量、平台成功/失败数和报告大小。部分数据源失败会给出警告。
AI 或推送结果还需查看 Run crawler 日志和企业微信群实收消息；网页部署成功不代表外部服务成功。
如需修改关注主题，编辑 `config/frequency_words.txt`；更换新闻源、RSS 或报告模式则编辑 `config/config.yaml`。

## 2026-10-23 试运行记录

北京时间 15:29 和 15:35 在本机使用相同程序及 Secrets 对应的 AI 配置完成两轮集成运行，最终报告生成时间为 15:37。
第二轮 11 个热榜平台全部成功，当前榜单 255 条、关键词命中 48 条；官方 Hacker News RSS 抓取 30 条，过滤旧文后 25 条、关键词命中 4 条。
两轮 SQLite 累计保存 264 条不同新闻，第二轮新增 9 条并更新 246 条，重复抓取与历史恢复已验证。
完整 AI 分析已渲染到报告，第二轮未触发 JSON 自动修复；消息推送已关闭。
以上数据库和报告已提交到 data 分支（初始试运行提交 9339236）。

当时 GitHub Actions 手动触发后持续处于 queued，jobs 列表为空，取消接口返回“尚未进入队列”；抓取任务和 GitHub 官方 Pages 构建任务均未开始。
因此云端定时执行、Runner 端 Secret 注入和 Pages 在线访问尚未验收通过，不能据本地结果认定云端部署成功。
已将 Pages 最终发布方式设为 GitHub Actions，master 分支允许部署；gh-pages 分支仅保留用于尝试首次发布的静态报告快照，不是自动更新的数据源。
后续请以 Actions 的 crawl/deploy 成功结果和在线报告实际内容为准。
