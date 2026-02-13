#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np

class SimpleNavigator(Node):
    def __init__(self):
        super().__init__('simple_navigator')
        
        # Subscribe to lidar
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )
        
        # Publish velocity commands
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.current_scan = None
        self.get_logger().info('Simple Navigator Started!')
    
    def scan_callback(self, msg):
        """Process lidar data"""
        self.current_scan = msg
        
        # Simple obstacle avoidance
        ranges = np.array(msg.ranges)
        ranges[np.isinf(ranges)] = msg.range_max
        
        cmd = Twist()
        
        # Check front sector (middle third of scan)
        num_ranges = len(ranges)
        front_start = num_ranges // 3
        front_end = 2 * num_ranges // 3
        front_ranges = ranges[front_start:front_end]
        
        if len(front_ranges) > 0:
            min_dist = np.min(front_ranges)
            
            if min_dist < 0.5:  # Obstacle within 0.5m
                cmd.linear.x = 0.0
                cmd.angular.z = 0.5  # Turn
                self.get_logger().info(f'Obstacle at {min_dist:.2f}m - turning')
            else:
                cmd.linear.x = 0.2  # Move forward
                cmd.angular.z = 0.0
                self.get_logger().info(f'Clear ahead ({min_dist:.2f}m) - moving forward')
        
        self.cmd_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    navigator = SimpleNavigator()
    
    try:
        rclpy.spin(navigator)
    except KeyboardInterrupt:
        pass
    finally:
        navigator.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
