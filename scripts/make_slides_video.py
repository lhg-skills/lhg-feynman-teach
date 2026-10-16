#!/usr/bin/env python3
"""lhg-feynman-teach 幻灯片模式渲染：把 slides.json 变成 video/body.mp4 + video/body.srt。

给能力一般的 agent 用：不需要自己拼 ffmpeg 命令，只要写好 slides.json、准备好旁白音频。
  python3 scripts/make_slides_video.py <工作区>

video/slides.json 格式（每句旁白一张幻灯片，字幕 = 旁白原句，自动烧录且同一时刻只有一句）：
{
  "audio": "video/narration.wav",          // 整篇旁白音频（一次合成）；没有就省略，输出静音片并标注
  "background": "#F7F1E6",                  // 可选，默认米白
  "slides": [
    {"say": "孩子问你：天为什么是蓝的？你可以这样讲。", "big": "天为什么是蓝的？"},
    {"say": "太阳光看着是白的，其实里面藏着彩虹的所有颜色。", "big": "白光 = 七种颜色", "image": "video/img/prism.png"},
    ...
  ]
}
- say：这一张对应的旁白原句（必须与 FEYNMAN.md 逐字一致，按顺序拼起来就是全文）。
- big：画面大字（≤12 字，可省略）；image：配图（可省略，有图时图在左、字在右）。
- seconds：可选；不写时按 say 的字数比例分配音频总时长（无音频时按 220 字/分钟）。
随后运行 finalize_video.py 加封面、出竖屏，再运行 check_delivery.py。
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).parent))
from finalize_video import find_font  # 同一套中文字体探测

W, H = 1920, 1080
CPS = 220 / 60

def wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for ch in text:
        if draw.textlength(cur + ch, font=font) > max_w and cur and ch not in "，。、；：？！”’）》…—,.;:?!)":  # 标点不放行首
            lines.append(cur); cur = ch
        else:
            cur += ch
    return lines + ([cur] if cur else [])

def render(slide, path, font_path, bg, root):
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    text_box = (120, 120, W - 120, H - 230)
    if slide.get("image"):
        pic = Image.open(root / slide["image"]).convert("RGB")
        pic.thumbnail((W // 2 - 160, H - 380))
        img.paste(pic, (120 + (W // 2 - 160 - pic.width) // 2, 150 + (H - 380 - pic.height) // 2))
        text_box = (W // 2 + 40, 120, W - 120, H - 230)
    if slide.get("big"):
        size = 120
        while size > 48:
            f = ImageFont.truetype(font_path, size)
            lines = wrap(d, slide["big"], f, text_box[2] - text_box[0])
            if len(lines) * size * 1.3 <= text_box[3] - text_box[1]:
                break
            size -= 8
        y = (text_box[1] + text_box[3]) / 2 - len(lines) * size * 1.3 / 2
        for line in lines:
            x = (text_box[0] + text_box[2]) / 2 - d.textlength(line, font=f) / 2
            d.text((x, y), line, font=f, fill="#222222")
            y += size * 1.3
    # 烧录字幕：底部一条，半透明深色底
    f = ImageFont.truetype(font_path, 44)
    lines = wrap(d, slide["say"], f, W - 300)[:2]
    box_h = 70 * len(lines) + 30
    overlay = Image.new("RGBA", (W, box_h), (0, 0, 0, 150))
    img.paste(overlay, (0, H - box_h - 40), overlay)
    y = H - box_h - 40 + 22
    for line in lines:
        d.text(((W - d.textlength(line, font=f)) / 2, y), line, font=f, fill="white")
        y += 70
    img.save(path)

def ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = Path(sys.argv[1])
    spec = json.loads((root / "video/slides.json").read_text(encoding="utf-8"))
    slides = spec["slides"]
    audio = root / spec["audio"] if spec.get("audio") else None
    if audio and not audio.is_file():
        sys.exit(f"缺旁白音频 {audio}")
    total = None
    if audio:
        total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(audio)],
                                     capture_output=True, text=True, check=True).stdout)
    import re
    chars = [max(1, len(re.sub(r"[\s，。、；：？！“”‘’（）《》…—·,.;:?!\"'()]", "", s["say"]))) for s in slides]  # 只数字，不数标点
    fixed = sum(s.get("seconds", 0) for s in slides)
    free = sum(c for s, c in zip(slides, chars) if "seconds" not in s)
    pool = (total - fixed) if total else free / CPS
    durs = [s.get("seconds") or pool * c / free for s, c in zip(slides, chars)]
    font = find_font(os.environ.get("TITLE_FONT"), "".join(s["say"] + s.get("big", "") for s in slides))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        lst = []
        for i, s in enumerate(slides):
            p = tmp / f"s{i:03d}.png"
            render(s, p, font, spec.get("background", "#F7F1E6"), root)
            lst += [f"file '{p}'", f"duration {durs[i]:.3f}"]
        lst.append(f"file '{tmp / f's{len(slides) - 1:03d}.png'}'")
        (tmp / "list.txt").write_text("\n".join(lst))
        a_in = ["-i", str(audio)] if audio else ["-f", "lavfi", "-t", f"{sum(durs):.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"), *a_in,
                        "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
                        "-ar", "48000", "-ac", "2", "-shortest", "-movflags", "+faststart", str(root / "video/body.mp4")], check=True)
    t, out = 0.0, []
    for i, (s, d) in enumerate(zip(slides, durs), 1):
        out.append(f"{i}\n{ts(t)} --> {ts(t + d)}\n{s['say']}\n")
        t += d
    (root / "video/body.srt").write_text("\n".join(out), encoding="utf-8")
    print(json.dumps({"status": "done", "slides": len(slides), "seconds": round(t, 2),
                      "voiceover": bool(audio), "note": "" if audio else "无旁白音频：输出的是静音片，只能算 A 档待配音包"},
                     ensure_ascii=False))

if __name__ == "__main__":
    main()
