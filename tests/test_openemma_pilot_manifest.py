from __future__ import annotations

import json
import re
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "experiments/openemma_parity_pilot/manifest.json"
LOCK_PATH = ROOT / "upstreams/openemma.lock.json"
HASH_PATH = ROOT / "experiments/openemma_parity_pilot/manifest.sha256"


def load_strict_json(path: Path) -> dict:
    return json.loads(
        path.read_text(encoding="utf-8"),
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
    )


def test_pilot_manifest_is_strict_and_frozen() -> None:
    manifest = load_strict_json(MANIFEST_PATH)
    lock = load_strict_json(LOCK_PATH)

    assert manifest["status"] == "BLOCKED_PRE_INFERENCE"
    assert manifest["upstream"]["commit"] == lock["pinned_commit"]
    assert re.fullmatch(r"[0-9a-f]{40}", manifest["model"]["revision"])
    assert manifest["selection"]["uses_future_targets"] is False
    assert manifest["compute_gate"]["model_inference_authorized"] is False

    expected_hash = HASH_PATH.read_text(encoding="utf-8").split()[0]
    assert sha256(MANIFEST_PATH.read_bytes()).hexdigest() == expected_hash


def test_pilot_manifest_has_unique_representative_samples() -> None:
    manifest = load_strict_json(MANIFEST_PATH)
    samples = manifest["samples"]
    sample_ids = [sample["sample_id"] for sample in samples]
    regimes = {sample["regime"] for sample in samples}

    assert len(samples) == manifest["selection"]["expected_records"] == 6
    assert len(sample_ids) == len(set(sample_ids))
    assert regimes == {
        "decelerating",
        "near_stop",
        "straight_fast",
        "turn_left",
        "turn_right",
        "visually_nontrivial",
    }


def test_pilot_manifest_contains_no_absolute_or_future_target_inputs() -> None:
    manifest = load_strict_json(MANIFEST_PATH)
    serialized = json.dumps(manifest)

    assert "/data2t/" not in serialized
    assert "future_positions" not in serialized
    assert "future_headings" not in serialized
    assert "future_actions" not in serialized
    for sample in manifest["samples"]:
        assert all(not Path(path).is_absolute() for path in sample["observed_image_relpaths"])
        assert sample["official_qwen_image_relpaths"] == [
            sample["observed_image_relpaths"][-1]
        ]
