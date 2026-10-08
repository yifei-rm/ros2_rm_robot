"""Offline MoveIt entry point using the selected model without a hardware driver."""

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder

from rm_bringup.variant_catalog import resolve_variant
from rm_description.variant_catalog import (
    MODEL_FORMATS, format_arm_type, resolve_variant as resolve_description,
)


def build_moveit_config(arm_type, model="auto", mount_mappings=None):
    plan = resolve_variant(arm_type, "real")
    spec = resolve_description(format_arm_type(plan.arm_type, plan.arm_variant), model)
    description = Path(get_package_share_directory("rm_description"))
    model_file = description / "urdf" / spec.model_file
    if not model_file.is_file():
        raise ValueError(f"Robot description is missing: {model_file}")
    stem = (
        "rml_63_description" if plan.moveit.package == "rm_63_config"
        else f"{plan.moveit.package.removesuffix('_config')}_description"
    )
    semantic = f"config/{stem}.srdf"
    if plan.arm_type == "rx75":
        semantic = f"config/rm_rx75_{plan.arm_variant}_description.srdf"
    mappings = dict(spec.xacro_mappings)
    if spec.dual_arm:
        mappings.update(mount_mappings or {})
    return (
        MoveItConfigsBuilder(stem, package_name=plan.moveit.package)
        .robot_description(file_path=str(model_file), mappings=mappings)
        .robot_description_semantic(file_path=semantic)
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .trajectory_execution(
            file_path="config/moveit_controllers.yaml",
            moveit_manage_controllers=False,
        )
        .planning_pipelines(
            default_planning_pipeline="ompl",
            pipelines=["ompl", "pilz_industrial_motion_planner"],
            load_all=False,
        )
        .pilz_cartesian_limits(file_path="config/pilz_cartesian_limits.yaml")
        .joint_limits(file_path="config/joint_limits.yaml")
        .to_moveit_configs()
    )


def value(context, name):
    return LaunchConfiguration(name).perform(context)


def boolean(context, name):
    text = value(context, name).strip().casefold()
    if text not in ("true", "false"):
        raise RuntimeError(f"'{name}' must be true or false, received '{text}'.")
    return text == "true"


def launch_setup(context):
    try:
        config = build_moveit_config(
            value(context, "arm_type"), value(context, "model"),
            {name: value(context, name) for name in (
                "left_xyz", "left_rpy", "right_xyz", "right_rpy"
            )},
        )
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc
    topic = value(context, "joint_states_topic").strip()
    if not topic:
        raise RuntimeError("joint_states_topic must not be empty")
    remappings = [("joint_states", topic)]
    actions = [Node(
        package="moveit_ros_move_group", executable="move_group",
        output="screen", remappings=remappings,
        parameters=[config.to_dict(), {
            "allow_trajectory_execution": boolean(context, "allow_trajectory_execution"),
            "publish_robot_description": True,
            "publish_robot_description_semantic": True,
            "publish_planning_scene": True,
            "publish_geometry_updates": True,
            "publish_state_updates": True,
            "publish_transforms_updates": True,
            "monitor_dynamics": False,
            "trajectory_execution.allowed_execution_duration_scaling": 1.2,
            "trajectory_execution.allowed_goal_duration_margin": 0.5,
            "trajectory_execution.allowed_start_tolerance": 0.15,
        }],
    )]
    if boolean(context, "use_robot_state_publisher"):
        actions.append(Node(
            package="robot_state_publisher", executable="robot_state_publisher",
            parameters=[config.robot_description], remappings=remappings,
            output="screen",
        ))
    if boolean(context, "use_joint_state_publisher_gui"):
        actions.append(Node(
            package="joint_state_publisher_gui", executable="joint_state_publisher_gui",
            parameters=[config.robot_description], remappings=remappings,
            output="screen",
        ))
    if boolean(context, "use_rviz"):
        rviz_file = Path(config.package_path) / "config" / "moveit.rviz"
        actions.append(Node(
            package="rviz2", executable="rviz2", name="rviz2",
            arguments=["-d", str(rviz_file)], output="screen",
            parameters=[config.robot_description, config.robot_description_semantic,
                        config.robot_description_kinematics,
                        config.planning_pipelines, config.joint_limits],
            remappings=remappings,
        ))
    return actions


def generate_launch_description():
    arguments = {
        "allow_trajectory_execution": "false",
        "use_rviz": "true",
        "use_robot_state_publisher": "true",
        "use_joint_state_publisher_gui": "false",
        "joint_states_topic": "/joint_states",
        "left_xyz": "0 -0.075 0.5",
        "left_rpy": "3.14 1.57 1.5707963267949",
        "right_xyz": "0 0.075 0.5",
        "right_rpy": "3.14 1.57 -1.5707963267949",
    }
    return LaunchDescription([
        DeclareLaunchArgument(
            "arm_type",
            description="Robot model including end-link version, e.g. 65-6f or eco63-6fb",
        ),
        DeclareLaunchArgument("model", default_value="auto", choices=MODEL_FORMATS),
        *(DeclareLaunchArgument(name, default_value=default)
          for name, default in arguments.items()),
        OpaqueFunction(function=launch_setup),
    ])
