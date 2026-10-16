#!/usr/bin/env python3
"""lhg-feynman-teach 交付自检：把 SKILL.md「完成判定」能机器检查的部分一次跑完。

用法：
  python3 scripts/check_delivery.py <教学工作区> --target 60          # B/C 档：有成片
  python3 scripts/check_delivery.py <教学工作区> --target 60 --level A # A 档：只交付待剪辑包
  python3 scripts/check_delivery.py <工作区> --target 30 --video-only    # 只查视频管线（样片回归）
--target 为目标时长（秒，1/3/5 分钟档分别填 60/180/300；样片等非标准时长按实际填）。
输出 JSON；全部通过退出码 0，否则 1。只用标准库 + ffmpeg/ffprobe。
"""
import argparse, json, re, shutil, subprocess, sys
from pathlib import Path

PUNCT = re.compile(r"[\s\u3000-\u303f\uff00-\uffef，。、；：？！“”‘’（）《》…—·,.;:?!\"'()\[\]<>-]+")
CHARS_PER_SEC = 220 / 60  # 中文旁白约 220 字/分钟

def narration(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = re.search(r"<!--\s*narration:start\s*-->(.*?)<!--\s*narration:end\s*-->", text, re.S)
    return (m.group(1) if m else text).strip()

def norm(s: str) -> str:
    return PUNCT.sub("", s)

def srt_cues(path: Path):
    cues = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip()):
        lines = [l for l in block.splitlines() if l.strip()]
        t = next((l for l in lines if "-->" in l), None)
        if not t:
            continue
        a, b = [x.strip() for x in t.split("-->")]
        sec = lambda x: (lambda h, m, s: int(h) * 3600 + int(m) * 60 + float(s.replace(",", ".")))(*x.split(":"))
        cues.append((sec(a), sec(b), "".join(lines[lines.index(t) + 1:])))
    return cues

def probe(video: Path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type",
                          "-of", "json", str(video)], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    return float(d["format"]["duration"]), {s["codec_type"] for s in d.get("streams", [])}

def frame_luma(video: Path, t: float) -> float:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1",
                          "-vf", "scale=64:-1,format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    return sum(raw) / max(len(raw), 1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace", type=Path)
    ap.add_argument("--target", type=float, required=True, help="目标时长（秒）")
    ap.add_argument("--level", choices=["A", "B", "C"], default="B")
    ap.add_argument("--tolerance", type=float, default=0.10)
    ap.add_argument("--video-only", action="store_true", help="只查视频管线（样片回归用），跳过教学文件")
    a = ap.parse_args()
    w, checks = a.workspace, {}

    def check(name, ok, detail=""):
        checks[name] = {"ok": bool(ok), "detail": detail}

    need = ["FEYNMAN.md", "video/script.md"] if a.video_only else \
        ["MISSION.md", "RESOURCES.md", "FEYNMAN.md", "GAP-LOG.md", "GATE.md", "video/script.md", "video/storyboard.md"]
    need += ["video/TODO-待剪辑.md"] if a.level == "A" else ["video/video.mp4", "video/subtitles.srt"]
    missing = [p for p in need if not (w / p).is_file() or (w / p).stat().st_size == 0]
    check("文件齐全", not missing, "缺：" + "、".join(missing) if missing else f"{len(need)} 个文件")

    gate = w / "GATE.md"
    if gate.is_file():
        unchecked = [l.strip() for l in gate.read_text(encoding="utf-8").splitlines() if l.strip().startswith("- [ ]")]
        check("门禁全勾", not unchecked, "未勾：" + "；".join(unchecked[:3]) if unchecked else "全部打勾")

    res = w / "RESOURCES.md"
    if res.is_file():
        n = len(re.findall(r"https?://", res.read_text(encoding="utf-8")))
        check("有来源", n >= 1, f"{n} 个链接")

    fe, sc = w / "FEYNMAN.md", w / "video/script.md"
    if fe.is_file() and sc.is_file():
        nf, ns = norm(narration(fe)), norm(narration(sc))
        diff = next((i for i, (x, y) in enumerate(zip(nf, ns)) if x != y), min(len(nf), len(ns)))
        check("讲稿=旁白", nf == ns, "逐字一致" if nf == ns else f"第 {diff + 1} 字起不同：FEYNMAN「{nf[diff:diff + 8]}」 vs script「{ns[diff:diff + 8]}」")
        lo, hi = a.target * CHARS_PER_SEC * 0.8, a.target * CHARS_PER_SEC * 1.1
        check("字数匹配时长", lo <= len(nf) <= hi, f"{len(nf)} 字，{a.target:.0f} 秒档建议 {lo:.0f}-{hi:.0f} 字")

    srt = w / "video/subtitles.srt"
    if a.level != "A" and srt.is_file() and fe.is_file():
        cues = srt_cues(srt)
        ns = norm("".join(c[2] for c in cues))
        check("字幕=旁白", ns == norm(narration(fe)), f"{len(cues)} 条字幕")
        overlaps = [i for i in range(1, len(cues)) if cues[i][0] < cues[i - 1][1] - 0.01]
        check("字幕不重叠", not overlaps, f"重叠条目：{overlaps[:5]}" if overlaps else "同一时刻只有一份")

    video = w / "video/video.mp4"
    if a.level != "A" and video.is_file():
        if not shutil.which("ffprobe"):
            check("成片可检查", False, "缺 ffprobe")
        else:
            dur, kinds = probe(video)
            ok = abs(dur - a.target) <= a.target * a.tolerance
            check("时长", ok, f"{dur:.2f} 秒，目标 {a.target:.0f}±{a.target * a.tolerance:.1f}")
            check("音画俱全", {"audio", "video"} <= kinds, "、".join(sorted(kinds)))
            lumas = [round(frame_luma(video, dur * p), 1) for p in (0.2, 0.5, 0.8)]
            check("非黑屏", all(l > 8 for l in lumas), f"抽帧亮度 {lumas}")

    passed = all(c["ok"] for c in checks.values())
    print(json.dumps({"status": "passed" if passed else "failed", "level": a.level, "checks": checks}, ensure_ascii=False, indent=2))
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
