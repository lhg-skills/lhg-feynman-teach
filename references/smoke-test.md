# lhg-feynman-teach 标准冒烟用例

自检命中疑似缺陷、或用户要求验证时运行。以下用例全部通过才算冒烟通过。

## 用例 F-1：费曼门禁全流程（讲稿档）

输入：“用 1 分钟给 12 岁孩子讲清楚：为什么天空是蓝色的”。参考产物见 `references/fixtures/sky-blue-1min/`（A 档，2026-10-15 实测通过）。

1. **观众使命**：`MISSION.md` 写清观众是谁、观众起点、看完能讲出哪一句话。
2. **可信资源**：`RESOURCES.md` 至少 2 个可信来源（百科 / 教材 / 科普机构），讲稿里“散射”“波长”等事实断言都能对上来源。
3. **费曼循环**：`FEYNMAN.md` 无未解释术语；`GAP-LOG.md` 至少记录 1 个卡点（如“为什么不是紫色”）及补漏来源；模拟观众追问至少 2 问且讲稿已回应。
4. **时长**：讲稿字数在 1 分钟档区间（约 200-240 字），时长选择说明有一句话理由。
5. **门禁**：`GATE.md` 全部打勾。
6. **自检脚本**：`python3 scripts/check_delivery.py <工作区> --target 60 --level A` 输出 `passed`。
7. **效率**：只在开工确认、讲稿确认两处停下来问用户；费曼循环不超过 3 轮。

## 用例 F-2：样片回归（幻灯片 / 手绘成片档）

在仓库根目录运行 `bash examples/ai-learn-30s/run.sh`（字体环境变量见 `examples/ai-learn-30s/README.md`）：

1. 脚本退出码为 0，生成成片（时长约 30 秒）。
2. 接着运行 `bash examples/ai-learn-30s/check.sh`，`check_delivery.py --video-only` 输出 `passed`（讲稿=旁白、字幕=旁白、字幕不重叠、时长、音画、非黑屏）。

## 用例 F-3：上游 vendor 健康

1. `vendor/sweety-handdraw-video.pin`、`vendor/teach.pin` 存在且是 40 位 commit。
2. `SKILL.md` 与 `references/*.md` 中引用的 teach 格式文件（MISSION / RESOURCES / LEARNING-RECORD / GLOSSARY 四个）在 `vendor/teach/` 下全部存在。
3. 在 `vendor/sweety-handdraw-video/skills/sweety-handdraw-video/scripts/` 下：`python3 -m unittest discover -s . -p 'test*.py'` 全部 OK；`python3 smoke_test.py --output <新建空目录>` 输出含 `offline_runtime_checks_passed`。
4. `validate_package.py` 需要上游全部依赖，只在上游完整副本上跑（CI 同步时自动跑）；精简后的 vendor 不跑这一项。

## 用例 F-4：降档诚实

在没有 `ffmpeg` 的环境里输入任意主题：

1. 第 0 步自检报出缺 `ffmpeg`，先尝试安装；装不上则明确告知“本次交付到 A 档”。
2. 交付待剪辑包（讲稿 + 分镜 + 带停顿标记的旁白 + `video/TODO-待剪辑.md`），**不出现“视频已生成”字样**。
3. `check_delivery.py --level A` 输出 `passed`；若误按 B 档检查，脚本报“缺 ffprobe”并以 `failed` 退出。

## 通过标准

- F-1、F-3、F-4 必过；F-2 在具备 B 档能力的环境必过，无能力时记“未运行 + 原因”。缺任一项即冒烟失败。
