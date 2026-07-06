# Pinned G1 model (reference only — NOT wired into the pipeline)

`mjcf/g1_29dof_rev_1_0.xml` + `meshes/` is a byte-identical local copy of the exact
model the G1 pipeline loads at runtime.

**The code does not read this copy.** G1 is special-cased in
`soma_retargeter/pipelines/newton_pipeline.py` and `feet_stabilizer.py` to fetch the
model on demand via `newton.utils.download_asset("unitree_g1")` — unlike the other
robots (r1/t1/h1_2/k1), whose configs point at a local MJCF through a `robot_mjcf`
field. The G1 retargeter config has no `robot_mjcf` field, so this directory is
deliberately left unreferenced. It exists only to pin the model for reproducibility
and offline inspection.

## Provenance
- Source: Newton asset `unitree_g1`, cache revision `308a72cd`
  (`~/.cache/newton/newton-assets_unitree_g1_308a72cd/unitree_g1/mjcf/g1_29dof_rev_1_0.xml`)
- newton 1.0.0 (soma-retargeter `.venv`, py3.12)
- Contents: the one loaded MJCF + the 35 STL meshes it references (`meshdir="../meshes"`
  preserved, hence the `mjcf/` + `meshes/` layout). The upstream asset ships ~119 more
  meshes for hand/other variants that this model does not use — those are omitted.

## To actually wire it (if ever desired)
Add `"robot_mjcf": "unitree_g1/robot/mjcf/g1_29dof_rev_1_0.xml"` to
`soma_to_g1_retargeter_config.json`, and drop the `target_type == UNITREE_G1`
special-case branches so G1 falls through to the generic local-MJCF path.
