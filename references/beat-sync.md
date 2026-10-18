# 音画卡点（手绘模式迭代规划，未实现）

> 一句话：手绘线的节拍来自**旁白**，不是配乐。先把每个 beat 的旁白逐字对齐成时间表，
> 描线、出字、字幕、翻页都从时间表里取时间——说到「门」才开始画门。

状态：**规划中**。本文件是设计说明，尚未改动 SKILL.md 与 `vendor/`（vendor 保持原样不手改）。

## 来源与取舍

- [Vincentwei1021/mg-styles-15](https://github.com/Vincentwei1021/mg-styles-15)（MIT）：吸收「画面按时间表出帧」（`cues.json` + `renderAt(t)`）的思路。
- [gnipbao/jev-remix-cutter](https://github.com/gnipbao/jev-remix-cutter)（MIT）：仅参考 librosa 节拍网格与 -14 LUFS 响度；不用其 Jev 打分与自动选角。

## 要解决的现状问题

- 字幕时间按字数比例估算，存在轻微漂移（目前写在交付 README 的诚实说明里）。
- text action / 插画描线的开始时间与旁白说到该词的时刻没有绑定。
- 生产 finalize 需要 `alignment.json`，目前缺。

## 迭代步骤

1. 每个 beat 的 `inputs/beat-*.wav` 跑逐字强制对齐（Whisper word timestamps 或同类）→ `alignment.json`。
2. 由对齐结果生成 `caption_cues`（按标点断句、单行），取代按字数比例估算。
3. job.json 里 text action / 插画描线的开始时间，绑定到对应关键词的说出时刻。
4. 可选：低音量 BGM，librosa 取强拍，翻页对齐强拍；旁白段 ducking，成片 -14 LUFS ±1。
5. 合并 1–4 的时间点输出 `cues.json`，与成片一起归档。

## cues.json 草案（与 lhg-stickman-director/BEAT-SYNC.md 共用格式）

```json
{
  "fps": 30,
  "cues": [
    {"t": 0.00, "frame": 0,  "kind": "section", "intent": "page-1", "source": "script"},
    {"t": 1.37, "frame": 41, "kind": "word",    "text": "门",      "source": "alignment"}
  ]
}
```

规则：关键词落点优先于 BGM 节拍；两者相距 ≤ 3 帧时吸附到关键词。

## 验收（先在 sample-30s-v4 上做 v5）

- [ ] 关键动作开始时刻与对应词误差 ≤ 1 帧
- [ ] 字幕时间来自对齐结果；交付 README 去掉「字幕可能轻微漂移」一条
- [ ] `handdraw_video.py doctor → build → render → verify` 全部通过，终帧文字全部画完
- [ ] 若加 BGM：成片 -14 LUFS ±1，旁白清晰不被盖住
