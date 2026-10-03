#!/usr/bin/env python3
"""Deterministic validator for script-to-storyboard-table schema v4."""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

VALID_MODES = {"faithful", "visual", "pacing", "story"}
SEQUENCE_TYPES = {
    "dialogue", "confrontation_negotiation", "emotional_intimacy",
    "investigation_reveal", "suspense_threat", "horror_dread",
    "stealth_infiltration", "chase_escape", "combat",
    "physical_hazard_rescue", "vehicle_action", "disaster_survival",
    "crowd_ensemble", "comedy", "montage_progression",
    "performance_ritual", "world_reveal_establishing",
    "transition_travel", "other",
}
HANDOFF_TYPES = {
    "direct", "match_on_action", "eyeline", "reaction", "insert",
    "insert_return", "sound_bridge", "reframe", "motivated_jump",
    "time_jump", "scene_cut",
}
TIMING_SOURCES = {
    "measured_audio", "measured_tts", "scripted", "estimated_target_text",
    "estimated", "inherited_source",
}
COMBAT_TYPES = {
    "engage", "pressure", "reversal", "disarm_or_prop_change",
    "environment_shift", "separation", "reengage", "escalation",
    "save_or_interrupt", "finish", "aftermath",
}
COMBAT_RANGES = {"far", "mid", "close", "grapple"}
COMBAT_PHASES = {
    "read_or_intent", "approach", "attack_attempt", "evade_or_block",
    "impact_or_near_impact", "reaction", "recovery_or_reposition",
    "aftermath",
}
ACTION_PHASES = (
    "prepare", "approach", "contact", "execution",
    "result", "reaction", "recovery", "aftermath",
)
ACTION_PHASE_ORDER = {name: index for index, name in enumerate(ACTION_PHASES)}
CONTINUITY_JUMP_TYPES = {"motivated_jump", "time_jump", "scene_cut"}
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


_MISSING = object()


def nested_get(mapping, path):
    """Read a dot-separated path from a nested mapping without guessing."""
    current = mapping
    for part in str(path).split("."):
        if not isinstance(current, dict) or part not in current:
            return _MISSING
        current = current[part]
    return current


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
    strict_sequence_schema = version in {"3.2", "4.0"}
    strict_continuity_schema = version == "4.0"
    if version not in {"3.0", "3.2", "4.0"}:
        warn(f"root: schema_version {version!r}; validator is optimized for 4.0")

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

            is_combat = False
            sequence_type = None
            sequence_ids = set()
            sequence_beats_data = []
            sequence_coverage = Counter()
            combat_ids = set()
            combat_zones = set()
            combat_beats_data = []
            combat_coverage = Counter()

            if version in {"3.0", "3.2", "4.0"}:
                plan = scene.get("director_plan")
                if not isinstance(plan, dict):
                    warn(f"{scw}: missing director_plan")
                else:
                    for key in ("dramatic_job", "turn", "blocking_plan"):
                        if not plan.get(key): warn(f"{scw}.director_plan: missing {key}")
                    if not plan.get("coverage_obligations"):
                        warn(f"{scw}.director_plan: no coverage_obligations")
                    sequence_type = plan.get("sequence_type")
                    if strict_sequence_schema and not sequence_type:
                        error(f"{scw}.director_plan: missing sequence_type")
                    if sequence_type and sequence_type not in SEQUENCE_TYPES:
                        error(f"{scw}.director_plan: unsupported sequence_type {sequence_type!r}")
                    is_combat = sequence_type == "combat"

                if strict_sequence_schema and sequence_type and not is_combat:
                    sequence_plan = scene.get("sequence_plan")
                    if not isinstance(sequence_plan, dict):
                        error(f"{scw}: sequence_type={sequence_type} requires sequence_plan")
                    else:
                        if sequence_plan.get("profile") != sequence_type:
                            error(
                                f"{scw}.sequence_plan.profile {sequence_plan.get('profile')!r} "
                                f"does not match sequence_type {sequence_type!r}"
                            )
                        for key in ("sequence_goal", "rhythm_plan", "camera_strategy", "continuity_priorities"):
                            if not sequence_plan.get(key):
                                warn(f"{scw}.sequence_plan: missing {key}")
                        sqbeats = sequence_plan.get("sequence_beats") or []
                        if not isinstance(sqbeats, list) or not sqbeats:
                            error(f"{scw}.sequence_plan: sequence_beats must be a non-empty list")
                            sqbeats = []
                        for sqi, sqbeat in enumerate(sqbeats, 1):
                            sqw = f"{scw}.sequence_plan.sequence_beats[{sqi}]"
                            if not isinstance(sqbeat, dict):
                                error(f"{sqw}: expected object")
                                continue
                            sqid = sqbeat.get("id")
                            uid(sqid, sqw)
                            if sqid:
                                sequence_ids.add(str(sqid))
                            if not sqbeat.get("purpose"):
                                warn(f"{sqw}: missing purpose")
                            if not sqbeat.get("visible_change"):
                                warn(f"{sqw}: missing visible_change")
                            sequence_beats_data.append((sqw, sqbeat))

                if is_combat:
                    combat = scene.get("combat_plan")
                    if not isinstance(combat, dict):
                        error(f"{scw}: sequence_type=combat requires combat_plan")
                    else:
                        if not combat.get("combat_goal"):
                            error(f"{scw}.combat_plan: missing combat_goal")
                        if not combat.get("participants"):
                            warn(f"{scw}.combat_plan: no participants")
                        arena = combat.get("arena") or {}
                        zones = arena.get("zones") or [] if isinstance(arena, dict) else []
                        local_zone_ids = []
                        for zi, zone in enumerate(zones, 1):
                            zw = f"{scw}.combat_plan.arena.zones[{zi}]"
                            zid = zone.get("id") if isinstance(zone, dict) else zone
                            if not zid:
                                error(f"{zw}: missing zone id")
                            else:
                                zid = str(zid)
                                if zid in local_zone_ids:
                                    error(f"{zw}: duplicate local zone id {zid}")
                                local_zone_ids.append(zid)
                                combat_zones.add(zid)
                        if not combat_zones:
                            error(f"{scw}.combat_plan: arena.zones must not be empty")

                        cbeats = combat.get("combat_beats") or []
                        if not isinstance(cbeats, list) or not cbeats:
                            error(f"{scw}.combat_plan: combat_beats must be a non-empty list")
                            cbeats = []
                        has_aftermath = False
                        for ci, cbeat in enumerate(cbeats, 1):
                            cw = f"{scw}.combat_plan.combat_beats[{ci}]"
                            if not isinstance(cbeat, dict):
                                error(f"{cw}: expected object")
                                continue
                            cbid = cbeat.get("id")
                            uid(cbid, cw)
                            if cbid:
                                combat_ids.add(str(cbid))
                            ctype = cbeat.get("type")
                            if ctype not in COMBAT_TYPES:
                                error(f"{cw}: unsupported combat beat type {ctype!r}")
                            has_aftermath = has_aftermath or ctype == "aftermath"
                            for key in ("range_before", "range_after"):
                                value = cbeat.get(key)
                                if value is not None and value not in COMBAT_RANGES:
                                    error(f"{cw}.{key}: unsupported range {value!r}")
                            for key in ("zone_before", "zone_after"):
                                value = cbeat.get(key)
                                if value is not None and combat_zones and str(value) not in combat_zones:
                                    error(f"{cw}.{key}: unknown combat zone {value!r}")
                            for key in ("advantage_before", "advantage_after"):
                                if not cbeat.get(key):
                                    warn(f"{cw}: missing {key}")
                            if ctype != "aftermath" and not cbeat.get("visible_result"):
                                warn(f"{cw}: missing visible_result")
                            combat_beats_data.append((cw, cbeat))
                        if not has_aftermath:
                            warn(f"{scw}.combat_plan: no aftermath combat beat")
                        if not combat.get("camera_strategy"):
                            warn(f"{scw}.combat_plan: missing camera_strategy")
                        if not combat.get("continuity_priorities"):
                            warn(f"{scw}.combat_plan: no continuity_priorities")

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

            if strict_sequence_schema and sequence_type and not is_combat:
                for sqw, sqbeat in sequence_beats_data:
                    for bid in sqbeat.get("source_beats") or []:
                        if beat_set and str(bid) not in beat_set:
                            error(f"{sqw}: unknown source beat {bid}")

            if is_combat:
                for cw, cbeat in combat_beats_data:
                    for bid in cbeat.get("source_beats") or []:
                        if beat_set and str(bid) not in beat_set:
                            error(f"{cw}: unknown source beat {bid}")

            shots = scene.get("shots") or []
            if not isinstance(shots, list):
                error(f"{scw}.shots: expected list")
                shots = []
            shot_by_id, shot_order = {}, []
            previous_id, previous_out = None, None
            previous_shot = None
            previous_sequence_context = None
            previous_combat_context = None

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
                if strict_continuity_schema:
                    for key in ("start_state", "end_state"):
                        if not isinstance(shot.get(key), dict):
                            error(f"{sw}.{key}: v4 requires an object for machine-readable continuity")
                if version in {"3.0", "3.2", "4.0"}:
                    for key in ("purpose", "cut_reason"):
                        if not shot.get(key): warn(f"{sw}: missing {key}")

                sequence_context = shot.get("sequence_context")
                if strict_sequence_schema and sequence_type and not is_combat:
                    if not isinstance(sequence_context, dict):
                        warn(f"{sw}: missing sequence_context")
                        sequence_context = None
                    else:
                        sqids = sequence_context.get("sequence_beat_ids") or []
                        if not sqids:
                            warn(f"{sw}.sequence_context: no sequence_beat_ids")
                        for sqid in map(str, sqids):
                            sequence_coverage[sqid] += 1
                            if sequence_ids and sqid not in sequence_ids:
                                error(f"{sw}.sequence_context: unknown sequence beat {sqid}")
                        if not isinstance(sequence_context.get("state_start"), dict):
                            warn(f"{sw}.sequence_context: missing state_start")
                        if not isinstance(sequence_context.get("state_end"), dict):
                            warn(f"{sw}.sequence_context: missing state_end")

                combat_context = shot.get("combat_context")
                if is_combat and combat_context is not None:
                    if not isinstance(combat_context, dict):
                        error(f"{sw}.combat_context: expected object")
                        combat_context = None
                    else:
                        cbids = combat_context.get("combat_beat_ids") or []
                        if not cbids:
                            warn(f"{sw}.combat_context: no combat_beat_ids")
                        for cbid in map(str, cbids):
                            combat_coverage[cbid] += 1
                            if combat_ids and cbid not in combat_ids:
                                error(f"{sw}.combat_context: unknown combat beat {cbid}")
                        phase = combat_context.get("action_phase")
                        if phase is not None and phase not in COMBAT_PHASES:
                            error(f"{sw}.combat_context.action_phase: unsupported value {phase!r}")
                        for key in ("range_start", "range_end"):
                            value = combat_context.get(key)
                            if value is not None and value not in COMBAT_RANGES:
                                error(f"{sw}.combat_context.{key}: unsupported range {value!r}")
                        for key in ("zone_start", "zone_end"):
                            value = combat_context.get(key)
                            if value is not None and combat_zones and str(value) not in combat_zones:
                                error(f"{sw}.combat_context.{key}: unknown combat zone {value!r}")

                handoff = shot.get("handoff_from_previous")
                if qi > 1 and version in {"3.0", "3.2", "4.0"}:
                    if not isinstance(handoff, dict):
                        (error if strict_continuity_schema else warn)(f"{sw}: missing handoff_from_previous")
                    else:
                        handoff_type = handoff.get("type")
                        if handoff_type not in HANDOFF_TYPES:
                            error(f"{sw}.handoff_from_previous: unsupported type {handoff_type!r}")
                        if handoff.get("from_shot_id") != previous_id:
                            error(f"{sw}.handoff_from_previous.from_shot_id does not match previous shot {previous_id!r}")
                        if not handoff.get("reason"):
                            warn(f"{sw}.handoff_from_previous: missing reason")

                        if strict_continuity_schema:
                            inheritance = handoff.get("state_inheritance")
                            if handoff_type not in CONTINUITY_JUMP_TYPES:
                                if not isinstance(inheritance, list) or not inheritance:
                                    error(
                                        f"{sw}.handoff_from_previous: v4 requires non-empty "
                                        "state_inheritance for continuous cuts"
                                    )
                                elif isinstance(previous_shot, dict):
                                    prev_end = previous_shot.get("end_state")
                                    cur_start = shot.get("start_state")
                                    if isinstance(prev_end, dict) and isinstance(cur_start, dict):
                                        seen_paths = set()
                                        for pi, path in enumerate(inheritance, 1):
                                            pw = f"{sw}.handoff_from_previous.state_inheritance[{pi}]"
                                            if not isinstance(path, str) or not path.strip():
                                                error(f"{pw}: expected non-empty dot path")
                                                continue
                                            path = path.strip()
                                            if path in seen_paths:
                                                warn(f"{pw}: duplicate path {path!r}")
                                            seen_paths.add(path)
                                            prev_value = nested_get(prev_end, path)
                                            cur_value = nested_get(cur_start, path)
                                            if prev_value is _MISSING:
                                                error(f"{pw}: path {path!r} missing from previous end_state")
                                            if cur_value is _MISSING:
                                                error(f"{pw}: path {path!r} missing from current start_state")
                                            if (
                                                prev_value is not _MISSING
                                                and cur_value is not _MISSING
                                                and prev_value != cur_value
                                            ):
                                                error(
                                                    f"{pw}: {path!r}={cur_value!r} does not continue "
                                                    f"previous end_state value {prev_value!r}"
                                                )
                            elif inheritance is not None and not isinstance(inheritance, list):
                                error(f"{sw}.handoff_from_previous.state_inheritance: expected list")

                action_state = shot.get("action_state")
                if action_state is not None:
                    if not isinstance(action_state, dict):
                        error(f"{sw}.action_state: expected object")
                        action_state = None
                    else:
                        action_id = action_state.get("action_id")
                        phase_start = action_state.get("phase_start")
                        phase_end = action_state.get("phase_end")
                        if not action_id:
                            error(f"{sw}.action_state: missing action_id")
                        for key, value in (("phase_start", phase_start), ("phase_end", phase_end)):
                            if value not in ACTION_PHASE_ORDER:
                                error(f"{sw}.action_state.{key}: unsupported phase {value!r}")
                        if phase_start in ACTION_PHASE_ORDER and phase_end in ACTION_PHASE_ORDER:
                            if ACTION_PHASE_ORDER[phase_start] > ACTION_PHASE_ORDER[phase_end]:
                                error(f"{sw}.action_state: phase_end occurs before phase_start")

                if (
                    strict_continuity_schema
                    and qi > 1
                    and isinstance(previous_shot, dict)
                    and isinstance(handoff, dict)
                ):
                    prev_action = previous_shot.get("action_state")
                    current_action = action_state if isinstance(action_state, dict) else None
                    handoff_type = handoff.get("type")
                    if handoff_type == "match_on_action":
                        if not isinstance(prev_action, dict) or not isinstance(current_action, dict):
                            error(f"{sw}: match_on_action requires action_state on both adjacent shots")
                        elif prev_action.get("action_id") != current_action.get("action_id"):
                            error(
                                f"{sw}: match_on_action must continue the same action_id; "
                                f"got {prev_action.get('action_id')!r} -> {current_action.get('action_id')!r}"
                            )
                    if (
                        isinstance(prev_action, dict)
                        and isinstance(current_action, dict)
                        and prev_action.get("action_id")
                        and prev_action.get("action_id") == current_action.get("action_id")
                        and handoff_type not in CONTINUITY_JUMP_TYPES
                    ):
                        prev_phase = prev_action.get("phase_end")
                        cur_phase = current_action.get("phase_start")
                        if prev_phase in ACTION_PHASE_ORDER and cur_phase in ACTION_PHASE_ORDER:
                            delta = ACTION_PHASE_ORDER[cur_phase] - ACTION_PHASE_ORDER[prev_phase]
                            if delta < 0:
                                error(
                                    f"{sw}.action_state: phase_start {cur_phase!r} moves backward "
                                    f"from previous phase_end {prev_phase!r}"
                                )
                            elif delta > 1:
                                warn(
                                    f"{sw}.action_state: action {current_action.get('action_id')!r} "
                                    f"skips phases from {prev_phase!r} to {cur_phase!r}; "
                                    "use a motivated_jump or add the missing action phase"
                                )

                speech_load, overlap = 0.0, False
                for field in ("dialogue", "voiceover"):
                    lines = shot.get(field) or []
                    if not isinstance(lines, list):
                        error(f"{sw}.{field}: expected list")
                        continue
                    for li, line in enumerate(lines, 1):
                        lw = f"{sw}.{field}[{li}]"
                        if isinstance(line, str):
                            if version in {"3.0", "3.2", "4.0"}: warn(f"{lw}: use object with language/timing")
                            continue
                        if not isinstance(line, dict):
                            error(f"{lw}: expected object or string")
                            continue
                        lang = line.get("language")
                        if version in {"3.0", "3.2", "4.0"} and not lang: warn(f"{lw}: missing language")
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
                if (
                    strict_sequence_schema
                    and sequence_type
                    and not is_combat
                    and isinstance(sequence_context, dict)
                    and isinstance(previous_sequence_context, dict)
                ):
                    handoff_type = (handoff or {}).get("type") if isinstance(handoff, dict) else None
                    allow_jump = handoff_type in {"motivated_jump", "time_jump", "scene_cut"}
                    if not allow_jump:
                        prev_state = previous_sequence_context.get("state_end") or {}
                        cur_state = sequence_context.get("state_start") or {}
                        if isinstance(prev_state, dict) and isinstance(cur_state, dict):
                            for key in sorted(set(prev_state) & set(cur_state)):
                                if prev_state[key] != cur_state[key]:
                                    error(
                                        f"{sw}.sequence_context: state_start[{key!r}]={cur_state[key]!r} "
                                        f"does not continue previous state_end={prev_state[key]!r}"
                                    )
                previous_sequence_context = (
                    sequence_context if isinstance(sequence_context, dict) else None
                )

                if is_combat and isinstance(combat_context, dict) and isinstance(previous_combat_context, dict):
                    handoff_type = (handoff or {}).get("type") if isinstance(handoff, dict) else None
                    allow_jump = handoff_type in {"motivated_jump", "time_jump", "scene_cut"}
                    if not allow_jump:
                        pairs = (
                            ("zone_end", "zone_start"),
                            ("range_end", "range_start"),
                            ("advantage_end", "advantage_start"),
                        )
                        for prev_key, cur_key in pairs:
                            prev_value = previous_combat_context.get(prev_key)
                            cur_value = combat_context.get(cur_key)
                            if prev_value is not None and cur_value is not None and str(prev_value) != str(cur_value):
                                error(
                                    f"{sw}.combat_context: {cur_key}={cur_value!r} "
                                    f"does not continue previous {prev_key}={prev_value!r}"
                                )
                previous_combat_context = combat_context if isinstance(combat_context, dict) else None
                previous_shot = shot
                previous_id = sid

            memberships = defaultdict(list)
            segments = scene.get("generation_segments") or []
            for gi, seg in enumerate(segments, 1):
                gw = f"{scw}.generation_segments[{gi}]"
                if not isinstance(seg, dict):
                    error(f"{gw}: expected object"); continue
                uid(seg.get("id"), gw)
                if version in {"3.0", "3.2", "4.0"} and "shots" in seg:
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

                if is_combat:
                    segment_combat_beats = set()
                    for sid in map(str, ids):
                        shot = shot_by_id.get(sid) or {}
                        context = shot.get("combat_context") or {}
                        if isinstance(context, dict):
                            segment_combat_beats.update(map(str, context.get("combat_beat_ids") or []))
                    if len(segment_combat_beats) > 2:
                        warn(
                            f"{gw}: combat segment spans {len(segment_combat_beats)} combat beats; "
                            "review AI generation complexity"
                        )

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

            if strict_sequence_schema and sequence_type and not is_combat:
                for sqid in sorted(sequence_ids):
                    if sequence_coverage[sqid] == 0:
                        error(f"{scw}: sequence beat not covered by any shot: {sqid}")
            if is_combat:
                for cbid in sorted(combat_ids):
                    if combat_coverage[cbid] == 0:
                        error(f"{scw}: combat beat not covered by any shot: {cbid}")

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
