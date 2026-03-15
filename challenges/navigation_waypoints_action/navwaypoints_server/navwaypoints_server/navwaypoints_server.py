#!/usr/bin/env python3

import os
import time
import pickle
import datetime
import rclpy
from rclpy.action import ActionServer, ActionClient
from rclpy.node import Node
from geometry_msgs.msg import Point, PoseStamped
from nav2_msgs.action import NavigateToPose
from navwaypoints_interfaces.action import NavigateWaypoints

RESULTS_DIR = '/tmp/challenge_results'
RESULTS_FILE = os.path.join(RESULTS_DIR, 'waypoint_results.pkl')


class WaypointServer(Node):
    def __init__(self):
        super().__init__('waypoint_server')

        # Initialize the Action Server
        self._action_server = ActionServer(
            self,
            NavigateWaypoints,
            'navigate_waypoints',
            self.execute_callback
        )
        self.nav_to_pose_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        os.makedirs(RESULTS_DIR, exist_ok=True)
        self.get_logger().info('Waypoint Action Server is up and waiting for goals...')

    def _load_results(self):
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, 'rb') as f:
                return pickle.load(f)
        return []

    def _save_results(self, results):
        with open(RESULTS_FILE, 'wb') as f:
            pickle.dump(results, f)

    def execute_callback(self, goal_handle):
        self.get_logger().info('Received new navigation goal!')

        waypoints = goal_handle.request.waypoints
        feedback_msg = NavigateWaypoints.Feedback()

        run_start = time.monotonic()
        run_timestamp = datetime.datetime.now()
        waypoint_records = []

        for i, target_point in enumerate(waypoints):
            self.get_logger().info(
                f'Navigating to Waypoint {i+1}: [X: {target_point.x:.2f}, Y: {target_point.y:.2f}]'
            )

            nav_goal = NavigateToPose.Goal()
            nav_goal.pose.header.frame_id = 'map'
            nav_goal.pose.header.stamp = self.get_clock().now().to_msg()
            nav_goal.pose.pose.position.x = target_point.x
            nav_goal.pose.pose.position.y = target_point.y
            nav_goal.pose.pose.orientation.w = 1.0

            self.get_logger().info('Waiting for Nav2 server...')
            self.nav_to_pose_client.wait_for_server()

            self.get_logger().info('Sending goal to Nav2...')
            wp_start = time.monotonic()
            send_goal_future = self.nav_to_pose_client.send_goal_async(nav_goal)

            while not send_goal_future.done():
                time.sleep(0.1)

            goal_handle_nav = send_goal_future.result()
            if not goal_handle_nav.accepted:
                self.get_logger().error('Nav2 goal rejected')
                waypoint_records.append({
                    'index': i + 1,
                    'point': {'x': target_point.x, 'y': target_point.y},
                    'reached': False,
                    'time_seconds': time.monotonic() - wp_start,
                })
                self._append_run(run_timestamp, waypoint_records, run_start, success=False)
                goal_handle.abort()
                return NavigateWaypoints.Result()

            self.get_logger().info('Nav2 goal accepted')
            get_result_future = goal_handle_nav.get_result_async()

            while not get_result_future.done():
                if goal_handle.is_cancel_requested:
                    self.get_logger().info('Goal canceled!')
                    waypoint_records.append({
                        'index': i + 1,
                        'point': {'x': target_point.x, 'y': target_point.y},
                        'reached': False,
                        'time_seconds': time.monotonic() - wp_start,
                    })
                    self._append_run(run_timestamp, waypoint_records, run_start, success=False)
                    goal_handle.canceled()
                    goal_handle_nav.cancel_goal_async()
                    return NavigateWaypoints.Result()
                time.sleep(0.1)

            wp_time = time.monotonic() - wp_start
            status = get_result_future.result().status

            if status == 4:  # GoalStatus.STATUS_SUCCEEDED
                self.get_logger().info(f'Reached Waypoint {i+1}! ({wp_time:.2f}s)')
                waypoint_records.append({
                    'index': i + 1,
                    'point': {'x': target_point.x, 'y': target_point.y},
                    'reached': True,
                    'time_seconds': wp_time,
                })
            else:
                self.get_logger().warn(
                    f'Navigation to Waypoint {i+1} finished with status: {status}'
                )
                self.get_logger().error(f'Failed to reach Waypoint {i+1}!')
                waypoint_records.append({
                    'index': i + 1,
                    'point': {'x': target_point.x, 'y': target_point.y},
                    'reached': False,
                    'time_seconds': wp_time,
                })
                self._append_run(run_timestamp, waypoint_records, run_start, success=False)
                goal_handle.abort()
                return NavigateWaypoints.Result()

            feedback_msg.last_passed_waypoint = target_point
            goal_handle.publish_feedback(feedback_msg)

        total_time = time.monotonic() - run_start
        self._append_run(run_timestamp, waypoint_records, run_start, success=True)

        goal_handle.succeed()

        result = NavigateWaypoints.Result()
        result.status = 1
        self.get_logger().info(
            f'All waypoints reached in {total_time:.2f}s. Results saved to {RESULTS_FILE}'
        )
        return result

    def _append_run(self, timestamp, waypoint_records, run_start, success):
        total_time = time.monotonic() - run_start
        run_entry = {
            'timestamp': timestamp,
            'success': success,
            'total_time_seconds': total_time,
            'waypoints': waypoint_records,
        }
        all_results = self._load_results()
        all_results.append(run_entry)
        self._save_results(all_results)
        self.get_logger().info(
            f'Run saved (run #{len(all_results)}, success={success}, total={total_time:.2f}s)'
        )


def main(args=None):
    rclpy.init(args=args)
    action_server = WaypointServer()

    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(action_server)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        action_server.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
