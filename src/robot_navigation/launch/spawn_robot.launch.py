import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Path to your URDF file
    pkg_share = get_package_share_directory('robot_navigation')
    urdf_file = os.path.join(pkg_share, 'urdf', 'my_robot.urdf')
    
    # Read URDF content
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()
    
    return LaunchDescription([
        # Launch Gazebo with empty world
        ExecuteProcess(
            cmd=['gz', 'sim', '-r', 'empty.sdf'],
            output='screen'
        ),
        
        # Spawn your robot from URDF
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-name', 'my_robot',
                '-string', robot_desc,
                '-x', '0',
                '-y', '0', 
                '-z', '0.5'
            ],
            output='screen'
        ),
        
        # Bridge Gazebo topics to ROS 2
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
                '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry'
            ],
            output='screen'
        ),
    ])