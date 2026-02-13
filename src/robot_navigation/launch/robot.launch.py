from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    use_sim = LaunchConfiguration('use_sim', default='false')
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim',
            default_value='false',
            description='Use Gazebo simulation or real hardware'
        ),
        
        # Launch TurtleBot3 simulation if use_sim=true
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('turtlebot3_gazebo'),
                    'launch',
                    'turtlebot3_world.launch.py'
                ])
            ]),
            condition=IfCondition(use_sim)
        ),
        
        # Your navigation node (always runs)
        Node(
            package='robot_navigation',
            executable='navigator',
            name='navigator',
            output='screen',
            parameters=[{'use_sim': use_sim}]
        ),
    ])
