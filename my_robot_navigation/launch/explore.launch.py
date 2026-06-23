import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # On pointe directement vers votre package my_robot_navigation
    config_file = os.path.join(
        get_package_share_directory('my_robot_navigation'),
        'config',
        'explore.yaml'
    )

    explore_node = Node(
        package='explore_lite',
        executable='explore',
        name='explore_node',
        output='screen',
        parameters=[config_file, {'use_sim_time': True}] # Indispensable avec Gazebo
    )

    return LaunchDescription([
        explore_node
    ])