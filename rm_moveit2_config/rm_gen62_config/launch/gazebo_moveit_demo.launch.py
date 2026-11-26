import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gen62_moveit_common import generate_moveit_gazebo_launch


def generate_launch_description():
    return generate_moveit_gazebo_launch("rm_gen62_gazebo_moveit.urdf.xacro")
