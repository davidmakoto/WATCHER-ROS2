import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_share = get_package_share_directory('robot_navigation')
    urdf_file = os.path.join(pkg_share, 'urdf', 'my_robot.urdf')
    rviz_config = os.path.join(pkg_share, 'rviz', 'my_robot.rviz')
    
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()
    
    return LaunchDescription([
        # Launch Gazebo
        ExecuteProcess(
            cmd=['gz', 'sim', '-r', 'empty.sdf'],
            output='screen'
        ),
        
        # Spawn robot
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-name', 'my_robot', '-string', robot_desc],
            output='screen'
        ),
        
        # Bridge topics
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            ],
            output='screen'
        ),
        
        # Your navigator
        Node(
            package='robot_navigation',
            executable='navigator',
            output='screen'
        ),
        
        # RViz with saved config
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
            output='screen'
        ),
    ])