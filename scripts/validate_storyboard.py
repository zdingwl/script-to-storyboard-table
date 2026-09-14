#!/usr/bin/env python3
"""Validate storyboard.json produced by script-to-storyboard-table.

Python 3 standard library only.
Usage:
    python scripts/validate_storyboard.py storyboard.json
    python scripts/validate_storyboard.py storyboard.json --strict
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

VALID_MODES = {"faithful", "visual", "pacing", "story"}
H3_MIN_SECONDS = 4.0
H3_MAX_SECONDS = 15.0
H3_MAX_IMAGES = 9
H3_MAX_VIDEOS = 3
H3_MAX_AUDIOS = 3
H3_MAX_MIXED_REFS = 12


def approx(a, b, eps=1e-6):
    return math.isclose(float(a), float(b), abs_tol=eps)


def validate(data):
    errors = []
    warnings = []
    seen_ids = set()

    def error(msg):
        errors.append(msg)

    def warn(msg):
        warnings.append(msg)

    def unique_id(value, where):
        if not value:
            error(f"{where}: missing id")
            return
        if value in seen_ids:
            error(f"{where}: duplicate id {value}")
        seen_ids.add(value)

    if not isinstance(data, dict):
        return ["root: JSON must be an object"], []

    if str(data.get("schema_version", "")) != "2.0":
        warn("root: schema_version is not '2.0'")

    project = data.get("project") or {}
    mode = project.get("mode", "faithful")
    if mode not in VALID_MODES:
        error(f"project.mode: unsupported value {mode!r}")

    episodes = data.get("episodes")
    if not isinstance(episodes, list) or not episodes:
        error("root.episodes: expected a non-empty list")
        return errors, warnings

    for ep_i, episode in enumerate(episodes, 1):
        where_ep = f"episodes[{ep_i}]"
        if not isinstance(episode, dict):
            error(f"{where_ep}: expected object")
            continue
        unique_id(episode.get("id"), where_ep)

        scenes = episode.get("scenes") or []
        if not scenes:
            warn(f"{where_ep}: no scenes")

        for sc_i, scene in enumerate(scenes, 1):
            where_sc = f"{where_ep}.scenes[{sc_i}]"
            if not isinstance(scene, dict):
                error(f"{where_sc}: expected object")
                continue

            scene_id = scene.get("id")
            unique_id(scene_id, where_sc)

            beats = scene.get("beats") or []
            beat_ids = []
            must_preserve = set()
            for b_i, beat in enumerate(beats, 1):
                where_b = f"{where_sc}.beats[{b_i}]"
                if not isinstance(beat, dict):
                    error(f"{where_b}: expected object")
                    continue
                bid = beat.get("id")
                unique_id(bid, where_b)
                if bid:
                    beat_ids.append(bid)
                    if beat.get("must_preserve", True):
                        must_preserve.add(bid)

            beat_set = set(beat_ids)
            coverage = Counter()

            def check_shot(shot, where_shot, expected_segment=None):
                if not isinstance(shot, dict):
                    error(f"{where_shot}: shot must be object")
                    return None

                unique_id(shot.get("id"), where_shot)

                if scene_id and shot.get("scene_id") not in (None, scene_id):
                    error(
                        f"{where_shot}: scene_id {shot.get('scene_id')!r} "
                        f"does not match parent {scene_id!r}"
                    )

                if expected_segment and shot.get("segment_id") not in (None, expected_segment):
                    error(
                        f"{where_shot}: segment_id {shot.get('segment_id')!r} "
                        f"does not match parent {expected_segment!r}"
                    )

                src = shot.get("source_beats") or []
                if not src:
                    warn(f"{where_shot}: no source_beats")
                for bid in src:
                    coverage[bid] += 1
                    if beat_set and bid not in beat_set:
                        error(f"{where_shot}: unknown source beat {bid}")

                duration = shot.get("duration_seconds")
                if duration is None:
                    error(f"{where_shot}: missing duration_seconds")
                    return None
                try:
                    duration = float(duration)
                except (TypeError, ValueError):
                    error(f"{where_shot}: duration_seconds must be numeric")
                    return None
                if duration <= 0:
                    error(f"{where_shot}: duration_seconds must be > 0")

                tin = shot.get("timecode_in")
                tout = shot.get("timecode_out")
                if tin is not None and tout is not None:
                    try:
                        if not approx(float(tout) - float(tin), duration, 1e-3):
                            error(
                                f"{where_shot}: timecode_out - timecode_in "
                                f"!= duration_seconds"
                            )
                    except (TypeError, ValueError):
                        error(f"{where_shot}: timecodes must be numeric seconds")

                if not shot.get("start_state"):
                    warn(f"{where_shot}: missing start_state")
                if not shot.get("end_state"):
                    warn(f"{where_shot}: missing end_state")
                if not shot.get("shot_size"):
                    warn(f"{where_shot}: missing shot_size")
                if not shot.get("camera_movement"):
                    warn(f"{where_shot}: missing camera_movement")

                return duration

            # Traditional workflow: shots directly under the scene.
            scene_shots = scene.get("shots") or []
            previous_out = None
            for sh_i, shot in enumerate(scene_shots, 1):
                where_shot = f"{where_sc}.shots[{sh_i}]"
                check_shot(shot, where_shot)
                if isinstance(shot, dict):
                    tin = shot.get("timecode_in")
                    tout = shot.get("timecode_out")
                    if previous_out is not None and tin is not None:
                        try:
                            if not approx(previous_out, float(tin), 1e-3):
                                warn(f"{where_shot}: timecode is not contiguous with previous shot")
                        except (TypeError, ValueError):
                            pass
                    if tout is not None:
                        try:
                            previous_out = float(tout)
                        except (TypeError, ValueError):
                            pass

            # AI workflow: shots grouped inside generation segments.
            segments = scene.get("generation_segments") or []
            for sg_i, segment in enumerate(segments, 1):
                where_sg = f"{where_sc}.generation_segments[{sg_i}]"
                if not isinstance(segment, dict):
                    error(f"{where_sg}: expected object")
                    continue

                segment_id = segment.get("id")
                unique_id(segment_id, where_sg)
                if scene_id and segment.get("scene_id") not in (None, scene_id):
                    error(f"{where_sg}: segment crosses/mismatches parent scene")

                seg_shots = segment.get("shots") or []
                sum_duration = 0.0
                previous_local_out = None

                for sh_i, shot in enumerate(seg_shots, 1):
                    where_shot = f"{where_sg}.shots[{sh_i}]"
                    if isinstance(shot, str):
                        warn(f"{where_shot}: ID-only shot cannot be deeply validated")
                        continue
                    duration = check_shot(shot, where_shot, segment_id)
                    if duration is not None:
                        sum_duration += duration

                    if isinstance(shot, dict):
                        tin = shot.get("timecode_in")
                        tout = shot.get("timecode_out")
                        if previous_local_out is not None and tin is not None:
                            try:
                                if not approx(previous_local_out, float(tin), 1e-3):
                                    warn(f"{where_shot}: timecode is not contiguous with previous shot")
                            except (TypeError, ValueError):
                                pass
                        if tout is not None:
                            try:
                                previous_local_out = float(tout)
                            except (TypeError, ValueError):
                                pass

                declared = segment.get("duration_seconds")
                if declared is not None:
                    try:
                        declared_f = float(declared)
                        if seg_shots and not approx(declared_f, sum_duration, 1e-3):
                            error(
                                f"{where_sg}: duration_seconds={declared_f:g} "
                                f"but shots sum to {sum_duration:g}"
                            )
                    except (TypeError, ValueError):
                        error(f"{where_sg}: duration_seconds must be numeric")
                        declared_f = None
                else:
                    declared_f = sum_duration if seg_shots else None

                target = str(segment.get("target_model") or project.get("target_video_model") or "")
                if "minimax" in target.lower() and "h3" in target.lower():
                    if declared_f is not None and not (H3_MIN_SECONDS <= declared_f <= H3_MAX_SECONDS):
                        error(
                            f"{where_sg}: MiniMax H3 duration {declared_f:g}s "
                            f"outside {H3_MIN_SECONDS:g}-{H3_MAX_SECONDS:g}s"
                        )

                    refs = segment.get("reference_assets") or []
                    if len(refs) > H3_MAX_MIXED_REFS:
                        error(f"{where_sg}: H3 mixed references exceed {H3_MAX_MIXED_REFS}")

                    image_n = video_n = audio_n = 0
                    labels = []
                    for ref in refs:
                        if not isinstance(ref, dict):
                            warn(f"{where_sg}: reference asset should be an object")
                            continue
                        label = str(ref.get("label") or "")
                        labels.append(label)
                        low = label.lower()
                        if low.startswith("picture") or low.startswith("image"):
                            image_n += 1
                        elif low.startswith("video"):
                            video_n += 1
                        elif low.startswith("audio"):
                            audio_n += 1
                    if image_n > H3_MAX_IMAGES:
                        error(f"{where_sg}: H3 image references exceed {H3_MAX_IMAGES}")
                    if video_n > H3_MAX_VIDEOS:
                        error(f"{where_sg}: H3 video references exceed {H3_MAX_VIDEOS}")
                    if audio_n > H3_MAX_AUDIOS:
                        error(f"{where_sg}: H3 audio references exceed {H3_MAX_AUDIOS}")
                    nonempty_labels = [x for x in labels if x]
                    if len(nonempty_labels) != len(set(nonempty_labels)):
                        error(f"{where_sg}: duplicate reference labels")

            # Beat coverage is checked after both scene-level and segment-level shots.
            for bid in sorted(must_preserve):
                if coverage[bid] == 0:
                    error(f"{where_sc}: must-preserve beat not covered: {bid}")
                elif coverage[bid] > 1:
                    warn(
                        f"{where_sc}: beat {bid} covered {coverage[bid]} times; "
                        "add coverage_exception if intentional"
                    )

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate storyboard.json")
    parser.add_argument("file", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failure")
    args = parser.parse_args()

    try:
        data = json.loads(args.file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.file}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
        return 2

    errors, warnings = validate(data)

    for item in warnings:
        print(f"WARNING: {item}")
    for item in errors:
        print(f"ERROR: {item}")

    print(f"\nValidation summary: {len(errors)} error(s), {len(warnings)} warning(s)")

    if errors:
        return 1
    if warnings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
