# lhg-feynman-teach · 费曼教学

> **一句话**：把一个知识点用费曼法讲通，再做成讲稿即旁白的教学视频（默认 3 分钟，幻灯片 / 手绘两种画面）。
>
> **开发者安装**（能访问 GitHub 时）：`npx skills add lhg-skills/lhg-feynman-teach`，或 `git clone` 后把整个目录放进对应平台的 skills 目录（**保留 `vendor/`**，手绘模式依赖它）。

[English](#english) | [中文](#中文)

---

## 发给 Agent 的安装话术（推荐）

复制下面整段话，发给你的 Agent（豆包 / WorkBuddy / Claude Code / Codex / Cursor 等）：

> 请帮我安装 Skill「lhg-feynman-teach」：先从 Gitee 上 lhg-skills 组织下的 lhg-feynman-teach 仓库下载；如果 Gitee 无法访问或下载失败，改从 GitHub 上 lhg-skills 组织下的同名仓库下载。按当前 Agent 的规范安装其中的 Skill，优先全局安装，保留完整目录和依赖。请直接执行，完成后验证是否安装成功，告诉我实际使用的来源、安装的版本号以及如何调用；遇到访问或安装限制请说明具体原因。

**怎么算装好了**：Agent 能在已安装的 Skill 里看到 `lhg-feynman-teach`，并报出版本号（与仓库 `manifest.yaml` 的 `version` 一致）；安装目录里有 `vendor/` 和 `references/`。只是打开了仓库网页不算安装。

## 如何调用

直接对 Agent 说：

- “用费曼法给 12 岁孩子讲清楚：为什么天空是蓝色的，做成 1 分钟视频。”
- “把『大模型为什么会胡说八道』讲通，出一条 3 分钟教学视频，用手绘画面。”
- “这是我的资料（附文件），帮我讲成小白能听懂的讲稿，先不用出视频。”

## 什么时候用 / 什么时候不用

**用它，当你**：
- 要把一个概念 / 工具 / 原理讲给外行听，并且要发成视频
- 想检验自己是不是真懂：讲不通，就说明没学会

**别用它，当你**：
- 只要一段好看的宣传片或纯剪辑（没有“讲通”的需求）
- 内容超过 5 分钟又不想拆集

## 常见失败与原因

| 现象 | 原因 | 应对 |
|---|---|---|
| 只给了讲稿和分镜，没有视频 | 宿主没有 `ffmpeg` / TTS（降到讲稿档） | 装 `ffmpeg` 与中文 TTS 后重跑第 6 步 |
| 手绘模式报错或退化成幻灯片 | 只复制了 `SKILL.md`，缺 `vendor/`；或缺 scipy / 手写字体 | 按话术“保留完整目录和依赖”重装；`pip install -r` 上游 requirements |
| 画面里的中文是方块 | 缺 CJK 字体 | 安装 Noto Sans CJK 等中文字体 |
| 自检报“有配音”失败 | 没有 TTS，渲染出的是静音片 | 接入中文 TTS 或自己录旁白，存成整篇音频后重跑；或按 A 档交付 |
| 装到旧版本 | Gitee 镜像未同步 | 让 Agent 报版本号，与 GitHub `manifest.yaml` 对比 |

## 卸载

删除 Agent skills 目录下的 `lhg-feynman-teach` 文件夹即可（或 `npx skills remove lhg-feynman-teach`）。教学工作区里已生成的讲稿和视频不受影响。

## 反馈

提 issue 时请附：Agent 名称、安装来源（Gitee / GitHub）、版本号、报错原文或截图、输入的主题。也可以让 Agent 按 SKILL.md 的“自检与反馈”生成质检报告后一键提交。

---

## English

**Feynman Teach** = Feynman Technique + stateful teaching + video output.

Input one thing you want to learn. It first forces the explanation through the Feynman 4-step loop (teach it in plain language to a 12-year-old → find gaps → go back to sources → simplify and re-teach) until it passes the Feynman Gate, then outputs the learning conclusion **and** a teaching video whose narration is exactly that Feynman script.

### Workflow

1. **Mission** — why learn it, what success looks like.
2. **Trusted resources** — no parametric trust; every factual claim needs a source.
3. **Split** — break into smallest teachable units (1 concept + 1 analogy + 1 example + 1 pitfall).
4. **Feynman loop** — plain-language script → gap log → back to sources → simplify → re-teach.
5. **Learning conclusion** — Feynman script + gap log + learning records + cheat sheet.
6. **Video** — script = narration; storyboard → visuals → voiceover → assembly → subtitles → QC. Two visual modes: slides (default, fast) / hand-drawn (optional, for processes and causal chains).
7. **Real-world check** — share the video, collect questions, feed back into gaps.

### Video length

| Length | Use for |
|---|---|
| 1 min | 1 single concept, 1 analogy, 1 example |
| 3 min (default) | 1 complete mini-lesson, 2-3 steps + 1 pitfall |
| 5 min | 1 system / chain with dependencies |
| >5 min | Split into multiple 3-min episodes |

### Base + attribution

Teaching-workspace structure and “no parametric trust” ideas come from Matt Pocock `teach` (https://github.com/mattpocock/skills/tree/main/skills/productivity/teach, MIT); its source is vendored unmodified under `vendor/teach/` and its format files are referenced directly. Hand-drawn mode references `threerocks/sweety-handdraw-video` (https://github.com/threerocks/sweety-handdraw-video, MIT, v1.2.3 at integration) for workflow ideas; its runtime part (minus two large reference packs, ~46 MB) is vendored unmodified under `vendor/sweety-handdraw-video/` (original MIT license kept) and synced weekly from upstream by GitHub Actions (auto-committed only after the smoke test passes). This skill adds original work: Feynman gate, gap log, script-as-narration, video pipeline, duration decision table, audience-oriented Feynman loop.

### License

MIT — see [LICENSE](LICENSE).

---

## 中文

**费曼教学**：费曼学习法 + 有状态教学 + 视频输出。

输入一个想学的东西，先用费曼四步讲通（用大白话讲给 12 岁 → 找卡点 → 回源补漏 → 简化重讲），通过费曼门禁后，再输出学习结论 + 教学视频。视频旁白就是那份费曼讲稿，不另写一套。

### 流程

1. **定使命** — 为什么学、学完能做什么。
2. **找可信资源** — 不信任参数记忆，每个事实断言要有来源。
3. **拆单元** — 拆到最小可讲单元（1 概念 + 1 类比 + 1 例子 + 1 易错点）。
4. **费曼循环** — 大白话讲稿 → 卡点日志 → 回源补漏 → 简化重讲。
5. **学习结论** — 讲稿 + 卡点日志 + 学习记录 + 速查表。
6. **视频** — 讲稿即旁白；分镜 → 画面 → 配音 → 组装 → 字幕 → 质检。两种视觉模式：幻灯片（默认，快）/ 手绘（可选，适合过程与因果链）。
7. **真实验证** — 把视频给目标观众看，问题回流为卡点。

### 视频时长

| 时长 | 适用 |
|---|---|
| 1 分钟 | 1 个单一概念、1 个类比、1 个例子 |
| 3 分钟（默认） | 1 个完整小课：2-3 步 + 1 易错点 |
| 5 分钟 | 1 个系统/链条，有依赖、需完整推导 |
| 超过 5 分钟 | 拆成多集 3 分钟 |

### 底座与归属

教学工作区结构与“不信任参数记忆”等理念源自 Matt Pocock `teach`（https://github.com/mattpocock/skills/tree/main/skills/productivity/teach，MIT），源码原样收录在 `vendor/teach/`，本 skill 直接引用其格式文件。手绘模式参考 `threerocks/sweety-handdraw-video`（https://github.com/threerocks/sweety-handdraw-video，MIT，吸纳时 v1.2.3），流程要点按费曼教学重新组织；其运行所需部分（不含两个约 46 MB 的参考资料包）原样收录在 `vendor/sweety-handdraw-video/`（保留原 MIT 许可证，不手改），由 GitHub Actions 每周自动同步上游，冒烟测试通过才更新。本 skill 在其上做了原创改动：费曼门禁、卡点日志、讲稿即旁白、视频管线、时长决策表、观众导向的费曼循环。

### License

MIT — 详见 [LICENSE](LICENSE)。

---

## 出品：刘洪光

本 skill 由真人出镜 IP「刘洪光」（安徽合肥）出品，归属 [lhg-skills](https://github.com/lhg-skills)。

- GitHub 主页：https://github.com/lhg-skills —— 全部 skill 开源在此，欢迎 star
- 视频号：搜「刘洪光实名上网」
- 微信：lhgsmsw
