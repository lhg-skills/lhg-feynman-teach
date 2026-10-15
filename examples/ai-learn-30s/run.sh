#!/usr/bin/env bash
# 回归测试：用收录的样片素材完整跑一遍 align -> job -> doctor/build/render/verify。
# 需要环境变量 HW_FONT（马善政体 ttf）、SC_FONT（简体中文字幕字体）、SC_INDEX（ttc 内序号，NotoSansCJK 用 2）。
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
ENGINE="${ENGINE:-$ROOT/vendor/sweety-handdraw-video/skills/sweety-handdraw-video/scripts/handdraw_video.py}"
W="${WORK:-/tmp/ai-learn-30s}"
rm -rf "$W"; mkdir -p "$W/inputs/narration" "$W/work" "$W/outputs"
for f in "$HERE"/assets/*.b64; do base64 -d "$f" > "$W/work/$(basename "${f%.b64}")"; done
cd "$W"
for n in desk student-a student-b teach-kid; do python3 -c "from PIL import Image;Image.open('work/$n.webp').convert('RGB').save('inputs/$n.png')"; done
ffmpeg -v error -y -i work/master.opus -ar 48000 -ac 1 inputs/narration/master.wav
cp "$HERE"/script.py "$HERE"/align.py "$HERE"/make_job.py .
cp "$HERE"/boundaries.json work/boundaries.json
python3 align.py > /dev/null
python3 make_job.py
python3 "$ENGINE" doctor . | tee work/doctor.json | grep -q '"ready": true'
python3 "$ENGINE" build .
python3 "$ENGINE" render . > work/render.log
python3 "$ENGINE" verify . > work/verify.log
grep -q '"status": "engineering_passed' work/verify.log
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 outputs/film.mp4)
python3 -c "import sys; d=float('$D'); sys.exit(0 if 28.5<d<32 else 1)"
echo "example ai-learn-30s OK: ${D}s -> $W/outputs/film.mp4"
