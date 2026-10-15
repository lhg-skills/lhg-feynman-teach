# vendor/

两个上游的完整源码快照，原样收录，**不要在这里手改**（下次同步会被覆盖）。

| 目录 | 上游 | 许可 | 当前版本 |
| --- | --- | --- | --- |
| `sweety-handdraw-video/` | https://github.com/threerocks/sweety-handdraw-video （整仓） | MIT，Copyright (c) 2026 threerocks，见目录内 `LICENSE` 与 `THIRD_PARTY_NOTICES.md` | `sweety-handdraw-video.pin` |
| `teach/` | https://github.com/mattpocock/skills/tree/main/skills/productivity/teach | MIT，Copyright (c) 2026 Matt Pocock，见目录内 `LICENSE`（复制自上游仓库根） | `teach.pin` |

- 自动同步：`.github/workflows/sync-vendor.yml`，每周一 09:00（北京时间）拉取两个上游最新版本。检查全部通过才直接提交到 main：sweety 自检 + 单元测试 + `smoke_test.py`、teach 结构检查（本 skill 引用的格式文件必须存在）、样片 `examples/ai-learn-30s` 完整渲染回归。任一失败则不提交并开 issue。
- 锁定或回退：手动改对应 `.pin` 文件为某个 commit 并推到 main，会同步到该版本。也可在 Actions 页面手动运行并指定版本。
- `UPSTREAM.md`：每次同步自动生成，记录版本、时间和上游变更列表。

手绘引擎入口：`vendor/sweety-handdraw-video/skills/sweety-handdraw-video/scripts/handdraw_video.py`
