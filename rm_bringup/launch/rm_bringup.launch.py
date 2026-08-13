"""Unified, component-level bringup for every supported RealMan arm."""

import os

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

from rm_bringup.variant_catalog import LaunchReference, resolve_variant


_TRUE_VALUES = {'1', 'true', 'yes', 'on'}
_FALSE_VALUES = {'0', 'false', 'no', 'off'}


def _value(context, name):
    return LaunchConfiguration(name).perform(context)


def _boolean_value(name, value):
    normalized = value.strip().casefold()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    raise RuntimeError(
        f"Launch argument '{name}' must be a boolean value; received '{value}'."
    )


def _include(reference: LaunchReference, arguments=None):
    launch_path = os.path.join(
        get_package_share_directory(reference.package),
        'launch',
        reference.launch_file,
    )
    if not os.path.isfile(launch_path):
        raise RuntimeError(
            'Bringup component does not exist: '
            f'package={reference.package}, '
            f'launch_file={reference.launch_file}'
        )
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(launch_path),
        launch_arguments=(arguments or {}).items(),
    )


def _resolved_joint_states_topic(context, plan):
    requested = _value(context, 'joint_states_topic').strip()
    if requested != 'auto':
        raise RuntimeError(
            "Launch argument 'joint_states_topic' currently only supports "
            f"'auto'; received '{requested or '<empty>'}'."
        )
    return plan.arm_profile.joint_states_topic(plan.mode)


def _moveit_action(context, plan, joint_states_topic):
    moveit_arguments = {
        'allow_trajectory_execution': _value(
            context, 'allow_trajectory_execution'
        ),
        'use_rviz': _value(context, 'use_rviz'),
    }
    if plan.arm_type == 'rx75' and plan.mode == 'gazebo':
        moveit_arguments['joint_states_topic'] = joint_states_topic

    return _include(plan.moveit, moveit_arguments)


def _build_real_actions(context, plan, joint_states_topic, use_moveit):
    actions = [
        _include(
            plan.driver,
            {
                'arm_type': plan.arm_profile.driver_profile,
                'driver_config': _value(context, 'driver_config'),
                'left_driver_config': _value(
                    context, 'left_driver_config'
                ),
                'right_driver_config': _value(
                    context, 'right_driver_config'
                ),
            },
        ),
        _include(
            plan.description,
            {
                'arm_type': plan.arm_type,
                'arm_variant': plan.arm_variant,
                'use_sim_time': 'false',
                'joint_states_topic': joint_states_topic,
                'use_joint_state_bridge': (
                    'true'
                    if plan.arm_profile.use_joint_state_bridge
                    else 'false'
                ),
                'use_joint_state_publisher_gui': 'false',
                'use_rviz': 'false',
            },
        ),
        _include(
            plan.control,
            {
                'arm_type': plan.arm_profile.control_profile,
                'follow': _value(context, 'follow'),
            },
        ),
    ]
    if use_moveit:
        actions.append(_moveit_action(context, plan, joint_states_topic))
    return actions


def _build_gazebo_actions(context, plan, joint_states_topic, use_moveit):
    for name in (
        'driver_config',
        'left_driver_config',
        'right_driver_config',
        'follow',
    ):
        if _value(context, name).strip().casefold() != 'auto':
            raise RuntimeError(
                f"Launch argument '{name}' only applies in mode='real'."
            )

    actions = [
        _include(
            plan.gazebo,
            {
                'arm_type': plan.arm_type,
                'arm_variant': plan.arm_variant,
                'start_gazebo': _value(context, 'start_gazebo'),
                'joint_states_topic': 'auto',
            },
        )
    ]
    if use_moveit:
        actions.append(
            TimerAction(
                period=8.0,
                actions=[
                    _moveit_action(context, plan, joint_states_topic)
                ],
            )
        )
    return actions


def _compose_bringup(context):
    try:
        plan = resolve_variant(
            _value(context, 'arm_type'),
            _value(context, 'arm_variant'),
            _value(context, 'mode'),
        )
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc

    use_moveit = _boolean_value(
        'use_moveit', _value(context, 'use_moveit')
    )
    use_rviz = _boolean_value('use_rviz', _value(context, 'use_rviz'))
    _boolean_value(
        'allow_trajectory_execution',
        _value(context, 'allow_trajectory_execution'),
    )
    _boolean_value(
        'start_gazebo',
        _value(context, 'start_gazebo'),
    )
    if use_rviz and not use_moveit:
        raise RuntimeError(
            "Launch argument 'use_rviz=true' requires 'use_moveit=true'."
        )

    joint_states_topic = _resolved_joint_states_topic(context, plan)
    if plan.mode == 'real':
        return _build_real_actions(
            context, plan, joint_states_topic, use_moveit
        )
    return _build_gazebo_actions(
        context, plan, joint_states_topic, use_moveit
    )


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'arm_type',
                description=(
                    'Robot model: 63, 63_iii, 65, 75, eco62, eco63, eco65, '
                    'gen72, gen72_ii, or rx75'
                ),
            ),
            DeclareLaunchArgument(
                'arm_variant',
                default_value='auto',
                description=(
                    'End-link variant: auto, standard, 6f, 6fb, or 6fb_v; '
                    'auto selects 6fb for RX75 and standard otherwise'
                ),
            ),
            DeclareLaunchArgument(
                'mode',
                default_value='real',
                description='Bringup mode: real or gazebo',
            ),
            DeclareLaunchArgument(
                'allow_trajectory_execution',
                default_value='true',
                description='Allow MoveIt to execute trajectories',
            ),
            DeclareLaunchArgument(
                'use_moveit',
                default_value='true',
                description='Start move_group and its supporting nodes',
            ),
            DeclareLaunchArgument(
                'use_rviz',
                default_value='true',
                description='Start the MoveIt RViz process',
            ),
            DeclareLaunchArgument(
                'driver_config',
                default_value='auto',
                description='Single-arm driver YAML or auto',
            ),
            DeclareLaunchArgument(
                'left_driver_config',
                default_value='auto',
                description='RX75 left-arm driver YAML or auto',
            ),
            DeclareLaunchArgument(
                'right_driver_config',
                default_value='auto',
                description='RX75 right-arm driver YAML or auto',
            ),
            DeclareLaunchArgument(
                'follow',
                default_value='auto',
                description='Driver-follow mode: auto, true, or false',
            ),
            DeclareLaunchArgument(
                'joint_states_topic',
                default_value='auto',
                choices=['auto'],
                description=(
                    'Only auto is currently supported; it selects the '
                    'model/mode default joint-state topic'
                ),
            ),
            DeclareLaunchArgument(
                'start_gazebo',
                default_value='true',
                description='Start the Gazebo server and client',
            ),
            OpaqueFunction(function=_compose_bringup),
        ]
    )
