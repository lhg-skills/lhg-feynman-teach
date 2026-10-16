#!/usr/bin/env bash
# 用 scripts/check_delivery.py 检查 run.sh 渲染出的样片（讲稿=旁白、字幕=旁白、字幕不重叠、时长、音画、黑屏）。
# 先跑 run.sh；样片只演示视频管线，没有 MISSION 等教学文件，这里用 --video-only 跳过文件门禁。
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
W="${WORK:-/tmp/ai-learn-30s}"
WS="$W/workspace"
rm -rf "$WS"; mkdir -p "$WS/video"
NARR="$(python3 -c "import sys; sys.path.insert(0, '$HERE'); from script import BEATS; print(''.join(t for _, t in BEATS))")"
printf '# 样片讲稿\n\n<!-- narration:start -->\n%s\n<!-- narration:end -->\n' "$NARR" > "$WS/FEYNMAN.md"
cp "$WS/FEYNMAN.md" "$WS/video/script.md"
cp "$W/outputs/editing/transcript.srt" "$WS/video/subtitles.srt"
cp "$W/outputs/film.mp4" "$WS/video/video.mp4"
python3 "$ROOT/scripts/check_delivery.py" "$WS" --target 30 --video-only
