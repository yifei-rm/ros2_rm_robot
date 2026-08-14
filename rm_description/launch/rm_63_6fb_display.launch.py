import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    actions = [
        DeclareLaunchArgument("link6_type", default_value="Link6_6fb"),
    ]
    launch_arguments = {
        "arm_type": "63",
        "arm_variant": "6fb",
        "use_sim_time": "false",
        "joint_states_topic": "/joint_states",
        "left_joint_states_topic": "/left_arm/joint_states",
        "right_joint_states_topic": "/right_arm/joint_states",
        "link6_type_override": LaunchConfiguration("link6_type"),
        "use_joint_state_bridge": "false",
        "use_joint_state_publisher_gui": "false",
        "use_rviz": "false",
    }
    unified_launch = os.path.join(
        get_package_share_directory("rm_description"),
        "launch",
        "rm_description.launch.py",
    )
    actions.append(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(unified_launch),
            launch_arguments=launch_arguments.items(),
        )
    )
    return LaunchDescription(actions)
