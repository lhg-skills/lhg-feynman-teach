# vendor/

`sweety-handdraw-video/` 是上游 [threerocks/sweety-handdraw-video](https://github.com/threerocks/sweety-handdraw-video) 的完整源码快照（MIT，Copyright (c) 2026 threerocks），原样收录，保留上游 `LICENSE` 与 `THIRD_PARTY_NOTICES.md`。**不要在这里手改代码**，下次同步会被覆盖；需要改动请提到上游或在本 skill 外层处理。

- `sweety-handdraw-video.pin`：当前收录的上游 commit。手动改成某个 commit 并推到 main，会触发同步到该版本（用于锁定或回退）。
- `UPSTREAM.md`：每次同步自动生成，记录版本、时间和上游变更列表。
- 自动同步：`.github/workflows/sync-sweety.yml`，每周一 09:00（北京时间）拉取上游最新；validate + 单元测试 + `smoke_test.py` 全部通过才提交到 main，失败则不提交并开 issue。也可在 Actions 页面手动运行。

引擎入口：`vendor/sweety-handdraw-video/skills/sweety-handdraw-video/scripts/handdraw_video.py`
