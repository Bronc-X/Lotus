#!/usr/bin/env python3
"""Put two videos on one frame clock without silently guessing a retiming."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from fractions import Fraction


def run(argv, **kwargs):
    result = subprocess.run(argv, capture_output=True, **kwargs)
    if result.returncode:
        error = result.stderr.decode("utf-8", "replace") if isinstance(result.stderr, bytes) else result.stderr
        raise RuntimeError(error[-5000:])
    return result.stdout


def probe(path, ffprobe):
    data = json.loads(run([ffprobe, "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", str(path)]))
    video = next(s for s in data["streams"] if s["codec_type"] == "video")
    return data, video


def file_hash(path):
    with open(path, "rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def audio_hash(path, ffmpeg):
    return run([ffmpeg, "-v", "error", "-i", str(path), "-map", "0:a:0", "-c", "copy", "-f", "hash", "-hash", "sha256", "-"]).decode().strip()


def pick_font(explicit):
    candidates = [Path(explicit)] if explicit else [
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/msyh.ttc",
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise RuntimeError("No suitable CJK font found; pass --font with a local font path")


def ffpath(path):
    # This is FFmpeg filter quoting, not shell quoting. All execution uses argv.
    return str(path).replace("\\", "/").replace(":", "\\:").replace("'", "'\\\\''")


def coarse_alignment(left, right, count, rate, ffmpeg):
    """A background/body diagnostic; it does not verify facial identity or lip sync."""
    width, height = 32, 56
    def frames(path):
        raw = run([ffmpeg, "-v", "error", "-i", str(path), "-an", "-vf", f"scale={width}:{height}:flags=area,format=gray", "-f", "rawvideo", "-"])
        size = width * height
        indices = [y * width + x for y in range(height) for x in range(width)
                   if y < 9 or y >= 43 or x >= 30]
        return [bytes(raw[offset+i] for i in indices) for offset in range(0, len(raw), size) if offset+size <= len(raw)]
    a, b = frames(left), frames(right)
    span = max(1, round(float(rate) / 2))
    windows = [(0, min(count, round(float(rate)*3))),
               (min(count, round(float(rate)*3)), min(count, round(float(rate)*7))),
               (min(count, round(float(rate)*7)), count)]
    def score(start, end, lag):
        differences = []
        for i in range(start, end, 2):
            j = i + lag
            if 0 <= i < len(a) and 0 <= j < len(b):
                differences.append(sum(abs(x-y) for x,y in zip(a[i], b[j])) / len(a[i]))
        return sum(differences)/len(differences) if differences else float("inf")
    results = []
    for start, end in windows:
        if start == end:
            continue
        scores = [(lag, score(start, end, lag)) for lag in range(-span, span+1)]
        best = min(scores, key=lambda value: value[1])
        results.append({"start_frame":start, "end_frame":end, "best_right_lag_frames":best[0],
                        "best_mean_absolute_luma_error":best[1], "zero_lag_error":score(start,end,0)})
    return {"method":"32x56 grayscale, outer background/body regions, search +/-0.5s; coarse diagnostic only",
            "windows":results, "retiming_performed":False, "visual_review_required":True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--left-label", default="左侧视频")
    parser.add_argument("--right-label", default="右侧视频")
    parser.add_argument("--font")
    parser.add_argument("--height", type=int)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    left, right = args.left.resolve(strict=True), args.right.resolve(strict=True)
    output = args.output.resolve()
    if output in {left, right}:
        raise RuntimeError("Output must be separate from both inputs")
    if output.exists() and not args.overwrite:
        raise RuntimeError("Output exists; select a new filename or explicitly use --overwrite")
    left_data, lv = probe(left, args.ffprobe)
    _, rv = probe(right, args.ffprobe)
    rate_l, rate_r = Fraction(lv["avg_frame_rate"]), Fraction(rv["avg_frame_rate"])
    count_l, count_r = int(lv["nb_read_frames"]), int(rv["nb_read_frames"])
    if rate_l != rate_r or count_l != count_r:
        raise RuntimeError("Input frame rates/counts differ; inspect event alignment and normalize explicitly before comparison")
    frame_times = []
    for path in (left, right):
        frame_data = json.loads(run([args.ffprobe, "-v", "error", "-select_streams", "v:0", "-show_frames", "-show_entries", "frame=best_effort_timestamp_time", "-of", "json", str(path)]))
        times = [Fraction(f["best_effort_timestamp_time"]) for f in frame_data["frames"]]
        times = [t-times[0] for t in times]
        if any(abs(t - Fraction(i, 1)/rate_l) > Fraction(1, 10000) for i,t in enumerate(times)):
            raise RuntimeError("Variable or irregular frame timestamps require explicit normalization")
        frame_times.append(times)
    height = args.height or min(int(lv["height"]), int(rv["height"]))
    height = height // 2 * 2
    if height < 64:
        raise RuntimeError("Panel height must be at least 64")
    width = round(height * int(lv["width"]) / int(lv["height"]) / 2) * 2
    header = max(32, round(height * .0377 / 2) * 2)
    font = pick_font(args.font)
    fontsize = max(18, round(height * .020))
    output.parent.mkdir(parents=True, exist_ok=True)
    alignment = coarse_alignment(left, right, count_l, rate_l, args.ffmpeg)
    with tempfile.TemporaryDirectory(prefix="video-compare-") as temporary:
        cwd = Path(temporary)
        (cwd / "left.txt").write_text(args.left_label, encoding="utf-8")
        (cwd / "right.txt").write_text(args.right_label, encoding="utf-8")
        chains = []
        for i, name in enumerate(("left", "right")):
            chains.append(f"[{i}:v]setpts=PTS-STARTPTS,setsar=1,scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:x=(ow-iw)/2:y=(oh-ih)/2:color=black,pad=iw:ih+{header}:0:{header}:color=0x111111,drawtext=fontfile='{ffpath(font)}':textfile={name}.txt:fontcolor=white:fontsize={fontsize}:x=(w-text_w)/2:y=({header}-text_h)/2[{name}]")
        chains.append("[left][right]hstack=inputs=2:shortest=1[comparison]")
        command = [args.ffmpeg, "-hide_banner", "-v", "error", "-y", "-i", str(left), "-i", str(right),
                   "-filter_complex", ";".join(chains), "-map", "[comparison]", "-map", "0:a:0?",
                   "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
                   "-fps_mode", "cfr", "-r", str(rate_l), "-c:a", "copy", "-movflags", "+faststart", str(output)]
        run(command, cwd=cwd)
    final_data, final = probe(output, args.ffprobe)
    has_audio = any(s["codec_type"] == "audio" for s in left_data["streams"])
    checks = {"frame_count":int(final["nb_read_frames"]) == count_l,
              "frame_rate":Fraction(final["avg_frame_rate"]) == rate_l,
              "canvas":final["width"] == width*2 and final["height"] == height+header,
              "audio_payload_equal":audio_hash(left,args.ffmpeg) == audio_hash(output,args.ffmpeg) if has_audio else True}
    report = {"status":"technical_checks_passed_visual_review_pending" if all(checks.values()) else "failed",
              "left_input":str(left), "right_input":str(right), "left_label":args.left_label, "right_label":args.right_label,
              "input_sha256":{"left":file_hash(left),"right":file_hash(right)},
              "output":str(output), "output_sha256":file_hash(output), "checks":checks,
              "clock":{"frame_rate":str(rate_l),"frame_count":count_l,"duration_seconds":float(Fraction(count_l,1)/rate_l),
                       "retime":False,"mapping":"left frame n and right frame n displayed at n/fps"},
              "alignment_diagnostic":alignment,"ffmpeg_argv":command}
    output.with_suffix(".qc.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(output),"checks":checks,"alignment":alignment},ensure_ascii=False))
    if not all(checks.values()):
        raise RuntimeError("Comparison failed measured checks; see adjacent .qc.json")


if __name__ == "__main__":
    main()
