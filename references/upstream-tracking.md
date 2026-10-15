# 上游跟踪 Upstream Tracking

## 本 skill 依赖的上游

### 1. mattpocock/teach（教学底座）
- 仓库：https://github.com/mattpocock/skills/tree/main/skills/productivity/teach
- 许可：MIT
- 吸纳点：教学工作区结构、不信任参数记忆、检索与间隔
- 跟踪方式：本 skill 发布时人工核对一次；日常不自动跟

### 2. threerocks/sweety-handdraw-video（手绘模式参考）
- 仓库：https://github.com/threerocks/sweety-handdraw-video
- 许可：MIT（Copyright (c) 2026 threerocks）
- 作者 X：@leo_xiaolei（水族店刘老板），帖子：https://x.com/leo_xiaolei/status/2110404124970045858
- 本 skill 吸纳时核验的版本：`1.2.3`，commit `5206ec0d17f9b353e400b64b9c51ad69e721e02a`，核验时间 2026-10-15
- 核验时快照：387→411 stars（页面与 API 在同一天内有波动，以 API 为准）、约 82→89 forks、公开仓、MIT
- 吸纳方式：只吸收流程要点，不复制代码与素材，不 vendor 其脚本与模型文件
- 吸纳点：声音先行、绘制计划、分部位描线、先轮廓后填色、字幕唯一性、代表段检查

## 跟踪规则

- 每周检查一次上游 `sweety-handdraw-video`：看 `VERSION`、最新 commit、README 变更，重点看三类变化：(1) 管线步骤变了 (2) 质量门槛变了 (3) 新增依赖或运行要求变了。
- 只有当上游变化影响本 skill 的 `references/handdraw-mode.md` 或 `references/video-spec.md` 时，才改本 skill；只改版本号、文案润色、与本 skill 无关的新功能，不跟。
- 跟踪记录格式：`日期 / 上游 VERSION / 上游 commit 前 8 位 / 是否影响本 skill / 处理结果`，记在下方“跟踪日志”里。
- 不要把上游作者的私人信息、未公开内容写进本 skill；只记公开仓库的公开变化。

## 跟踪日志

- 2026-10-15 / 1.2.3 / 5206ec0d / 首次吸纳 / 新建 `references/handdraw-mode.md`，SKILL.md 升级到 1.1.0，手绘模式作为可选视觉模式
- 2026-10-15 / 1.2.3 / 5206ec0d / 完整包已下载 / 全量克隆到 ~/workspace/skills/threerocks-sweety-handdraw-video/（1307 文件，约 81M，含 scripts 37 个文件 + dependencies + assets + docs + tools），SOURCE.md 已写；冒烟：smoke_test.py 离线回归通过（offline_runtime_checks_passed，合成夹具 13.43 秒 960x540 film.mp4，visual_acceptance_claimed=false，仅为运行时回归，非成品验收）
