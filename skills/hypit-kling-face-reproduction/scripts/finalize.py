#!/usr/bin/env python3
"""Finalize a downloaded edit against its original video and retain measured QC."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
from fractions import Fraction
from typing import Any
import uuid


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Match a generated video to a measured CFR timing source, "
            "restore original audio, and write measured QC plus a contact sheet."
        )
    )
    parser.add_argument("--generated", required=True, type=Path, help="Downloaded generated video")
    parser.add_argument("--source", required=True, type=Path, help="Original source.mp4")
    parser.add_argument(
        "--timing-source", type=Path,
        help="CFR video defining target frame rate/count; defaults to --source. Audio always comes from --source",
    )
    parser.add_argument("--output", required=True, type=Path, help="Final faststart MP4")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="FFmpeg executable")
    parser.add_argument("--ffprobe", default="ffprobe", help="FFprobe executable")
    parser.add_argument("--qc-dir", type=Path, help="Default: <output-stem>-qc beside output")
    parser.add_argument("--parent-build", help="Existing generating Hypit Build ID, when known")
    parser.add_argument("--parent-job", help="Existing human-service request ID, when known")
    parser.add_argument(
        "--max-retime-percent", type=float, default=5.0,
        help="Reject larger overall timing changes (default: 5%%)",
    )
    parser.add_argument("--overwrite", action="store_true", help="Replace the explicit output path")
    return parser.parse_args()


def run(command: list[str], commands: list[dict[str, Any]]) -> str:
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    commands.append({"argv": command, "returncode": completed.returncode, "stderr": completed.stderr[-16000:]})
    if completed.returncode:
        raise RuntimeError(
            f"{Path(command[0]).name} exited {completed.returncode}: "
            + completed.stderr[-4000:].strip()
        )
    return completed.stdout


def fraction(value: Any) -> Fraction | None:
    try:
        result = Fraction(str(value))
        return result if result > 0 else None
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def number(value: Any) -> float | None:
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def integer(value: Any) -> int | None:
    try:
        result = int(value)
        return result if result > 0 else None
    except (TypeError, ValueError):
        return None


def file_hash(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def probe(path: Path, executable: str, commands: list[dict[str, Any]]) -> dict[str, Any]:
    data = json.loads(run([
        executable, "-v", "error", "-count_frames", "-show_streams", "-show_format",
        "-of", "json", str(path),
    ], commands))
    streams = data.get("streams", [])
    video = next((stream for stream in streams if stream.get("codec_type") == "video"
                  and not stream.get("disposition", {}).get("attached_pic")), None)
    if video is None:
        raise RuntimeError(f"No moving video stream in {path.name}")
    audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    rate = fraction(video.get("avg_frame_rate")) or fraction(video.get("r_frame_rate"))
    count = integer(video.get("nb_read_frames")) or integer(video.get("nb_frames"))
    if rate is None or count is None:
        raise RuntimeError(f"Cannot determine video frame rate/count in {path.name}")
    return {
        "path": str(path), "frame_count": count, "frame_rate": str(rate),
        "frame_duration_seconds": float(Fraction(count, 1) / rate),
        "video_stream_duration_seconds": number(video.get("duration")),
        "container_duration_seconds": number(data.get("format", {}).get("duration")),
        "video": {key: video.get(key) for key in (
            "index", "codec_name", "width", "height", "pix_fmt", "bits_per_raw_sample",
            "color_range", "color_space", "color_transfer", "color_primaries", "start_time",
            "time_base", "avg_frame_rate", "r_frame_rate",
        )},
        "audio": None if audio is None else {key: audio.get(key) for key in (
            "index", "codec_name", "sample_rate", "channels", "channel_layout",
            "duration", "start_time", "nb_frames",
        )},
    }


def frame_clock(
    path: Path, information: dict[str, Any], executable: str, commands: list[dict[str, Any]],
) -> dict[str, Any]:
    """Use actual presentation timestamps; avg_frame_rate alone does not prove CFR."""
    data = json.loads(run([
        executable, "-v", "error", "-select_streams", str(information["video"]["index"]),
        "-show_frames", "-show_entries", "frame=best_effort_timestamp,best_effort_timestamp_time",
        "-of", "json", str(path),
    ], commands))
    time_base = fraction(information["video"].get("time_base"))
    timestamps: list[Fraction] = []
    for frame in data.get("frames", []):
        if time_base is not None and frame.get("best_effort_timestamp") is not None:
            timestamps.append(int(frame["best_effort_timestamp"]) * time_base)
        elif frame.get("best_effort_timestamp_time") is not None:
            timestamps.append(Fraction(str(frame["best_effort_timestamp_time"])))
        else:
            raise RuntimeError(f"Missing presentation timestamp in {path.name}")
    if len(timestamps) < 2 or len(timestamps) != information["frame_count"]:
        raise RuntimeError(f"Cannot establish a complete presentation clock for {path.name}")
    relative = [value - timestamps[0] for value in timestamps]
    deltas = [right - left for left, right in zip(timestamps, timestamps[1:])]
    # Accommodate quantization to the file's timestamp tick, not a whole-frame drift.
    tolerance = max(time_base / 2 if time_base else Fraction(0), Fraction(1, 1_000_000))
    candidates = []
    for value in (information["video"].get("r_frame_rate"), information["frame_rate"]):
        rate = fraction(value)
        if rate is not None and rate not in candidates:
            candidates.append(rate)
    measured = [(rate, max(abs(value - Fraction(index, 1) / rate)
                           for index, value in enumerate(relative))) for rate in candidates]
    best_rate, deviation = min(measured, key=lambda item: item[1])
    is_cfr = all(delta > 0 for delta in deltas) and deviation <= tolerance
    return {
        "is_cfr": is_cfr, "frame_rate": str(best_rate) if is_cfr else None,
        "observed_frame_count": len(timestamps), "first_pts_seconds": float(timestamps[0]),
        "last_pts_seconds": float(timestamps[-1]),
        "minimum_frame_interval_seconds": float(min(deltas)),
        "maximum_frame_interval_seconds": float(max(deltas)),
        "maximum_cfr_clock_deviation_seconds": float(deviation),
        "timestamp_tolerance_seconds": float(tolerance),
        "method": "all decoded frame presentation timestamps; nominal/average rates are candidates only",
    }


def audio_packets(path: Path, executable: str, commands: list[dict[str, Any]]) -> dict[str, Any]:
    data = json.loads(run([
        executable, "-v", "error", "-select_streams", "a:0", "-show_packets",
        "-show_data_hash", "sha256", "-show_entries",
        "packet=data_hash,size,pts_time,dts_time,duration_time", "-of", "json", str(path),
    ], commands))
    packets = data.get("packets", [])
    hashes = [packet.get("data_hash") for packet in packets]
    if any(not isinstance(value, str) or not value.startswith("SHA256:") for value in hashes):
        raise RuntimeError(f"FFprobe did not return a SHA256 payload hash for every audio packet in {path.name}")
    durations = [number(packet.get("duration_time")) for packet in packets]
    starts = [number(packet.get("pts_time")) for packet in packets]
    valid_starts = [value for value in starts if value is not None]
    ends = [start + duration for start, duration in zip(starts, durations)
            if start is not None and duration is not None]
    return {
        "packet_count": len(packets),
        "ordered_payload_sha256": hashlib.sha256("\n".join(hashes).encode("ascii")).hexdigest(),
        "packet_duration_sum_seconds": sum(value for value in durations if value is not None),
        "first_packet_pts_seconds": min(valid_starts) if valid_starts else None,
        "last_packet_end_seconds": max(ends) if ends else None,
        "packet_hashes": hashes,
    }


def compare_audio(source: dict[str, Any], final: dict[str, Any]) -> dict[str, Any]:
    left, right = source["packet_hashes"], final["packet_hashes"]
    mismatch = next((index for index, values in enumerate(zip(left, right)) if values[0] != values[1]), None)
    if mismatch is None and len(left) != len(right):
        mismatch = min(len(left), len(right))
    return {
        "algorithm": "FFprobe SHA256 of each encoded audio packet payload, in packet order",
        "source": {key: value for key, value in source.items() if key != "packet_hashes"},
        "final": {key: value for key, value in final.items() if key != "packet_hashes"},
        "equal": left == right,
        "first_differing_packet_index": mismatch,
        "difference": None if left == right else (
            f"Audio payload differs: source={len(left)} packets, final={len(right)} packets; "
            f"first difference at zero-based packet {mismatch}."
        ),
    }


def color_arguments(video: dict[str, Any]) -> list[str]:
    result: list[str] = []
    for key, flag in (
        ("color_range", "-color_range"), ("color_space", "-colorspace"),
        ("color_transfer", "-color_trc"), ("color_primaries", "-color_primaries"),
    ):
        value = video.get(key)
        if value and value not in {"unknown", "unspecified", "reserved"}:
            result += [flag, str(value)]
    # Keep the generated pixel format where libx264 supports it; do not silently reduce bit depth.
    pixel_format = video.get("pix_fmt")
    if pixel_format:
        result += ["-pix_fmt", str(pixel_format)]
    return result


def contact_sheet(
    final: Path, qc_directory: Path, frame_rate: Fraction, frame_count: int,
    executable: str, commands: list[dict[str, Any]],
) -> dict[str, Any]:
    duration = Fraction(frame_count, 1) / frame_rate
    times = list(range(math.ceil(float(duration))))
    frame_indices = sorted({min(frame_count - 1, round(Fraction(second, 1) * frame_rate)) for second in times})
    select = "+".join(f"eq(n\\,{index})" for index in frame_indices)
    columns = min(4, len(frame_indices))
    rows = math.ceil(len(frame_indices) / columns)
    path = qc_directory / "final-contact.png"
    filters = (
        f"select={select},scale=240:-2:flags=lanczos,"
        f"tile={columns}x{rows}:nb_frames={len(frame_indices)}:padding=8:margin=8:color=0x161616"
    )
    run([executable, "-hide_banner", "-v", "error", "-y", "-i", str(final),
         "-an", "-vf", filters, "-frames:v", "1", "-threads:v", "1", str(path)], commands)
    return {
        "path": str(path), "columns": columns, "rows": rows,
        "order": "left-to-right, top-to-bottom",
        "samples": [{"frame_index": index, "time_seconds": float(Fraction(index, 1) / frame_rate)}
                    for index in frame_indices],
        "visual_review": "not_performed_by_script",
    }


def main() -> int:
    args = arguments()
    generated = args.generated.expanduser().resolve(strict=True)
    source = args.source.expanduser().resolve(strict=True)
    timing_source = (args.timing_source or args.source).expanduser().resolve(strict=True)
    output = args.output.expanduser().resolve()
    if generated == source or output in {generated, source, timing_source}:
        raise RuntimeError("Final output must be separate from all inputs; generated and original must differ")
    if not all(path.is_file() for path in (generated, source, timing_source)):
        raise RuntimeError("Generated, original and timing inputs must be local files")
    if output.suffix.lower() != ".mp4":
        raise RuntimeError("Output must have the .mp4 extension")
    if output.exists() and not args.overwrite:
        raise RuntimeError("Output exists; choose a new path or use --overwrite")
    if not math.isfinite(args.max_retime_percent) or not 0 <= args.max_retime_percent <= 20:
        raise RuntimeError("--max-retime-percent must be between 0 and 20")
    output.parent.mkdir(parents=True, exist_ok=True)
    qc_directory = (args.qc_dir.expanduser().resolve() if args.qc_dir else
                    output.parent / f"{output.stem}-qc")
    qc_directory.mkdir(parents=True, exist_ok=True)
    report_path = qc_directory / "final-QC.json"
    temporary = output.parent / f".{output.stem}.{uuid.uuid4().hex}.partial.mp4"
    commands: list[dict[str, Any]] = []
    report: dict[str, Any] = {
        "format": "hypit.final-video-qc@1", "status": "running",
        "generated_path": str(generated), "source_path": str(source), "output_path": str(output),
        "timing_source_path": str(timing_source),
        "commands": commands, "visual_review": "not_performed_by_script",
        "parent": {"build": args.parent_build, "job": args.parent_job, "output": "edit.video" if args.parent_build else None},
        "file_sha256": {"source": file_hash(source), "timing_source": file_hash(timing_source), "generated": file_hash(generated)},
    }
    try:
        source_info = probe(source, args.ffprobe, commands)
        timing_info = source_info if timing_source == source else probe(timing_source, args.ffprobe, commands)
        generated_info = probe(generated, args.ffprobe, commands)
        report["source"] = source_info
        report["timing_source"] = timing_info
        report["generated"] = generated_info
        source_clock = frame_clock(source, source_info, args.ffprobe, commands)
        timing_clock = source_clock if timing_source == source else frame_clock(timing_source, timing_info, args.ffprobe, commands)
        report["source_frame_clock"] = source_clock
        report["timing_source_frame_clock"] = timing_clock
        if not timing_clock["is_cfr"]:
            if args.timing_source is None:
                raise RuntimeError(
                    "Source video has VFR or irregular presentation timestamps. Supply --timing-source "
                    "with a CFR copy created from original PTS; audio will still come from --source. "
                    "No average-frame-rate timing has been applied."
                )
            raise RuntimeError("--timing-source must have a measured CFR presentation clock; VFR timing is not accepted")
        rate = Fraction(timing_clock["frame_rate"])
        count = timing_info["frame_count"]
        target_duration = Fraction(count, 1) / rate
        generated_duration = Fraction(generated_info["frame_count"], 1) / Fraction(generated_info["frame_rate"])
        requested_factor = target_duration / generated_duration
        difference_percent = abs(float(requested_factor) - 1.0) * 100
        if difference_percent > args.max_retime_percent:
            raise RuntimeError(
                f"Required retime is {difference_percent:.4f}%, above the permitted "
                f"{args.max_retime_percent:.4f}%"
            )
        # Ignore sub-half-frame container rounding while still producing exactly the source frames.
        retime = abs(target_duration - generated_duration) > Fraction(1, 2) / rate
        factor = requested_factor if retime else Fraction(1, 1)
        filters = (
            f"setpts=(PTS-STARTPTS)*{factor.numerator}/{factor.denominator},"
            f"fps=fps={rate}:start_time=0:round=near,"
            f"tpad=stop_mode=clone:stop_duration={float(2 / rate):.12f},"
            f"trim=end_frame={count},setpts=N/({rate}*TB)"
        )
        report["timing"] = {
            "authority": "timing-source" if args.timing_source else "source",
            "audio_authority": "source",
            "target_frame_rate": str(rate), "target_frame_count": count,
            "target_video_duration_seconds": float(target_duration),
            "retime_applied": retime, "pts_multiplier": str(factor),
            "overall_duration_change_percent": (float(factor) - 1.0) * 100,
            "max_retime_percent": args.max_retime_percent,
            "frame_rate_conversion": generated_info["frame_rate"] != str(rate),
        }
        has_audio = source_info["audio"] is not None
        audio_modes = ["copy", "aac"] if has_audio else ["none"]
        last_error: RuntimeError | None = None
        for audio_mode in audio_modes:
            command = [args.ffmpeg, "-hide_banner", "-nostdin", "-y", "-i", str(generated), "-i", str(source),
                       "-map", f"0:{generated_info['video']['index']}"]
            command += ["-map", f"1:{source_info['audio']['index']}"] if has_audio else ["-an"]
            command += ["-map_metadata", "0", "-vf", filters, "-c:v", "libx264", "-preset", "slow",
                        "-crf", "16", "-tag:v", "avc1", "-fps_mode", "cfr"]
            command += color_arguments(generated_info["video"])
            if has_audio:
                command += ["-c:a", audio_mode]
                if audio_mode == "aac":
                    command += ["-b:a", "256k"]
            command += ["-movflags", "+faststart", str(temporary)]
            try:
                run(command, commands)
                report["audio_mode"] = audio_mode
                report["transcode_command"] = command
                last_error = None
                break
            except RuntimeError as error:
                last_error = error
                if audio_mode == "copy":
                    report["audio_copy_failure"] = str(error)
        if last_error is not None:
            raise last_error
        final_info = probe(temporary, args.ffprobe, commands)
        generated_video, final_video = generated_info["video"], final_info["video"]
        measured_checks = {
            "frame_count_matches_timing_source": final_info["frame_count"] == count,
            "frame_rate_matches_timing_source": Fraction(final_info["frame_rate"]) == rate,
            "video_duration_matches_timing_source_frames": abs(final_info["frame_duration_seconds"] - float(target_duration)) < 1e-6,
            "video_stream_duration_matches_timing_source_frames": (
                final_info["video_stream_duration_seconds"] is not None
                and abs(final_info["video_stream_duration_seconds"] - float(target_duration)) < 1e-5
            ),
            "resolution_matches_generated": all(final_video.get(key) == generated_video.get(key) for key in ("width", "height")),
            "color_tags_match_generated": all(final_video.get(key) == generated_video.get(key)
                for key in ("color_range", "color_space", "color_transfer", "color_primaries")
                if generated_video.get(key) not in {None, "unknown", "unspecified", "reserved"}),
            "pixel_format_matches_generated": final_video.get("pix_fmt") == generated_video.get("pix_fmt"),
        }
        report["checks"] = measured_checks
        report["final"] = final_info
        if not all(measured_checks.values()):
            report["candidate_path"] = str(temporary)
            raise RuntimeError("Final media checks differ from the requested timing, resolution or color; candidate retained")
        source_packets = audio_packets(source, args.ffprobe, commands)
        final_packets = audio_packets(temporary, args.ffprobe, commands)
        report["audio_packet_hash"] = compare_audio(source_packets, final_packets)
        if not has_audio:
            report["audio_packet_hash"]["applicability"] = "source_has_no_audio"
        os.replace(temporary, output)
        report["file_sha256"]["final"] = file_hash(output)
        report["final"]["path"] = str(output)
        report["contact_sheet"] = contact_sheet(output, qc_directory, rate, count, args.ffmpeg, commands)
        payload_equal = report["audio_packet_hash"]["equal"]
        report["status"] = "measured_checks_passed_visual_review_pending" if payload_equal else "audio_payload_difference_visual_review_pending"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"output": str(output), "qc": str(report_path), "status": report["status"],
                          "audio_packet_payload_equal": payload_equal}, ensure_ascii=False))
        return 0 if payload_equal else 2
    except Exception as error:
        report["status"] = "failed"
        report["error"] = str(error)
        if temporary.exists():
            report["candidate_path"] = str(temporary)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Finalization failed; measured evidence: {report_path}\n{error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
