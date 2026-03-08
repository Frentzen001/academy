import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool


class ObstacleSubscriber(Node):

    def __init__(self):
        super().__init__('obstacle_subscriber')

        self.subscription = self.create_subscription(
            Bool,
            '/obstacle_alert',
            self.alert_callback,
            10
        )

        self.get_logger().info('Obstacle Subscriber node started. Listening for alerts...')

    def alert_callback(self, msg):
        if msg.data:
            self.get_logger().warn('Obstacle detected!')
        else:
            self.get_logger().info('Path is clear.')


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
