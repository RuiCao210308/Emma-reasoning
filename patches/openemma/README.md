# OpenEMMA patches

This directory is intentionally empty until a parity audit proves that an upstream patch is unavoidable.

Any patch added here must include:

- the pinned upstream commit it applies to;
- the exact problem it fixes;
- a minimal diff;
- a test that fails before and passes after the patch;
- evidence that unrelated upstream behavior is unchanged;
- an experiment manifest field identifying the patch.

Do not edit `third_party/OpenEMMA` and then run a paper experiment from the dirty checkout.
