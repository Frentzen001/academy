import rclpy
import math
import os
import yaml
from ament_index_python.packages import get_package_share_directory
from rclpy.action import ActionClient
from rclpy.node import Node
from geometry_msgs.msg import Point, PoseWithCovarianceStamped
from rclpy.qos import QoSProfile, ReliabilityPolicy

from navwaypoints_interfaces.action import NavigateWaypoints

class WaypointClient(Node):
    def __init__(self):
        super().__init__('waypoint_client')
        
        # Initialize Action Client
        self._action_client = ActionClient(self, NavigateWaypoints, 'navigate_waypoints')
        
        # Subscribe to robot pose to independently verify arrival
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.create_subscription(PoseWithCovarianceStamped, '/amcl_pose', self.pose_callback, qos)

        # Timing and Tracking variables
        self.start_time = None
        self.tracked_waypoints = []
        
        # "Anti-Cheat" Verification State
        self.pending_targets = []  # List of Points we expect to visit
        self.current_target_idx = 0
        self.verified_arrival_times = []
        self.verification_tolerance = 0.35 # meters

    def pose_callback(self, msg):
        if not self.start_time or self.current_target_idx >= len(self.pending_targets):
            return

        current_x = msg.pose.pose.position.x
        current_y = msg.pose.pose.position.y
        
        target = self.pending_targets[self.current_target_idx]
        
        # Calculate Euclidean distance
        distance = math.sqrt(pow(current_x - target.x, 2) + pow(current_y - target.y, 2))
        
        if distance < self.verification_tolerance:
            arrival_time = self.get_clock().now()
            duration = (arrival_time - self.start_time).nanoseconds / 1e9
            
            self.get_logger().info(f'✅ INDEPENDENT VERIFICATION: Robot is physically near Waypoint {self.current_target_idx + 1} ({distance:.2f}m away) at {duration:.2f}s')
            
            self.verified_arrival_times.append(duration)
            self.current_target_idx += 1

    def send_goal(self, waypoints):
        self.get_logger().info('Waiting for action server...')
        self._action_client.wait_for_server()

        # Create the goal message
        goal_msg = NavigateWaypoints.Goal()
        goal_msg.waypoints = waypoints
        
        # Store targets for verification
        self.pending_targets = waypoints

        self.get_logger().info('Sending goal with 4 waypoints...')
        
        # Record the exact start time
        self.start_time = self.get_clock().now()

        # Send the goal asynchronously
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by server!')
            return

        self.get_logger().info('Goal accepted! Robot is moving...')
        
        # Wait for the final result
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        p = feedback_msg.feedback.last_passed_waypoint
        point_tuple = (round(p.x, 3), round(p.y, 3)) # Round to avoid float precision issues
        
        # Only record time if this is the FIRST time we've seen this waypoint in feedback
        if point_tuple not in self.tracked_waypoints:
            self.tracked_waypoints.append(point_tuple)
            
            current_time = self.get_clock().now()
            duration = (current_time - self.start_time).nanoseconds / 1e9
            
            self.get_logger().info(
                f'--> Waypoint Reached at [X: {p.x:.2f}, Y: {p.y:.2f}]! Time elapsed: {duration:.2f}s'
            )

    def get_result_callback(self, future):
        result = future.result().result
        
        # Record final time
        end_time = self.get_clock().now()
        total_duration = (end_time - self.start_time).nanoseconds / 1e9
        
        self.get_logger().info(f'=== Navigation Complete! Server Status: {result.status} ===')
        self.get_logger().info(f'=== Total Mission Time: {total_duration:.2f} seconds ===')
        
        # Compare verification
        if len(self.verified_arrival_times) == len(self.pending_targets):
             self.get_logger().info('🏆 SUCCESS: Client independently verified arrival at all waypoints!')
        else:
             self.get_logger().warn(f'⚠️ WARNING: Client only verified {len(self.verified_arrival_times)}/{len(self.pending_targets)} waypoints! Possible skipping or cheating detecting.')

        # Shut down node after completion
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    action_client = WaypointClient()
    
    # Load waypoints from config file
    pkg_share_path = get_package_share_directory('navwaypoints_client')
    config_path = os.path.join(pkg_share_path, 'config', 'waypoints.yaml')
    
    action_client.get_logger().info(f'Loading waypoints from: {config_path}')

    if not os.path.exists(config_path):
        action_client.get_logger().error(f'Config file not found: {config_path}')
        return

    with open(config_path, 'r') as file:
        waypoints_data = yaml.safe_load(file)

    if not waypoints_data or 'waypoints' not in waypoints_data:
        action_client.get_logger().error('Invalid config file format! Missing "waypoints" key.')
        return

    target_coords = waypoints_data['waypoints']
    action_client.get_logger().info(f'Loaded {len(target_coords)} waypoints from config.')

    # Convert tuples into geometry_msgs/Point objects
    waypoints = []
    for x, y in target_coords:
        p = Point()
        p.x = x
        p.y = y
        p.z = 0.0
        waypoints.append(p)
        
    action_client.send_goal(waypoints)
    rclpy.spin(action_client)

if __name__ == '__main__':
    main()