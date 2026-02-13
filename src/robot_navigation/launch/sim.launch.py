from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Just launch TurtleBot3 world
        Node(
            package='turtlebot3_gazebo',
            executable='turtlebot3_world',
            name='turtlebot3_world',
            output='screen'
        ),
    ])
