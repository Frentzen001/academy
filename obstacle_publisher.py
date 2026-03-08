import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool


def is_obstacle_detected(ranges, threshold=0.5):
    """
    Obstacle detection algorithm.

    Checks whether any range reading directly in front of the robot
    is closer than the given threshold distance.

    Args:
        ranges (list): Array of range readings from the LaserScan message.
        threshold (float): Distance in metres. Default is 0.5m.

    Returns:
        bool: True if an obstacle is detected, False otherwise.
    """
    num_readings = len(ranges)
    if num_readings == 0:
        return False

    front_index = num_readings // 2
    window = 10
    front_readings = ranges[max(0, front_index - window): front_index + window]

    valid_readings = [r for r in front_readings if r == r and r != float('inf')]

    if not valid_readings:
        return False

    return min(valid_readings) < threshold


class ObstaclePublisher(Node):

    def __init__(self):
        super().__init__('obstacle_publisher')

        self.publisher_ = self.create_publisher(Bool, '/obstacle_alert', 10)

        self.subscription = self.create_subscription(
            LaserScan,
            '/hokuyo',
            self.lidar_callback,
            10
        )

        self.get_logger().info('Obstacle Publisher node started.')

    def lidar_callback(self, msg):
        detected = is_obstacle_detected(list(msg.ranges))

        alert = Bool()
        alert.data = detected
        self.publisher_.publish(alert)

        if detected:
            self.get_logger().warn('Obstacle detected!')
        else:
            self.get_logger().info('Path is clear.')


def main(args=None):
    rclpy.init(args=args)
    node = ObstaclePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
