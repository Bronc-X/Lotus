"""Exercise only the local VFR timing boundary with two-second synthetic media."""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile


def sha256(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', default='ffmpeg')
    parser.add_argument('--ffprobe', default='ffprobe')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    finalizer = Path(__file__).resolve().with_name('finalize.py')
    report = {
        'format': 'hypit.finalizer-vfr-validation@1', 'status': 'RUNNING',
        'startedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'Two-second synthetic media: VFR rejection, explicit CFR timing with original audio, default CFR regression',
        'pythonVersion': platform.python_version(), 'platform': platform.system(),
        'finalizerSha256': sha256(finalizer), 'testScriptSha256': sha256(Path(__file__)),
        'cloudGenerationPerformed': False, 'runtimeTouched': False,
        'visualIdentityQualityAccepted': False, 'independentForwardTestPerformed': False,
        'cases': [],
    }
    environment = os.environ.copy()
    environment.update({'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'})

    def run_case(name, argv, expected=0):
        result = subprocess.run(argv, capture_output=True, text=True, encoding='utf-8',
                                errors='replace', env=environment, timeout=45)
        passed = result.returncode == expected
        report['cases'].append({
            'case': name, 'status': 'PASS' if passed else 'FAIL', 'exitCode': result.returncode,
            'stdoutSha256': hashlib.sha256(result.stdout.encode('utf-8')).hexdigest(),
            'stderrSha256': hashlib.sha256(result.stderr.encode('utf-8')).hexdigest(),
        })
        if not passed:
            raise RuntimeError(name + ' failed: ' + (result.stdout + result.stderr)[-3000:])
        return result

    try:
        with tempfile.TemporaryDirectory(prefix='hypit-vfr-boundary-') as directory:
            root = Path(directory)
            source_cfr, source_vfr = root/'original-cfr.mp4', root/'original-vfr.mp4'
            timing, generated = root/'timing-cfr.mp4', root/'generated-fixture.mp4'
            run_case('make-two-second-cfr-source', [args.ffmpeg, '-hide_banner', '-v', 'error', '-y',
                '-f', 'lavfi', '-i', 'testsrc2=size=320x240:rate=30:duration=2',
                '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000:duration=2',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', str(source_cfr)])
            # Keep the original PTS while removing alternate frames only during the second half.
            select = 'select=lt(n\\,30)+gte(n\\,30)*not(mod(n\\,2))+eq(n\\,59)'
            run_case('make-two-second-vfr-source', [args.ffmpeg, '-hide_banner', '-v', 'error', '-y',
                '-i', str(source_cfr), '-vf', select, '-fps_mode', 'vfr',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'copy', str(source_vfr)])
            # This fixture's declared span is exactly 2 s; discard codec tail padding
            # after PTS resampling, without changing the retained frame timestamps.
            run_case('make-pts-preserving-cfr-timing', [args.ffmpeg, '-hide_banner', '-v', 'error', '-y',
                '-i', str(source_vfr), '-map', '0:v:0', '-vf', 'fps=30:start_time=0:round=near,trim=duration=2',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-an', str(timing)])
            run_case('make-generated-fixture-without-audio', [args.ffmpeg, '-hide_banner', '-v', 'error', '-y',
                '-i', str(timing), '-map', '0:v:0', '-c:v', 'copy', '-an', str(generated)])
            common = [sys.executable, str(finalizer), '--generated', str(generated),
                      '--ffmpeg', args.ffmpeg, '--ffprobe', args.ffprobe]
            rejected = root/'vfr-rejected.mp4'
            rejection = run_case('reject-vfr-without-explicit-cfr-timing', common + [
                '--source', str(source_vfr), '--output', str(rejected)], expected=1)
            rejected_qc = json.loads((root/'vfr-rejected-qc/final-QC.json').read_text(encoding='utf-8'))
            assert not rejected.exists() and rejected_qc['source_frame_clock']['is_cfr'] is False
            assert '--timing-source' in rejection.stderr
            assert all(Path(item['argv'][0]).name.lower() not in {'ffmpeg', 'ffmpeg.exe'}
                       for item in rejected_qc['commands'])
            report['cases'].append({'case': 'vfr-rejection-before-transcode', 'status': 'PASS'})
            run_case('reject-explicit-vfr-timing', common + ['--source', str(source_vfr),
                '--timing-source', str(source_vfr), '--output', str(root/'invalid-timing.mp4')], expected=1)
            assert not (root/'invalid-timing.mp4').exists()
            final = root/'final.mp4'
            run_case('accept-explicit-cfr-timing-and-original-audio', common + ['--source', str(source_vfr),
                '--timing-source', str(timing), '--output', str(final)])
            qc = json.loads((root/'final-qc/final-QC.json').read_text(encoding='utf-8'))
            report['observedTiming'] = {
                'sourceFrames': qc['source']['frame_count'],
                'timingFrames': qc['timing_source']['frame_count'],
                'timingRate': qc['timing']['target_frame_rate'],
                'targetDurationSeconds': qc['timing']['target_video_duration_seconds'],
                'sourceClock': qc['source_frame_clock'],
                'timingClock': qc['timing_source_frame_clock'],
            }
            assert all(qc['checks'].values())
            assert qc['source_frame_clock']['is_cfr'] is False and qc['timing_source_frame_clock']['is_cfr'] is True
            assert qc['timing']['authority'] == 'timing-source' and qc['timing']['audio_authority'] == 'source'
            assert qc['timing']['target_frame_count'] == 60 and qc['timing']['target_frame_rate'] == '30'
            assert qc['timing_source']['audio'] is None
            assert qc['audio_packet_hash']['equal'] is True and qc['audio_packet_hash']['source']['packet_count'] > 0
            assert qc['file_sha256']['source'] == sha256(source_vfr)
            assert qc['file_sha256']['timing_source'] == sha256(timing)
            assert qc['file_sha256']['final'] == sha256(final)
            report['cases'].append({'case': 'separate-timing-audio-authorities-hashes-and-60-frame-clock',
                'status': 'PASS', 'audioPackets': qc['audio_packet_hash']['source']['packet_count'],
                'targetFrameCount': 60, 'targetFrameRate': '30',
                'sourceIntervalsSeconds': [qc['source_frame_clock']['minimum_frame_interval_seconds'],
                                          qc['source_frame_clock']['maximum_frame_interval_seconds']]})
            run_case('default-cfr-source-still-works', common + ['--source', str(source_cfr),
                '--output', str(root/'cfr-default.mp4')])
            cfr_qc = json.loads((root/'cfr-default-qc/final-QC.json').read_text(encoding='utf-8'))
            assert cfr_qc['timing']['authority'] == 'source' and all(cfr_qc['checks'].values())
            assert cfr_qc['audio_packet_hash']['equal'] is True
            report['status'] = 'TECHNICAL_PASS'
    except Exception as error:
        report['status'] = 'FAILED'
        report['failureType'] = type(error).__name__
        print(type(error).__name__ + ': ' + str(error), file=sys.stderr)
    report['finishedAt'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    report['passedCases'] = sum(case['status'] == 'PASS' for case in report['cases'])
    report['failedCases'] = sum(case['status'] == 'FAIL' for case in report['cases'])
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'TECHNICAL_PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
