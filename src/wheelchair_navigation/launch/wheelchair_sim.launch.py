import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Get package paths
    pkg_share = get_package_share_directory('wheelchair_navigation')
    
    # File paths
    urdf_file = os.path.join(pkg_share, 'urdf', 'wheelchair.urdf')
    # world_file = 'empty.sdf'  # Uses Gazebo's built-in empty world
    # world_file = '/opt/ros/jazzy/share/turtlebot3_gazebo/worlds/turtlebot3_world.sdf'
    world_file = os.path.join(pkg_share, 'worlds', 'obstacles.sdf')
    
    # Read URDF
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()
    
    return LaunchDescription([
        # Launch Gazebo
        ExecuteProcess(
            cmd=['gz', 'sim', '-r', world_file],
            output='screen'
        ),
        
        # Spawn wheelchair in Gazebo
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-name', 'wheelchair',
                '-string', robot_desc,
                '-x', '0', '-y', '0', '-z', '0.5'
            ],
            output='screen'
        ),
        
        # Bridge Gazebo<->ROS topics
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
                '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
            ],
            output='screen'
        ),
        
        # Robot state publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc}],
            output='screen'
        ),
    ])
