# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

import newton

from soma_retargeter.assets.csv import (
    AISapiens23DOF_CSVConfig,
    BoosterT1_23DOF_CSVConfig,
    RobotCSVConfig,
    UnitreeG129DOF_CSVConfig,
    UnitreeH1_2_27DOF_CSVConfig,
    UnitreeR1_24DOF_CSVConfig,
    BoosterT1_29DOF_CSVConfig,
)


def _create_ai_sapiens_builder() -> "newton.ModelBuilder":
    # Lazy import: resolution may regenerate the MJCF, which pulls in mujoco.
    import soma_retargeter.assets.ai_sapiens as ai_sapiens_assets

    builder = newton.ModelBuilder()
    builder.add_mjcf(ai_sapiens_assets.resolve_ai_sapiens_mjcf_path())
    return builder


@dataclass(frozen=True)
class RobotSpec:
    """
    Description of a target robot supported by the retargeting pipeline.

    A RobotSpec bundles everything that is specific to one robot: where its
    simulation model lives, which retargeter/scaler/feet-stabilizer configs to
    use, and how its motion CSV files are formatted. Adding support for a new
    robot means registering one RobotSpec plus its config files under
    ``soma_retargeter/configs/<config_dir>/`` — no pipeline code changes.
    """
    name: str
    """Robot type name used in configs and CLI options (e.g. "unitree_g1")."""

    asset_folder: str
    """Local directory containing the robot model, or the name of a folder in
    the newton-assets repository to download when no local copy exists."""

    model_file: str
    """Path of the robot model file relative to ``asset_folder``
    (e.g. "mjcf/g1_29dof_rev_1_0.xml"). MJCF (.xml) and URDF (.urdf) are supported."""

    config_dir: str
    """Directory under ``soma_retargeter/configs/`` holding this robot's config files."""

    retargeter_configs: Dict[str, str]
    """Maps a source skeleton type name (e.g. "soma") to the retargeter config
    filename inside ``config_dir``."""

    csv_config: RobotCSVConfig = field(compare=False)
    """CSV format definition for this robot's motion files. The header/DOF order
    must match the joint order of the robot model file, which is the layout
    Newton uses for ``joint_q``."""

    builder_factory: Optional[Callable[[], "newton.ModelBuilder"]] = field(default=None, compare=False)
    """Optional custom factory used instead of the default asset resolution in
    ``create_builder`` (e.g. AI Sapiens resolves its MJCF through env/config
    overrides and on-demand generation)."""

    def resolve_asset_root(self) -> Path:
        """
        Return the directory containing ``model_file``.

        A local ``asset_folder`` that already contains ``model_file`` is used
        as-is; otherwise ``asset_folder`` is treated as a folder name in the
        newton-assets repository and downloaded into the newton cache.
        """
        local_root = Path(self.asset_folder)
        if (local_root / self.model_file).exists():
            return local_root

        return newton.utils.download_asset(self.asset_folder)

    def create_builder(self) -> newton.ModelBuilder:
        """
        Create a ``newton.ModelBuilder`` with this robot's model loaded.

        Returns:
            newton.ModelBuilder: Builder containing the robot articulation.

        Raises:
            ValueError: If the model file extension is not supported.
        """
        if self.builder_factory is not None:
            return self.builder_factory()

        model_path = self.resolve_asset_root() / self.model_file

        builder = newton.ModelBuilder()
        suffix = model_path.suffix.lower()
        if suffix == ".xml":
            builder.add_mjcf(model_path)
        elif suffix == ".urdf":
            builder.add_urdf(model_path)
        else:
            raise ValueError(
                f"Unsupported robot model format [{suffix}] for robot [{self.name}]. "
                "Supported formats: .xml (MJCF), .urdf (URDF).")

        return builder


_ROBOT_REGISTRY: Dict[str, RobotSpec] = {
    "unitree_g1": RobotSpec(
        name="unitree_g1",
        asset_folder="unitree_g1",
        model_file="mjcf/g1_29dof_rev_1_0.xml",
        config_dir="unitree_g1",
        retargeter_configs={"soma": "soma_to_g1_retargeter_config.json"},
        csv_config=UnitreeG129DOF_CSVConfig(),
    ),
    "unitree_h1_2": RobotSpec(
        name="unitree_h1_2",
        asset_folder="assets/robots/unitree_h1_2",
        model_file="mjcf/h1_2_handless.xml",
        config_dir="unitree_h1_2",
        retargeter_configs={"soma": "soma_to_h1_2_retargeter_config.json"},
        csv_config=UnitreeH1_2_27DOF_CSVConfig(),
    ),
    "unitree_r1": RobotSpec(
        name="unitree_r1",
        asset_folder="assets/robots/unitree_r1",
        model_file="mjcf/r1_24dof.xml",
        config_dir="unitree_r1",
        retargeter_configs={"soma": "soma_to_r1_retargeter_config.json"},
        csv_config=UnitreeR1_24DOF_CSVConfig(),
    ),
    "booster_t1_29dof": RobotSpec(
        name="booster_t1_29dof",
        asset_folder="assets/robots/booster_t1_29dof",
        model_file="mjcf/t1_29dof.xml",
        config_dir="booster_t1_29dof",
        retargeter_configs={"soma": "soma_to_t1_29dof_retargeter_config.json"},
        csv_config=BoosterT1_29DOF_CSVConfig(),
    ),
    "booster_t1": RobotSpec(
        name="booster_t1",
        asset_folder="assets/robots/booster_t1",
        model_file="mjcf/t1_serial.xml",
        config_dir="booster_t1",
        retargeter_configs={"soma": "soma_to_t1_retargeter_config.json"},
        csv_config=BoosterT1_23DOF_CSVConfig(),
    ),
    "ai_sapiens": RobotSpec(
        name="ai_sapiens",
        asset_folder="soma_retargeter/configs/ai_sapiens",
        model_file="ai_sapiens_retarget.xml",
        config_dir="ai_sapiens",
        retargeter_configs={"soma": "soma_to_ai_sapiens_retargeter_config.json"},
        csv_config=AISapiens23DOF_CSVConfig(),
        builder_factory=_create_ai_sapiens_builder,
    ),
}


def robot_names() -> List[str]:
    """Return the names of all registered target robots."""
    return list(_ROBOT_REGISTRY.keys())


def get_robot_spec(name: str) -> RobotSpec:
    """
    Look up the RobotSpec registered under the given robot type name.

    Args:
        name (str): The robot type name (e.g. "unitree_g1").

    Returns:
        RobotSpec: The registered robot specification.

    Raises:
        ValueError: If no robot is registered under the given name.
    """
    try:
        return _ROBOT_REGISTRY[name]
    except KeyError:
        allowed = ", ".join(_ROBOT_REGISTRY.keys())
        raise ValueError(f"Unknown robot type: [{name}]. Allowed values: {allowed}") from None


def register_robot(spec: RobotSpec) -> None:
    """
    Register a new target robot.

    Args:
        spec (RobotSpec): The robot specification to register.

    Raises:
        ValueError: If a robot is already registered under ``spec.name``.
    """
    if spec.name in _ROBOT_REGISTRY:
        raise ValueError(f"Robot type [{spec.name}] is already registered.")

    _ROBOT_REGISTRY[spec.name] = spec
