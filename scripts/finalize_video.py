#!/usr/bin/env python3
"""lhg-feynman-teach 成片收尾：做封面 → 封面插到最前面（当首帧，平台默认就用它当封面）→ 出黑底 9:16 竖屏版。

一条命令完成，弱一些的 agent 也只需要填参数：
  python3 scripts/finalize_video.py <工作区> --title1 "钩子一句" --title2 "结论一句" [--footer "刘洪光实名上网 · 2026-10-16"]

输入（渲染步骤的产物，文件名固定）：
  video/body.mp4   不带封面的横屏 16:9 正片
  video/body.srt   正片字幕（可选）
输出：
  video/cover.png            横屏封面（正片画面 + 大标题）
  video/cover-vertical.png   竖屏封面（黑底，上标题 / 中画面 / 下日期出品人）
  video/video.mp4            横屏成片：封面在最前面，并内嵌为封面图
  video/video-vertical.mp4   竖屏成片：1080×1920 黑底，横屏画面居中（等同剪映把横屏放进 9:16 画布）
  video/subtitles.srt        字幕整体后移封面时长，与成片对齐
  video/finalize.json        记录封面时长等参数，供 check_delivery.py 使用
可重复运行：每次都从 body.* 重新生成，不会叠加封面。只依赖 ffmpeg / ffprobe / Pillow。
"""
import argparse, datetime, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration:stream=codec_type,width,height,r_frame_rate,sample_rate",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    return {"duration": float(d["format"]["duration"]), "w": v["width"], "h": v["height"],
            "fps": v["r_frame_rate"], "sr": int(a["sample_rate"]) if a else 48000, "audio": a is not None}

def has_glyphs(path, text):
    try:
        from fontTools.ttLib import TTFont
        cmap = TTFont(path, fontNumber=0, lazy=True).getBestCmap()
        return all(ord(ch) in cmap for ch in text if not ch.isspace())
    except Exception:
        return False

def find_font(arg, text):
    """找一个能显示全部标题字的中文粗体：--font > TITLE_FONT > fc-list 里的中文粗体。"""
    cands = [arg, os.environ.get("TITLE_FONT")]
    try:
        out = subprocess.run(["fc-list", ":lang=zh", "file", "style"], capture_output=True, text=True).stdout
        rank = lambda l: ("Serif" in l or "Mono" in l, 0 if re.search(r"Black|Heavy", l) else 1 if "Bold" in l else 2)
        cands += [l.split(":")[0] for l in sorted(out.splitlines(), key=rank)]
    except FileNotFoundError:
        pass
    for c in cands:
        if c and Path(c).is_file() and has_glyphs(c, text):
            return c
    sys.exit("找不到能显示标题的中文字体：用 --font 指定，或安装 Noto Sans CJK / 思源黑体")

def fit_font(font_path, text, max_w, size):
    while size > 20:
        f = ImageFont.truetype(font_path, size)
        if f.getlength(text) <= max_w:
            return f
        size -= 4
    return ImageFont.truetype(font_path, size)

def draw_lines(img, font_path, lines, colors, center_y, max_w, size, stroke):
    d = ImageDraw.Draw(img)
    fonts = [fit_font(font_path, t, max_w, size) for t in lines]
    heights = [f.getbbox(t)[3] - f.getbbox(t)[1] for f, t in zip(fonts, lines)]
    gap = int(size * 0.35)
    y = center_y - (sum(heights) + gap * (len(lines) - 1)) // 2
    for t, f, h, col in zip(lines, fonts, heights, colors):
        top = f.getbbox(t)[1]
        x = (img.width - f.getlength(t)) / 2
        d.text((x, y - top), t, font=f, fill=col, stroke_width=stroke, stroke_fill="black")
        y += h + gap

def srt_shift(src, dst, offset):
    def shift(m):
        h, mi, s, ms = map(int, m.groups())
        t = max(0, h * 3600000 + mi * 60000 + s * 1000 + ms + int(round(offset * 1000)))
        return f"{t // 3600000:02d}:{t // 60000 % 60:02d}:{t // 1000 % 60:02d},{t % 1000:03d}"
    dst.write_text(re.sub(r"(\d+):(\d+):(\d+),(\d+)", shift, src.read_text(encoding="utf-8")), encoding="utf-8")

def prepend_cover(body, cover_png, seconds, info, out, vf_body, size):
    W, H = size
    fc = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black,"
          f"fps={info['fps']},format=yuv420p,setsar=1[cv];"
          f"[1:v]{vf_body},fps={info['fps']},format=yuv420p,setsar=1[bv];")
    if info["audio"]:
        fc += (f"[2:a]aformat=sample_rates={info['sr']}:channel_layouts=stereo[ca];"
               f"[1:a]aformat=sample_rates={info['sr']}:channel_layouts=stereo[ba];"
               "[cv][ca][bv][ba]concat=n=2:v=1:a=1[v][a]")
        maps = ["-map", "[v]", "-map", "[a]", "-c:a", "aac", "-b:a", "192k"]
    else:
        fc += "[cv][bv]concat=n=2:v=1:a=0[v]"
        maps = ["-map", "[v]"]
    run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", f"{seconds}", "-i", str(cover_png), "-i", str(body),
         "-f", "lavfi", "-t", f"{seconds}", "-i", f"anullsrc=r={info['sr']}:cl=stereo",
         "-filter_complex", fc, *maps, "-c:v", "libx264", "-crf", "18", "-preset", "medium",
         "-movflags", "+faststart", str(out)])

def embed_cover(video, cover_png, out):
    jpg = cover_png.with_suffix(".jpg")
    Image.open(cover_png).convert("RGB").save(jpg, quality=92)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-i", str(jpg), "-map", "0", "-map", "1", "-c", "copy",
         "-disposition:v:1", "attached_pic", "-movflags", "+faststart", str(out)])
    jpg.unlink()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace", type=Path)
    ap.add_argument("--title1", required=True, help="封面第 1 行：钩子（≤12 字最好）")
    ap.add_argument("--title2", required=True, help="封面第 2 行：一句话结论（≤12 字最好）")
    ap.add_argument("--footer", default=None, help="竖屏封面底部一行，默认“刘洪光实名上网 · 今天日期”")
    ap.add_argument("--cover-time", type=float, default=None, help="封面取正片第几秒的画面，默认结尾前 1 秒（手绘画面最完整）")
    ap.add_argument("--cover-image", type=Path, default=None, help="直接用这张图当封面底图，不从正片取帧")
    ap.add_argument("--cover-seconds", type=float, default=0.5, help="封面在片头停留秒数，默认 0.5")
    ap.add_argument("--font", default=None)
    a = ap.parse_args()
    v = a.workspace / "video"
    body = v / "body.mp4"
    if not body.is_file():
        sys.exit(f"缺 {body}：先把不带封面的正片存为 video/body.mp4")
    info = probe(body)
    footer = a.footer or f"刘洪光实名上网 · {datetime.date.today():%Y-%m-%d}"
    font = find_font(a.font, a.title1 + a.title2 + footer)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        frame = tmp / "frame.png"
        if a.cover_image:
            Image.open(a.cover_image).convert("RGB").resize((info["w"], info["h"])).save(frame)
        else:
            t = a.cover_time if a.cover_time is not None else max(0.0, info["duration"] - 1.0)
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(body), "-frames:v", "1", str(frame)])
        base = Image.open(frame).convert("RGB")
        # 横屏封面：画面 + 两行大标题（白字 / 黄字，黑描边）
        cover = Image.blend(base, Image.new("RGB", base.size, "black"), 0.45)  # 压暗底图，标题更醒目
        W, H = cover.size
        draw_lines(cover, font, [a.title1, a.title2], ["white", "#FFD400"], H // 2, int(W * 0.88), int(H * 0.15), max(4, H // 110))
        cover.save(v / "cover.png")
        # 竖屏封面：黑底；上方两行标题，中间原画面，下方日期出品人
        VW, VH = 1080, 1920
        vc = Image.new("RGB", (VW, VH), "black")
        fh = round(VW * H / W)
        vc.paste(base.resize((VW, fh)), (0, (VH - fh) // 2))
        draw_lines(vc, font, [a.title1, a.title2], ["white", "#FFD400"], (VH - fh) // 4, int(VW * 0.9), 96, 3)
        draw_lines(vc, font, [footer], ["#BBBBBB"], VH - (VH - fh) // 4, int(VW * 0.9), 40, 0)
        vc.save(v / "cover-vertical.png")
        # 横屏成片：封面在最前面 + 内嵌封面图
        h_tmp = tmp / "h.mp4"
        prepend_cover(body, v / "cover.png", a.cover_seconds, info, h_tmp, f"scale={W}:{H}", (W, H))
        embed_cover(h_tmp, v / "cover.png", v / "video.mp4")
        # 竖屏成片：1080×1920 黑底，横屏画面按宽度缩放后居中
        v_tmp = tmp / "v.mp4"
        prepend_cover(body, v / "cover-vertical.png", a.cover_seconds, info, v_tmp,
                      f"scale={VW}:-2,pad={VW}:{VH}:(ow-iw)/2:(oh-ih)/2:black", (VW, VH))
        embed_cover(v_tmp, v / "cover-vertical.png", v / "video-vertical.mp4")
    if (v / "body.srt").is_file():
        srt_shift(v / "body.srt", v / "subtitles.srt", a.cover_seconds)
    meta = {"font": font, "cover_seconds": a.cover_seconds, "body_duration": round(info["duration"], 3),
            "title1": a.title1, "title2": a.title2, "footer": footer}
    (v / "finalize.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "done", **meta, "outputs": ["video/video.mp4", "video/video-vertical.mp4",
                      "video/cover.png", "video/cover-vertical.png"]}, ensure_ascii=False))

if __name__ == "__main__":
    main()
