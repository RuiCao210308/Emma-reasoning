import pytest

from emma_reasoning.adapters.openemma import (
    OpenEmmaInvocation,
    OpenEmmaRawResult,
    UpstreamProvenance,
)


def _provenance() -> UpstreamProvenance:
    return UpstreamProvenance(
        name="openemma-official",
        commit="8403ea636696c5c10e8fdeca566410de0a07e449",
        checkout_clean=True,
        model_id="Qwen/Qwen2-VL-7B-Instruct",
        method="openemma",
        command=("python", "main.py"),
    )


def test_invocation_records_raw_upstream_inputs_without_future_target() -> None:
    invocation = OpenEmmaInvocation(
        run_id="run-1",
        sample_id="scene-0001:0000",
        image_paths=("frame0.jpg", "frame1.jpg"),
        observed_speeds_mps=(1.0, 2.0),
        observed_curvatures_inv_m=(0.0, 0.1),
        observed_timestamps_seconds=(0.0, 0.5),
        provenance=_provenance(),
        intervention={"type": "none"},
    )

    assert invocation.provenance.checkout_clean
    assert not hasattr(invocation, "future_positions_xy")


def test_invocation_rejects_misaligned_history() -> None:
    with pytest.raises(ValueError, match="must align"):
        OpenEmmaInvocation(
            run_id="run-1",
            sample_id="sample",
            image_paths=("frame.jpg",),
            observed_speeds_mps=(1.0, 2.0),
            observed_curvatures_inv_m=(0.0,),
            observed_timestamps_seconds=(0.0, 0.5),
            provenance=_provenance(),
        )


@pytest.mark.parametrize("timestamps", [(0.0,), (0.0, 0.5)])
def test_invocation_accepts_single_or_increasing_timestamps(
    timestamps: tuple[float, ...],
) -> None:
    length = len(timestamps)
    invocation = OpenEmmaInvocation(
        run_id="run-1",
        sample_id="sample",
        image_paths=("frame.jpg",),
        observed_speeds_mps=(1.0,) * length,
        observed_curvatures_inv_m=(0.0,) * length,
        observed_timestamps_seconds=timestamps,
        provenance=_provenance(),
    )

    assert invocation.observed_timestamps_seconds == timestamps


@pytest.mark.parametrize("timestamps", [(0.0, 0.0), (0.5, 0.0)])
def test_invocation_rejects_non_increasing_timestamps(
    timestamps: tuple[float, float],
) -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        OpenEmmaInvocation(
            run_id="run-1",
            sample_id="sample",
            image_paths=("frame0.jpg", "frame1.jpg"),
            observed_speeds_mps=(1.0, 2.0),
            observed_curvatures_inv_m=(0.0, 0.1),
            observed_timestamps_seconds=timestamps,
            provenance=_provenance(),
        )


@pytest.mark.parametrize("invalid_timestamp", [float("nan"), float("inf")])
def test_invocation_rejects_non_finite_timestamps(invalid_timestamp: float) -> None:
    with pytest.raises(ValueError, match="finite values"):
        OpenEmmaInvocation(
            run_id="run-1",
            sample_id="sample",
            image_paths=("frame0.jpg", "frame1.jpg"),
            observed_speeds_mps=(1.0, 2.0),
            observed_curvatures_inv_m=(0.0, 0.1),
            observed_timestamps_seconds=(0.0, invalid_timestamp),
            provenance=_provenance(),
        )


def test_successful_raw_result_requires_motion_text() -> None:
    with pytest.raises(ValueError, match="raw_motion_text"):
        OpenEmmaRawResult(
            run_id="run-1",
            sample_id="sample",
            raw_motion_text=None,
            scene_description=None,
            object_description=None,
            intent_description=None,
            prompts={},
            generation_metadata={},
        )


def test_failed_raw_result_preserves_error_without_fake_output() -> None:
    result = OpenEmmaRawResult(
        run_id="run-1",
        sample_id="sample",
        raw_motion_text=None,
        scene_description=None,
        object_description=None,
        intent_description=None,
        prompts={},
        generation_metadata={},
        error="CUDA out of memory",
    )
    assert result.error == "CUDA out of memory"
