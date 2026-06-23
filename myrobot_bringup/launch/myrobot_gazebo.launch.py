from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    # =========================================================================
    # 🔹 Fix GPU NVIDIA (mode on-demand / Optimus RTX 3060)
    # Doit être déclaré avant tout node
    # =========================================================================
    set_nvidia_offload = SetEnvironmentVariable('__NV_PRIME_RENDER_OFFLOAD', '1')
    set_nvidia_glx     = SetEnvironmentVariable('__GLX_VENDOR_LIBRARY_NAME', 'nvidia')

    # =========================================================================
    # 🔹 Arguments dynamiques
    # =========================================================================
    model_arg = DeclareLaunchArgument(
        'model',
        default_value='turtle_nav.urdf.xacro',
        description='URDF/XACRO file'
    )
    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='turtle_nav',
        description='Nom du robot dans Gazebo'
    )
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='turtle_train_world.world',
        description='Fichier world Gazebo'
    )
    x_arg = DeclareLaunchArgument('x', default_value='0.0')
    y_arg = DeclareLaunchArgument('y', default_value='0.0')
    z_arg = DeclareLaunchArgument('z', default_value='0.01')

    # =========================================================================
    # 🔹 Variables
    # =========================================================================
    model      = LaunchConfiguration('model')
    robot_name = LaunchConfiguration('robot_name')
    world      = LaunchConfiguration('world')
    x          = LaunchConfiguration('x')
    y          = LaunchConfiguration('y')
    z          = LaunchConfiguration('z')

    # =========================================================================
    # 🔹 Packages
    # =========================================================================
    description_pkg = get_package_share_directory('my_robot_description')
    bringup_pkg     = get_package_share_directory('myrobot_bringup')

    # =========================================================================
    # 🔹 Paths
    # =========================================================================
    urdf_path     = PathJoinSubstitution([description_pkg, 'urdf', model])
    world_path    = PathJoinSubstitution([bringup_pkg, 'worlds', world])
    rviz_config   = PathJoinSubstitution([bringup_pkg, 'rviz', 'myrobot.rviz'])
    bridge_config = os.path.join(bringup_pkg, 'config', 'ros_gz_bridge.yaml')

    # =========================================================================
    # 🔹 Robot description
    # =========================================================================
    robot_description = Command(['xacro ', urdf_path])

    # =========================================================================
    # 🔹 Nodes
    # =========================================================================

    # --- Robot State Publisher ---
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
            'publish_frequency': 30.0,
        }]
    )

    # --- Gazebo Harmonic ---
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ),
        launch_arguments={
            'gz_args': [world_path, ' -r --render-engine ogre']
        }.items()
    )

    # --- Spawn robot dans Gazebo ---
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name',  robot_name,
            '-x', x,
            '-y', y,
            '-z', z
        ],
        output='screen'
    )

    # --- Bridge ROS2 <-> Gazebo Harmonic ---
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        parameters=[
            {'config_file': bridge_config},
            {'use_sim_time': True},
            {'qos_overrides./tf_static.publisher.durability': 'transient_local'},
            {'qos_overrides./tf_static.publisher.reliability': 'reliable'},
            {'subscription_heartbeat_period_ms': 100},  
        ],
        output='screen'
    )

    # --- RViz2 ---
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',                              
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],      
        output='screen'
    )

    # =========================================================================
    # 🔹 Spawners de Contrôleurs
    # =========================================================================

    # --- Spawner pour le contrôleur Diff Drive ---
    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont", "--controller-manager", "/controller_manager"],
        ros_arguments=["--remap", "/diff_cont/cmd_vel:=/cmd_vel"],
        output="screen",
    )

    # --- Spawner pour le Joint State Broadcaster ---
    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
        output="screen",
    )

    # =========================================================================
    # 🔹 Launch Description
    # =========================================================================
    return LaunchDescription([
        set_nvidia_offload,
        set_nvidia_glx,
        model_arg,
        robot_name_arg,
        world_arg,
        x_arg,
        y_arg,
        z_arg,
        gazebo,
        spawn_entity,
        bridge,
        robot_state_publisher,
        rviz,
        diff_drive_spawner,
        joint_broad_spawner,
    ])