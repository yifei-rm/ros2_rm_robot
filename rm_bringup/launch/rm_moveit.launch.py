"""Offline MoveIt using the selected model and Foxy's existing YAML configs."""

from pathlib import Path
import runpy

import xacro
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, OpaqueFunction
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def build_moveit_config(arm_type, model="auto", mount_mappings=None):
    bringup = runpy.run_path(str(Path(__file__).with_name("rm_bringup.launch.py")))
    arm_type, _, plan = bringup["_resolve_selection"](arm_type, "real")
    description_share = Path(get_package_share_directory("rm_description"))
    description = runpy.run_path(str(description_share / "launch/rm_description.launch.py"))
    _, (model_file, _, mappings, dual_arm) = description["_resolve_model"](arm_type, model)
    mappings = dict(mappings)
    if dual_arm:
        mappings.update(mount_mappings or {})
    model_path = description_share / "urdf" / model_file
    config_path = Path(get_package_share_directory(plan[0])) / "config"
    stem = "rml_63" if plan[0] == "rm_63_config" else plan[0][:-len("_config")]
    semantic = stem + "_description.srdf"
    if dual_arm:
        semantic = "rm_" + arm_type.replace("-", "_") + "_description.srdf"

    def load_yaml(filename):
        with (config_path / filename).open() as stream:
            return yaml.safe_load(stream)

    controllers = load_yaml("moveit_controllers.yaml")
    if "moveit_controller_manager" not in controllers:
        controllers = {
            "moveit_simple_controller_manager": controllers,
            "moveit_controller_manager": "moveit_simple_controller_manager/MoveItSimpleControllerManager",
        }
    controllers["moveit_manage_controllers"] = False
    pipeline = {
        "planning_plugin": "ompl_interface/OMPLPlanner",
        "request_adapters": (
            "default_planner_request_adapters/AddTimeOptimalParameterization "
            "default_planner_request_adapters/FixWorkspaceBounds "
            "default_planner_request_adapters/FixStartStateBounds "
            "default_planner_request_adapters/FixStartStateCollision "
            "default_planner_request_adapters/FixStartStatePathConstraints"
        ),
        "start_state_max_bounds_error": 0.1,
    }
    pipeline.update(load_yaml("ompl_planning.yaml"))
    # Foxy reads group kinematics directly, as in rx75_moveit_common.py.
    return {
        "description": {"robot_description": xacro.process_file(str(model_path), mappings=mappings).toxml()},
        "semantic": {"robot_description_semantic": (config_path / semantic).read_text()},
        "kinematics": load_yaml("kinematics.yaml"),
        "limits": {"robot_description_planning": load_yaml("joint_limits.yaml")},
        "pipeline": {"move_group": pipeline},
        "controllers": controllers,
        "rviz": str(config_path / "moveit.rviz"),
    }


def value(context, name):
    return LaunchConfiguration(name).perform(context)


def boolean(context, name):
    text = value(context, name).strip().casefold()
    if text not in ("true", "false", "1", "0", "yes", "no", "on", "off"):
        raise RuntimeError(f"'{name}' must be a boolean, received '{text}'.")
    return text in ("true", "1", "yes", "on")


def launch_setup(context):
    flags = {name: boolean(context, name) for name in (
        "allow_trajectory_execution", "use_rviz", "use_robot_state_publisher",
        "use_joint_state_publisher_gui",
    )}
    topic = value(context, "joint_states_topic").strip()
    if not topic:
        raise RuntimeError("joint_states_topic must not be empty")
    config = build_moveit_config(value(context, "arm_type"), value(context, "model"), {
        name: value(context, name) for name in ("left_xyz", "left_rpy", "right_xyz", "right_rpy")
    })
    remappings = [("joint_states", topic)]
    common = [config[key] for key in ("description", "semantic", "kinematics", "limits", "pipeline")]
    actions = [Node(
        package="moveit_ros_move_group", executable="move_group", output="screen",
        on_exit=[EmitEvent(event=Shutdown(reason="move_group exited"))],
        remappings=remappings,
        parameters=[*common, config["controllers"], {
            "allow_trajectory_execution": flags["allow_trajectory_execution"],
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
    for flag, package in (
        ("use_robot_state_publisher", "robot_state_publisher"),
        ("use_joint_state_publisher_gui", "joint_state_publisher_gui"),
    ):
        if flags[flag]:
            actions.append(Node(package=package, executable=package, output="screen",
                                parameters=[config["description"]], remappings=remappings))
    if flags["use_rviz"]:
        actions.append(Node(package="rviz2", executable="rviz2", name="rviz2",
                            arguments=["-d", config["rviz"]], output="screen",
                            parameters=common, remappings=remappings))
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
        DeclareLaunchArgument("arm_type", description="Robot model, e.g. 65-6f or eco63-6fb"),
        DeclareLaunchArgument("model", default_value="auto", choices=["auto", "stl", "dae"]),
        *(DeclareLaunchArgument(name, default_value=default) for name, default in arguments.items()),
        OpaqueFunction(function=launch_setup),
    ])
