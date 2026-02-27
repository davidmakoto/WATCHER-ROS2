#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math

class SimpleTurtleNavigator(Node):
    def __init__(self):
        super().__init__('simple_turtle_navigator')
        
        # Subscribe to turtle's position
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10
        )
        
        # Publish velocity commands
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        # Timer for navigation loop (10 Hz)
        self.timer = self.create_timer(0.1, self.navigate)
        
        self.current_pose = None
        self.goal_x = 9.0
        self.goal_y = 9.0
        
        self.get_logger().info('Turtle Navigator started!')
    
    def pose_callback(self, msg):
        """Update current position"""
        self.current_pose = msg
    
    def navigate(self):
        """Simple goal-seeking behavior"""
        if self.current_pose is None:
            return
        
        cmd = Twist()
        
        # Calculate distance to goal
        dx = self.goal_x - self.current_pose.x
        dy = self.goal_y - self.current_pose.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Calculate desired angle
        desired_angle = math.atan2(dy, dx)
        angle_diff = desired_angle - self.current_pose.theta
        
        # Normalize angle to [-pi, pi]
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        
        if distance > 0.1:  # Not at goal
            if abs(angle_diff) > 0.1:  # Need to turn
                cmd.angular.z = 2.0 * angle_diff
                cmd.linear.x = 0.0
            else:  # Move forward
                cmd.linear.x = 1.5 * distance
                cmd.angular.z = 0.5 * angle_diff
        else:
            self.get_logger().info('Goal reached!')
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
        
        self.cmd_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    navigator = SimpleTurtleNavigator()
    
    try:
        rclpy.spin(navigator)
    except KeyboardInterrupt:
        pass
    finally:
        navigator.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()