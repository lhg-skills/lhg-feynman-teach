# 样片：AI 答对了，就算学会了吗？（30 秒）

- 作用：示例 + 回归测试。每周同步上游后由 `.github/workflows/sync-vendor.yml` 跑 `run.sh`，**你的样片跑不通就不合并上游更新**。
- 话题：2026-10-11 清华求真书院「AI 与数学」圆桌论坛的学生 A / 学生 B 之问。
- 旁白：edge-tts `zh-CN-YunxiNeural` 整篇一次合成；`boundaries.json` 是合成时拿到的逐词时间，`align.py` 据此生成 `alignment.json` 与字幕断句。
- 素材：`assets/*.b64` 是 4 张 AI 插画（webp）和旁白母带（opus）的 base64 文本。用文本存放是因为本仓库通过 GitHub API 提交，只支持文本文件；`run.sh` 会还原。
- 本地运行：

```bash
HW_FONT=~/workspace/fonts/MaShanZheng-Regular.ttf \
SC_FONT=/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc SC_INDEX=2 \
bash examples/ai-learn-30s/run.sh
```

- 说明：runtime_fixture 模式，仅作工程回归，不是生产 finalize 成片。
