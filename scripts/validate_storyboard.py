#!/usr/bin/env python3
"""Deterministic validator for script-to-storyboard-table schema v3."""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

VALID_MODES = {"faithful", "visual", "pacing", "story"}
HANDOFF_TYPES = {
    "direct", "match_on_action", "eyeline", "reaction", "insert",
    "insert_return", "sound_bridge", "reframe", "motivated_jump",
    "time_jump", "scene_cut",
}
TIMING_SOURCES = {
    "measured_audio", "measured_tts", "scripted", "estimated_target_text",
    "estimated", "inherited_source",
}
H3_RULES_VERIFIED_AT = "2026-10-03"
H3 = {
    "min": 4.0, "max": 15.0, "images": 9, "videos": 3, "audios": 3,
    "mixed": 12, "ref_min": 2.0, "ref_max": 15.0,
    "video_total": 15.0, "audio_total": 15.0,
}


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def close(a, b, eps=1e-3):
    return math.isclose(float(a), float(b), abs_tol=eps)


def validate(data):
    errors, warnings = [], []
    seen = set()

    def error(msg): errors.append(msg)
    def warn(msg): warnings.append(msg)
    def uid(value, where):
        if not value:
            error(f"{where}: missing id")
        elif str(value) in seen:
            error(f"{where}: duplicate id {value}")
        else:
            seen.add(str(value))

    if not isinstance(data, dict):
        return ["root: JSON must be an object"], []

    version = str(data.get("schema_version", ""))
    if version != "3.0":
        warn(f"root: schema_version {version!r}; validator is optimized for 3.0")

    project = data.get("project") or {}
    if project.get("mode", "faithful") not in VALID_MODES:
        error(f"project.mode: unsupported value {project.get('mode')!r}")

    source_lang = project.get("source_language")
    output_lang = project.get("output_language")
    dialogue_lang = project.get("dialogue_language")
    translated = bool(source_lang and output_lang and source_lang != output_lang)
    project_model = str(project.get("target_video_model") or "")
    if "minimax" in project_model.lower() and "h3" in project_model.lower():
        verified = (project.get("model_profile") or {}).get("verified_at")
        if verified != H3_RULES_VERIFIED_AT:
            warn(
                "project.model_profile.verified_at: expected "
                f"{H3_RULES_VERIFIED_AT!r}; re-check current official H3 limits"
            )

    assets = data.get("assets") or {}
    asset_ids = {
        key: {str(x.get("id")) for x in assets.get(key, []) if isinstance(x, dict) and x.get("id")}
        for key in ("characters", "scenes", "props")
    }

    episodes = data.get("episodes")
    if not isinstance(episodes, list) or not episodes:
        return ["root.episodes: expected a non-empty list"], warnings

    project_runtime = 0.0

    for ei, episode in enumerate(episodes, 1):
        epw = f"episodes[{ei}]"
        if not isinstance(episode, dict):
            error(f"{epw}: expected object")
            continue
        uid(episode.get("id"), epw)

        ending = ((episode.get("hook_audit") or {}).get("ending") or {})
        if isinstance(ending, dict) and ending.get("type") == "result_only":
            warn(f"{epw}.hook_audit.ending: result_only is not an unresolved hook")

        scenes = episode.get("scenes") or []
        if not isinstance(scenes, list):
            error(f"{epw}.scenes: expected list")
            continue

        episode_runtime = 0.0
        for si, scene in enumerate(scenes, 1):
            scw = f"{epw}.scenes[{si}]"
            if not isinstance(scene, dict):
                error(f"{scw}: expected object")
                continue
            scene_id = scene.get("id")
            uid(scene_id, scw)

            if version == "3.0":
                plan = scene.get("director_plan")
                if not isinstance(plan, dict):
                    warn(f"{scw}: missing director_plan")
                else:
                    for key in ("dramatic_job", "turn", "blocking_plan"):
                        if not plan.get(key): warn(f"{scw}.director_plan: missing {key}")
                    if not plan.get("coverage_obligations"):
                        warn(f"{scw}.director_plan: no coverage_obligations")

            beats = scene.get("beats") or []
            beat_ids, beat_index, must = [], {}, set()
            for bi, beat in enumerate(beats, 1):
                bw = f"{scw}.beats[{bi}]"
                if not isinstance(beat, dict):
                    error(f"{bw}: expected object")
                    continue
                bid = beat.get("id")
                uid(bid, bw)
                if bid:
                    bid = str(bid)
                    beat_index[bid] = len(beat_ids)
                    beat_ids.append(bid)
                    if beat.get("must_preserve", True): must.add(bid)
            beat_set, coverage = set(beat_ids), Counter()

            shots = scene.get("shots") or []
            if not isinstance(shots, list):
                error(f"{scw}.shots: expected list")
                shots = []
            shot_by_id, shot_order = {}, []
            previous_id, previous_out = None, None

            for qi, shot in enumerate(shots, 1):
                sw = f"{scw}.shots[{qi}]"
                if not isinstance(shot, dict):
                    error(f"{sw}: expected object")
                    continue
                sid = shot.get("id")
                uid(sid, sw)
                sid = str(sid) if sid else None
                if sid:
                    shot_by_id[sid] = shot
                    shot_order.append(sid)
                if scene_id and shot.get("scene_id") not in (None, scene_id):
                    error(f"{sw}: scene_id does not match parent {scene_id!r}")

                src = shot.get("source_beats") or []
                indices = []
                for bid in src:
                    bid = str(bid); coverage[bid] += 1
                    if beat_set and bid not in beat_set:
                        error(f"{sw}: unknown source beat {bid}")
                    elif bid in beat_index:
                        indices.append(beat_index[bid])
                if len(indices) > 1 and not shot.get("nonlinear_exception"):
                    if indices != sorted(indices): error(f"{sw}: source_beats are out of scene order")
                    if indices and indices != list(range(indices[0], indices[-1] + 1)):
                        error(f"{sw}: source_beats are not contiguous")

                duration = number(shot.get("duration_seconds"))
                if duration is None or duration <= 0:
                    error(f"{sw}: duration_seconds must be > 0")
                    duration = 0.0
                episode_runtime += duration; project_runtime += duration

                tin, tout = number(shot.get("timecode_in")), number(shot.get("timecode_out"))
                if tin is not None and tout is not None and not close(tout - tin, duration):
                    error(f"{sw}: timecode_out - timecode_in != duration_seconds")
                if previous_out is not None and tin is not None and not close(previous_out, tin):
                    warn(f"{sw}: finished-cut timecode is not contiguous with previous shot")
                if tout is not None: previous_out = tout

                for key in ("start_state", "end_state", "shot_size", "camera_movement"):
                    if not shot.get(key): warn(f"{sw}: missing {key}")
                if version == "3.0":
                    for key in ("purpose", "cut_reason"):
                        if not shot.get(key): warn(f"{sw}: missing {key}")

                handoff = shot.get("handoff_from_previous")
                if qi > 1 and version == "3.0":
                    if not isinstance(handoff, dict):
                        warn(f"{sw}: missing handoff_from_previous")
                    else:
                        if handoff.get("type") not in HANDOFF_TYPES:
                            error(f"{sw}.handoff_from_previous: unsupported type {handoff.get('type')!r}")
                        if handoff.get("from_shot_id") != previous_id:
                            error(f"{sw}.handoff_from_previous.from_shot_id does not match previous shot {previous_id!r}")
                        if not handoff.get("reason"):
                            warn(f"{sw}.handoff_from_previous: missing reason")

                speech_load, overlap = 0.0, False
                for field in ("dialogue", "voiceover"):
                    lines = shot.get(field) or []
                    if not isinstance(lines, list):
                        error(f"{sw}.{field}: expected list")
                        continue
                    for li, line in enumerate(lines, 1):
                        lw = f"{sw}.{field}[{li}]"
                        if isinstance(line, str):
                            if version == "3.0": warn(f"{lw}: use object with language/timing")
                            continue
                        if not isinstance(line, dict):
                            error(f"{lw}: expected object or string")
                            continue
                        lang = line.get("language")
                        if version == "3.0" and not lang: warn(f"{lw}: missing language")
                        elif dialogue_lang and lang and str(lang) != str(dialogue_lang):
                            warn(f"{lw}: language differs from project.dialogue_language")
                        source = line.get("timing_source")
                        if source and source not in TIMING_SOURCES:
                            error(f"{lw}: unsupported timing_source {source!r}")
                        if translated and source == "inherited_source":
                            error(f"{lw}: inherited_source timing is invalid when project language changes")
                        timing = number(line.get("timing_seconds"))
                        if line.get("text") and timing is None: warn(f"{lw}: missing timing_seconds")
                        if timing is not None:
                            is_overlap = bool(line.get("overlap") or line.get("overlap_with_dialogue"))
                            overlap = overlap or is_overlap
                            if not is_overlap: speech_load += timing
                if speech_load > duration + 1e-6:
                    error(f"{sw}: dialogue/voiceover timing exceeds shot duration")
                elif duration and speech_load > duration * 0.88:
                    warn(f"{sw}: speech uses more than 88% of shot duration")
                if overlap: warn(f"{sw}: overlapping timed speech requires manual review")

                refs = shot.get("assets") or {}
                if isinstance(refs, dict):
                    if refs.get("scene") and asset_ids["scenes"] and str(refs["scene"]) not in asset_ids["scenes"]:
                        error(f"{sw}: unknown scene asset {refs['scene']}")
                    for kind in ("characters", "props"):
                        for aid in refs.get(kind) or []:
                            if asset_ids[kind] and str(aid) not in asset_ids[kind]:
                                error(f"{sw}: unknown {kind[:-1]} asset {aid}")
                previous_id = sid

            memberships = defaultdict(list)
            segments = scene.get("generation_segments") or []
            for gi, seg in enumerate(segments, 1):
                gw = f"{scw}.generation_segments[{gi}]"
                if not isinstance(seg, dict):
                    error(f"{gw}: expected object"); continue
                uid(seg.get("id"), gw)
                if version == "3.0" and "shots" in seg:
                    error(f"{gw}: v3 forbids embedded segment.shots; use scene.shots + segment.shot_ids")
                ids = seg.get("shot_ids") or []
                if not isinstance(ids, list): error(f"{gw}.shot_ids: expected list"); ids = []
                total, last_index = 0.0, None
                for sid in map(str, ids):
                    memberships[sid].append(seg.get("id"))
                    shot = shot_by_id.get(sid)
                    if not shot:
                        error(f"{gw}: unknown shot_id {sid}"); continue
                    total += number(shot.get("duration_seconds")) or 0.0
                    idx = shot_order.index(sid)
                    if last_index is not None and idx <= last_index: error(f"{gw}: shot_ids are not in scene order")
                    last_index = idx
                declared = number(seg.get("duration_seconds"))
                if ids and declared is not None and not close(declared, total):
                    error(f"{gw}: duration_seconds={declared:g} but referenced shots sum to {total:g}")

                model = str(seg.get("target_model") or project_model)
                if "minimax" in model.lower() and "h3" in model.lower():
                    if declared is not None and not (H3["min"] <= declared <= H3["max"]):
                        error(f"{gw}: MiniMax H3 duration {declared:g}s outside 4-15s")
                    refs = seg.get("reference_assets") or []
                    if len(refs) > H3["mixed"]: error(f"{gw}: H3 mixed references exceed 12")
                    counts = Counter(); totals = Counter(); labels = []
                    for ri, ref in enumerate(refs, 1):
                        if not isinstance(ref, dict): continue
                        label = str(ref.get("label") or ""); labels.append(label)
                        low = label.lower(); dur = number(ref.get("duration_seconds"))
                        if low.startswith(("picture", "image")): counts["image"] += 1
                        elif low.startswith("video"):
                            counts["video"] += 1
                            if dur is not None:
                                if not H3["ref_min"] <= dur <= H3["ref_max"]: error(f"{gw}: H3 video reference duration outside 2-15s")
                                totals["video"] += dur
                        elif low.startswith("audio"):
                            counts["audio"] += 1
                            if dur is not None:
                                if not H3["ref_min"] <= dur <= H3["ref_max"]: error(f"{gw}: H3 audio reference duration outside 2-15s")
                                totals["audio"] += dur
                    if counts["image"] > H3["images"]: error(f"{gw}: H3 image references exceed 9")
                    if counts["video"] > H3["videos"]: error(f"{gw}: H3 video references exceed 3")
                    if counts["audio"] > H3["audios"]: error(f"{gw}: H3 audio references exceed 3")
                    if totals["video"] > H3["video_total"]: error(f"{gw}: H3 total video reference duration exceeds 15s")
                    if totals["audio"] > H3["audio_total"]: error(f"{gw}: H3 total audio reference duration exceeds 15s")
                    labels = [x for x in labels if x]
                    if len(labels) != len(set(labels)): error(f"{gw}: duplicate reference labels")

            for sid, segs in memberships.items():
                if len(segs) > 1: error(f"{scw}: shot {sid} belongs to multiple generation segments {segs}")
            for bid in beat_ids:
                if bid in must and coverage[bid] == 0: error(f"{scw}: must-preserve beat not covered: {bid}")
                elif coverage[bid] > 1:
                    related = [s for s in shots if bid in (s.get("source_beats") or [])]
                    if not related or not all(s.get("coverage_exception") for s in related):
                        warn(f"{scw}: beat {bid} covered {coverage[bid]} times without coverage_exception")

        target = number(episode.get("target_runtime_seconds"))
        if target is not None and not close(target, episode_runtime):
            msg = f"{epw}: target_runtime_seconds={target:g} but canonical shots sum to {episode_runtime:g}"
            (error if episode.get("runtime_lock", project.get("runtime_lock", False)) else warn)(msg)

    target = number(project.get("target_runtime_seconds"))
    if target is not None and not close(target, project_runtime):
        msg = f"project: target_runtime_seconds={target:g} but canonical shots sum to {project_runtime:g}"
        (error if project.get("runtime_lock", False) else warn)(msg)
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate storyboard.json")
    parser.add_argument("file", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failure")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable report")
    args = parser.parse_args()
    try:
        data = json.loads(args.file.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 2
    errors, warnings = validate(data)
    if args.json:
        print(json.dumps({"errors": errors, "warnings": warnings, "summary": {
            "error_count": len(errors), "warning_count": len(warnings),
            "h3_rules_verified_at": H3_RULES_VERIFIED_AT}}, ensure_ascii=False, indent=2))
    else:
        for item in warnings: print(f"WARNING: {item}")
        for item in errors: print(f"ERROR: {item}")
        print(f"\nValidation summary: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors or (warnings and args.strict) else 0


if __name__ == "__main__":
    raise SystemExit(main())
