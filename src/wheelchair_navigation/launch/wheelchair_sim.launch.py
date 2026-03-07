import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

CAMERAS = ['front', 'front_right', 'front_left', 'back', 'back_right', 'back_left']


def generate_launch_description():
    pkg_share = get_package_share_directory('wheelchair_navigation')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    urdf_file = os.path.join(pkg_share, 'urdf', 'wheelchair.urdf')
    sdf_file = os.path.join(pkg_share, 'urdf', 'wheelchair.sdf')
    world_file = os.path.join(pkg_share, 'worlds', 'obstacles.sdf')
    ekf_config = os.path.join(pkg_share, 'config', 'ekf.yaml')
    nav2_params = os.path.join(pkg_share, 'config', 'nav2_params.yaml')

    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    # Build bridge args for all 6 cameras + base topics
    bridge_args = []
    for cam in CAMERAS:
        bridge_args += [
            f'/depth_camera_{cam}/image@sensor_msgs/msg/Image[gz.msgs.Image',
            f'/depth_camera_{cam}/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
        ]
    bridge_args += [
        '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
        '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
        '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        '/model/wheelchair/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
    ]

    # depth_image_proc nodes: depth image → PointCloud2
    pointcloud_nodes = [
        Node(
            package='depth_image_proc',
            executable='point_cloud_xyz_node',
            name=f'depth_to_pc_{cam}',
            remappings=[
                ('depth/image_rect', f'/depth_camera_{cam}/image'),
                ('depth/camera_info', f'/depth_camera_{cam}/camera_info'),
                ('points', f'/camera_{cam}/points'),
            ],
            parameters=[{'use_sim_time': True}],
            output='screen',
        )
        for cam in CAMERAS
    ]

    return LaunchDescription([
        # Gazebo simulator
        ExecuteProcess(
            cmd=['gz', 'sim', '-r', world_file],
            output='screen'
        ),

        # Spawn from SDF (preserves sensor plugins stripped by URDF -string)
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-name', 'wheelchair', '-file', sdf_file,
                       '-x', '0', '-y', '0', '-z', '0.5'],
            output='screen'
        ),

        # Gz <-> ROS bridge
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=bridge_args,
            output='screen'
        ),

        # URDF → TF tree
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc, 'use_sim_time': True}],
            output='screen'
        ),

        # EKF: fuses /odom → publishes odom→base_footprint TF
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            parameters=[ekf_config],
            output='screen'
        ),

        # PointCloud2 converters (6x)
        *pointcloud_nodes,

        # Nav2 lifecycle manager
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'autostart': True,
                'node_names': [
                    'planner_server',
                    'controller_server',
                    'bt_navigator',
                    'local_costmap',
                    'global_costmap',
                ],
            }],
        ),

        # Nav2 stack
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')
            ),
            launch_arguments={
                'params_file': nav2_params,
                'use_sim_time': 'true',
            }.items()
        ),
    ])
