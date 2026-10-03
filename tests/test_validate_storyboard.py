import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_storyboard.py"
EXAMPLE = ROOT / "examples" / "storyboard.example.json"

spec = importlib.util.spec_from_file_location("validate_storyboard", VALIDATOR)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class StoryboardValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_valid_v3_example(self):
        errors, warnings = validator.validate(copy.deepcopy(self.base))
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_translation_rejects_inherited_source_timing(self):
        data = copy.deepcopy(self.base)
        data["project"]["source_language"] = "zh-CN"
        data["project"]["output_language"] = "en-US"
        data["project"]["dialogue_language"] = "en-US"
        line = data["episodes"][0]["scenes"][0]["shots"][1]["dialogue"][0]
        line["language"] = "en-US"
        line["text"] = "You knew all along."
        line["timing_source"] = "inherited_source"
        errors, _ = validator.validate(data)
        self.assertTrue(any("inherited_source timing is invalid" in x for x in errors))

    def test_v3_forbids_embedded_segment_shots(self):
        data = copy.deepcopy(self.base)
        segment = data["episodes"][0]["scenes"][0]["generation_segments"][0]
        segment["shots"] = [copy.deepcopy(data["episodes"][0]["scenes"][0]["shots"][0])]
        errors, _ = validator.validate(data)
        self.assertTrue(any("v3 forbids embedded segment.shots" in x for x in errors))

    def test_h3_segment_duration_is_validated(self):
        data = copy.deepcopy(self.base)
        scene = data["episodes"][0]["scenes"][0]
        scene["shots"][0]["duration_seconds"] = 1.0
        scene["shots"][0]["timecode_out"] = 1.0
        scene["shots"][1]["timecode_in"] = 1.0
        scene["shots"][1]["timecode_out"] = 3.0
        scene["shots"][1]["duration_seconds"] = 2.0
        scene["generation_segments"][0]["duration_seconds"] = 3.0
        data["episodes"][0]["target_runtime_seconds"] = 3.0
        data["project"]["target_runtime_seconds"] = 3.0
        errors, _ = validator.validate(data)
        self.assertTrue(any("MiniMax H3 duration 3s outside 4-15s" in x for x in errors))

    def test_handoff_must_point_to_previous_shot(self):
        data = copy.deepcopy(self.base)
        handoff = data["episodes"][0]["scenes"][0]["shots"][1]["handoff_from_previous"]
        handoff["from_shot_id"] = "E01-S01-999"
        errors, _ = validator.validate(data)
        self.assertTrue(any("does not match previous shot" in x for x in errors))

    def test_combat_scene_requires_combat_plan(self):
        data = copy.deepcopy(self.base)
        scene = data["episodes"][0]["scenes"][0]
        scene["director_plan"]["sequence_type"] = "combat"
        errors, _ = validator.validate(data)
        self.assertTrue(any("sequence_type=combat requires combat_plan" in x for x in errors))

    def test_combat_context_continuity_is_validated(self):
        data = copy.deepcopy(self.base)
        scene = data["episodes"][0]["scenes"][0]
        scene["director_plan"]["sequence_type"] = "combat"
        scene["combat_plan"] = {
            "combat_goal": "C01 must get past C02.",
            "participants": [{"character_id": "C01"}, {"character_id": "C02"}],
            "arena": {
                "zones": [{"id": "Z1", "name": "door"}, {"id": "Z2", "name": "table"}]
            },
            "combat_beats": [
                {
                    "id": "E01-S01-CB01",
                    "type": "pressure",
                    "advantage_before": "C01",
                    "advantage_after": "C02",
                    "zone_before": "Z1",
                    "zone_after": "Z2",
                    "range_before": "mid",
                    "range_after": "close",
                    "visible_result": "C01 is forced toward the table.",
                    "source_beats": ["E01-S01-B01"]
                },
                {
                    "id": "E01-S01-CB02",
                    "type": "aftermath",
                    "advantage_before": "C02",
                    "advantage_after": "C02",
                    "zone_before": "Z2",
                    "zone_after": "Z2",
                    "range_before": "close",
                    "range_after": "close",
                    "source_beats": ["E01-S01-B02"]
                }
            ],
            "camera_strategy": "Wide establishes geography, then medium-close for the reversal.",
            "continuity_priorities": ["zone", "range", "advantage"]
        }
        scene["shots"][0]["combat_context"] = {
            "combat_beat_ids": ["E01-S01-CB01"],
            "action_phase": "reaction",
            "zone_start": "Z1",
            "zone_end": "Z2",
            "range_start": "mid",
            "range_end": "close",
            "advantage_start": "C01",
            "advantage_end": "C02"
        }
        scene["shots"][1]["combat_context"] = {
            "combat_beat_ids": ["E01-S01-CB02"],
            "action_phase": "aftermath",
            "zone_start": "Z1",
            "zone_end": "Z2",
            "range_start": "close",
            "range_end": "close",
            "advantage_start": "C02",
            "advantage_end": "C02"
        }
        errors, _ = validator.validate(data)
        self.assertTrue(any("zone_start='Z1' does not continue previous zone_end='Z2'" in x for x in errors))

    def test_v32_requires_sequence_type(self):
        data = copy.deepcopy(self.base)
        scene = data["episodes"][0]["scenes"][0]
        scene["director_plan"].pop("sequence_type", None)
        errors, _ = validator.validate(data)
        self.assertTrue(any("missing sequence_type" in x for x in errors))

    def test_v32_requires_matching_sequence_plan(self):
        data = copy.deepcopy(self.base)
        scene = data["episodes"][0]["scenes"][0]
        scene["sequence_plan"]["profile"] = "dialogue"
        errors, _ = validator.validate(data)
        self.assertTrue(any("does not match sequence_type" in x for x in errors))

    def test_sequence_beat_must_be_covered(self):
        data = copy.deepcopy(self.base)
        scene = data["episodes"][0]["scenes"][0]
        scene["shots"][1].pop("sequence_context", None)
        errors, _ = validator.validate(data)
        self.assertTrue(any("sequence beat not covered by any shot" in x for x in errors))

    def test_sequence_context_state_continuity(self):
        data = copy.deepcopy(self.base)
        scene = data["episodes"][0]["scenes"][0]
        scene["shots"][1]["sequence_context"]["state_start"]["evidence_state"] = "hidden"
        errors, _ = validator.validate(data)
        self.assertTrue(any("does not continue previous state_end" in x for x in errors))


if __name__ == "__main__":
    unittest.main()
