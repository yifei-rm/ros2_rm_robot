"""Unified component-level bringup for all supported RealMan arms."""

import os
import re

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}

_ARM_TYPE_ALIASES = {
    "63": "63",
    "rm63": "63",
    "63iii": "63_iii",
    "rm63iii": "63_iii",
    "65": "65",
    "rm65": "65",
    "75": "75",
    "rm75": "75",
    "eco62": "eco62",
    "rmeco62": "eco62",
    "eco63": "eco63",
    "rmeco63": "eco63",
    "eco65": "eco65",
    "rmeco65": "eco65",
    "gen72": "gen72",
    "rmgen72": "gen72",
    "gen72ii": "gen72_ii",
    "rmgen72ii": "gen72_ii",
    "rx75": "rx75",
    "rmrx75": "rx75",
}

# package, real MoveIt launch, Gazebo MoveIt launch
_VARIANTS = {
    ("63", "standard"): (
        "rm_63_config", "real_moveit_demo.launch.py",
        "gazebo_moveit_demo.launch.py"
    ),
    ("63", "6f"): (
        "rm_63_config", "real_moveit_demo_6f.launch.py",
        "gazebo_moveit_demo_6f.launch.py"
    ),
    ("63", "6fb"): (
        "rm_63_config", "real_moveit_demo_6fb.launch.py",
        "gazebo_moveit_demo_6fb.launch.py"
    ),
    ("63_iii", "standard"): (
        "rm_63_config", "real_moveit_demo_III.launch.py",
        "gazebo_moveit_demo_III.launch.py"
    ),
    ("63_iii", "6fb"): (
        "rm_63_config", "real_moveit_demo_III_6fb.launch.py",
        "gazebo_moveit_demo_III_6fb.launch.py"
    ),
    ("65", "standard"): (
        "rm_65_config", "real_moveit_demo.launch.py",
        "gazebo_moveit_demo.launch.py"
    ),
    ("65", "6f"): (
        "rm_65_config", "real_moveit_demo_6f.launch.py",
        "gazebo_moveit_demo_6f.launch.py"
    ),
    ("65", "6fb"): (
        "rm_65_config", "real_moveit_demo_6fb.launch.py",
        "gazebo_moveit_demo_6fb.launch.py"
    ),
    ("75", "standard"): (
        "rm_75_config", "real_moveit_demo.launch.py",
        "gazebo_moveit_demo.launch.py"
    ),
    ("75", "6f"): (
        "rm_75_config", "real_moveit_demo_6f.launch.py",
        "gazebo_moveit_demo_6f.launch.py"
    ),
    ("75", "6fb"): (
        "rm_75_config", "real_moveit_demo_6fb.launch.py",
        "gazebo_moveit_demo_6fb.launch.py"
    ),
    ("eco62", "standard"): (
        "rm_eco62_config", "real_moveit_demo.launch.py",
        "gazebo_moveit_demo.launch.py"
    ),
    ("eco63", "standard"): (
        "rm_eco63_config", "real_moveit_demo.launch.py",
        "gazebo_moveit_demo.launch.py"
    ),
    ("eco63", "6fb"): (
        "rm_eco63_config", "real_moveit_demo_6fb.launch.py",
        "gazebo_moveit_demo_6fb.launch.py"
    ),
    ("eco65", "standard"): (
        "rm_eco65_config", "real_moveit_demo.launch.py",
        "gazebo_moveit_demo.launch.py"
    ),
    ("eco65", "6f"): (
        "rm_eco65_config", "real_moveit_demo_6f.launch.py",
        "gazebo_moveit_demo_6f.launch.py"
    ),
    ("eco65", "6fb"): (
        "rm_eco65_config", "real_moveit_demo_6fb.launch.py",
        "gazebo_moveit_demo_6fb.launch.py"
    ),
    ("gen72", "standard"): (
        "rm_gen72_config", "real_moveit_demo.launch.py",
        "gazebo_moveit_demo.launch.py"
    ),
    ("gen72_ii", "standard"): (
        "rm_gen72_config", "real_moveit_demo_II.launch.py",
        "gazebo_moveit_demo_II.launch.py"
    ),
    ("rx75", "6fb"): (
        "rm_rx75_config", "real_moveit_demo_6fb.launch.py",
        "gazebo_moveit_demo_6fb.launch.py"
    ),
    ("rx75", "6fb_v"): (
        "rm_rx75_config", "real_moveit_demo_6fb_v.launch.py",
        "gazebo_moveit_demo_6fb_v.launch.py"
    ),
}

if len(_VARIANTS) != 21:
    raise RuntimeError("Bringup variant catalog must contain 21 combinations.")


def _value(context, name):
    return LaunchConfiguration(name).perform(context)


def _compact_token(value):
    normalized = re.sub(r"[\s-]+", "_", value.lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized.replace("_", "")


def _normalize_arm_type(value):
    raw_value = value.strip() if isinstance(value, str) else ""
    arm_type = _ARM_TYPE_ALIASES.get(_compact_token(raw_value))
    if arm_type is None:
        valid = ", ".join(sorted({key[0] for key in _VARIANTS}))
        raise RuntimeError(
            f"Unsupported arm_type: {raw_value or value}. Valid arm types: {valid}."
        )
    return arm_type


def _resolve_selection(arm_type, arm_variant, mode):
    canonical_type = _normalize_arm_type(arm_type)
    canonical_mode = mode.strip().casefold()
    if canonical_mode not in ("real", "gazebo"):
        raise RuntimeError(
            f"Unsupported mode: {mode}. Valid modes: real, gazebo."
        )

    compact_variant = _compact_token(arm_variant.strip())
    if compact_variant == "auto":
        canonical_variant = "6fb" if canonical_type == "rx75" else "standard"
    else:
        canonical_variant = {
            "standard": "standard",
            "6f": "6f",
            "6fb": "6fb",
            "6fbv": "6fb_v",
        }.get(compact_variant)
    if canonical_variant is None:
        raise RuntimeError(
            f"Unsupported arm_variant: {arm_variant}. "
            "Valid values: auto, standard, 6f, 6fb, 6fb_v."
        )

    key = (canonical_type, canonical_variant)
    if key not in _VARIANTS:
        valid = ", ".join(
            variant for candidate, variant in _VARIANTS
            if candidate == canonical_type
        )
        raise RuntimeError(
            "Unsupported combination: "
            f"arm_type={canonical_type}, arm_variant={canonical_variant}. "
            f"Valid variants for {canonical_type}: {valid}."
        )
    return canonical_type, canonical_variant, canonical_mode, _VARIANTS[key]


def _boolean_value(name, value):
    normalized = value.strip().casefold()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    raise RuntimeError(
        f"Launch argument '{name}' must be a boolean value; received '{value}'."
    )


def _include(package, launch_file, arguments=None):
    launch_path = os.path.join(
        get_package_share_directory(package), "launch", launch_file
    )
    if not os.path.isfile(launch_path):
        raise RuntimeError(
            "Bringup component does not exist: "
            f"package={package}, launch_file={launch_file}"
        )
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(launch_path),
        launch_arguments=(arguments or {}).items(),
    )


def _moveit_action(
    context,
    arm_type,
    mode,
    moveit_spec,
    joint_states_topic,
):
    package, real_launch, gazebo_launch = moveit_spec
    arguments = {
        "allow_trajectory_execution": _value(
            context, "allow_trajectory_execution"
        ),
        "use_rviz": _value(context, "use_rviz"),
    }
    if arm_type == "rx75":
        arguments["joint_states_topic"] = joint_states_topic
    return _include(
        package,
        real_launch if mode == "real" else gazebo_launch,
        arguments,
    )


def _build_real_actions(
    context,
    arm_type,
    arm_variant,
    moveit_spec,
    use_moveit,
):
    actions = [
        _include(
            "rm_driver",
            "rm_driver.launch.py",
            {
                "arm_type": arm_type,
                "driver_config": _value(context, "driver_config"),
                "left_driver_config": _value(context, "left_driver_config"),
                "right_driver_config": _value(context, "right_driver_config"),
            },
        ),
        _include(
            "rm_description",
            "rm_description.launch.py",
            {
                "arm_type": arm_type,
                "arm_variant": arm_variant,
                "use_sim_time": "false",
                "joint_states_topic": "/joint_states",
                "use_joint_state_bridge": (
                    "true" if arm_type == "rx75" else "false"
                ),
                "use_joint_state_publisher_gui": "false",
                "use_rviz": "false",
            },
        ),
        _include(
            "rm_control",
            "rm_control.launch.py",
            {
                "arm_type": arm_type,
                "follow": _value(context, "follow"),
            },
        ),
    ]
    if use_moveit:
        actions.append(
            _moveit_action(
                context, arm_type, "real", moveit_spec, "/joint_states"
            )
        )
    return actions


def _build_gazebo_actions(
    context,
    arm_type,
    arm_variant,
    moveit_spec,
    use_moveit,
):
    for name in (
        "driver_config",
        "left_driver_config",
        "right_driver_config",
        "follow",
    ):
        if _value(context, name).strip().casefold() != "auto":
            raise RuntimeError(
                f"Launch argument '{name}' only applies in mode='real'."
            )

    joint_states_topic = (
        "/joint_state_broadcaster/joint_states"
        if arm_type == "rx75"
        else "/joint_states"
    )
    actions = [
        _include(
            "rm_gazebo",
            "rm_gazebo.launch.py",
            {
                "arm_type": arm_type,
                "arm_variant": arm_variant,
                "start_gazebo": _value(context, "start_gazebo"),
                "use_gazebo_gui": _value(context, "use_gazebo_gui"),
                "joint_states_topic": "auto",
                "use_sim_time": "true",
            },
        )
    ]
    if use_moveit:
        actions.append(
            TimerAction(
                period=8.0,
                actions=[
                    _moveit_action(
                        context,
                        arm_type,
                        "gazebo",
                        moveit_spec,
                        joint_states_topic,
                    )
                ],
            )
        )
    return actions


def _compose_bringup(context):
    arm_type, arm_variant, mode, moveit_spec = _resolve_selection(
        _value(context, "arm_type"),
        _value(context, "arm_variant"),
        _value(context, "mode"),
    )

    use_moveit = _boolean_value("use_moveit", _value(context, "use_moveit"))
    use_rviz = _boolean_value("use_rviz", _value(context, "use_rviz"))
    _boolean_value(
        "allow_trajectory_execution",
        _value(context, "allow_trajectory_execution"),
    )
    _boolean_value("start_gazebo", _value(context, "start_gazebo"))
    _boolean_value("use_gazebo_gui", _value(context, "use_gazebo_gui"))

    requested_joint_states_topic = _value(
        context, "joint_states_topic"
    ).strip()
    if requested_joint_states_topic != "auto":
        raise RuntimeError(
            "Launch argument 'joint_states_topic' currently only supports "
            f"'auto'; received '{requested_joint_states_topic or '<empty>'}'."
        )
    if use_rviz and not use_moveit:
        raise RuntimeError(
            "Launch argument 'use_rviz=true' requires 'use_moveit=true'."
        )

    if mode == "real":
        return _build_real_actions(
            context,
            arm_type,
            arm_variant,
            moveit_spec,
            use_moveit,
        )
    return _build_gazebo_actions(
        context,
        arm_type,
        arm_variant,
        moveit_spec,
        use_moveit,
    )


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "arm_type",
                description=(
                    "Robot model: 63, 63_iii, 65, 75, eco62, eco63, "
                    "eco65, gen72, gen72_ii, or rx75"
                ),
            ),
            DeclareLaunchArgument(
                "arm_variant",
                default_value="auto",
                description="End-link variant: auto, standard, 6f, 6fb, or 6fb_v",
            ),
            DeclareLaunchArgument("mode", default_value="real"),
            DeclareLaunchArgument(
                "allow_trajectory_execution",
                default_value="true",
                description=(
                    "Allow MoveIt trajectory execution; use false for the "
                    "first real-robot validation"
                ),
            ),
            DeclareLaunchArgument("use_moveit", default_value="true"),
            DeclareLaunchArgument("use_rviz", default_value="true"),
            DeclareLaunchArgument("driver_config", default_value="auto"),
            DeclareLaunchArgument("left_driver_config", default_value="auto"),
            DeclareLaunchArgument("right_driver_config", default_value="auto"),
            DeclareLaunchArgument("follow", default_value="auto"),
            DeclareLaunchArgument(
                "joint_states_topic",
                default_value="auto",
                choices=["auto"],
            ),
            DeclareLaunchArgument("start_gazebo", default_value="true"),
            DeclareLaunchArgument("use_gazebo_gui", default_value="true"),
            OpaqueFunction(function=_compose_bringup),
        ]
    )
