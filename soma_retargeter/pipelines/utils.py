# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from enum import IntEnum, auto

import soma_retargeter.utils.io_utils as io_utils
import soma_retargeter.assets.usd as usd_utils

from soma_retargeter.robotics.robot_registry import RobotSpec


class SourceType(IntEnum):
    """Enumeration of supported source model types."""
    SOMA = auto()


_SOURCE_TYPE_TO_STR = {
    SourceType.SOMA : "soma"
}
_STR_TO_SOURCE_TYPE = {s : t for t, s in _SOURCE_TYPE_TO_STR.items()}


def get_source_str_from_type(source: SourceType) -> str:
    """
    Get the string name associated with a given source type.

    Args:
        source (SourceType): The source type enum value.

    Returns:
        str: The string representation of the source type.
    """
    return _SOURCE_TYPE_TO_STR[source]


def get_source_type_from_str(source: str) -> SourceType:
    """
    Convert a string to its corresponding SourceType enum value.

    Args:
        source (str): The string representation of a source.

    Returns:
        SourceType: The corresponding source type enum.

    Raises:
        ValueError: If the provided string does not correspond to a valid source type.
    """
    try:
        return _STR_TO_SOURCE_TYPE[source]
    except KeyError:
        allowed = ", ".join(_STR_TO_SOURCE_TYPE.keys())
        raise ValueError(f"Unknown source type: [{source}]. Allowed values: {allowed}") from None


def get_source_model_mesh(source: SourceType, skeleton) -> dict:
    """
    Retrieve model mesh for a given source type.

    Args:
        source (SourceType): The source type for which properties should be retrieved.
        skeleton: The skeleton associated with the source model, used for loading the mesh.

    Returns:
        SkeletalMesh: The skeleton mesh for the given source type.

    Raises:
        ValueError: If the source type is not recognized.
    """
    if source == SourceType.SOMA:
        return usd_utils.load_skeletal_mesh_from_usd(
            str(io_utils.get_config_file('soma', 'soma_base_skel_minimal.usd')),
            skeleton,
            '/OUTPUT/c_geometry_grp',
            '/OUTPUT/c_skeleton_grp/Root')

    raise ValueError(f"Unknown source type {source}.")


def get_retargeter_config(source: SourceType, robot_spec: RobotSpec) -> dict:
    """
    Load the retargeter configuration between a specific source and target robot.

    Args:
        source (SourceType): The source type.
        robot_spec (RobotSpec): The target robot specification.

    Returns:
        dict: The loaded JSON configuration for the retargeter.

    Raises:
        ValueError: If the robot has no retargeter config registered for the source type.
    """
    source_name = get_source_str_from_type(source)
    try:
        filename = robot_spec.retargeter_configs[source_name]
    except KeyError:
        raise ValueError(f"Unknown source type [{source_name}] for target [{robot_spec.name}].") from None

    return io_utils.load_json(
        io_utils.get_config_file(robot_spec.config_dir, filename)
    )
