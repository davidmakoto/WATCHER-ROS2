import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_share = get_package_share_directory('wheelchair_navigation')

    urdf_file = os.path.join(pkg_share, 'urdf', 'wheelchair.urdf')
    sdf_file = os.path.join(pkg_share, 'urdf', 'wheelchair.sdf')
    world_file = os.path.join(pkg_share, 'worlds', 'obstacles.sdf')

    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    return LaunchDescription([
        # Launch Gazebo
        ExecuteProcess(
            cmd=['gz', 'sim', '-r', world_file],
            output='screen'
        ),

        # Spawn wheelchair from SDF (URDF -string strips sensor plugins)
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-name', 'wheelchair',
                '-file', sdf_file,
                '-x', '0', '-y', '0', '-z', '0.5'
            ],
            output='screen'
        ),

        # Bridge Gazebo <-> ROS topics
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/depth_camera/image@sensor_msgs/msg/Image[gz.msgs.Image',
                '/depth_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
                '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                '/model/wheelchair/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
                '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            ],
            output='screen'
        ),

        # Broadcast odom → base_footprint transform (identity; odom pose is on /odom)
        # This is a quick hack — it makes odom and base_footprint the same (no drift tracked). 
        # For a proper solution later you'd use robot_localization's ekf_node to read /odom and publish the real transform. 
        # But for now this will get odom into your TF tree so RViz works.
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 'odom', 'base_footprint'],
            output='screen'
        ),

        # Robot state publisher (uses URDF for TF tree)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc}],
            output='screen'
        ),

        # Convert depth image to /scan for Nav2
        Node(
            package='depthimage_to_laserscan',
            executable='depthimage_to_laserscan_node',
            name='depthimage_to_laserscan',
            parameters=[{
                'scan_height': 10,
                'range_min': 0.3,
                'range_max': 10.0,
                'output_frame': 'camera_link',
            }],
            remappings=[
                ('depth', '/depth_camera/image'),
                ('depth_camera_info', '/depth_camera/camera_info'),
                ('scan', '/scan'),
            ],
            output='screen'
        ),
    ])
