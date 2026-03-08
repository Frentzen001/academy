# ROS 2 Assignment: Obstacle Notification System Integration

---

## Brief from Your Manager

Hey, welcome aboard! Glad to have you on the team

So for your first task, we've already got an obstacle detection algorithm ready to go and the notification system topic has been set up on our end. What we need from you is to **hook it all up to the robot's LIDAR sensor** and make sure the system is publishing correctly.

Here's what you need to know to get started:

- **Your task:** Integrate the provided obstacle detection algorithm with the robot's LIDAR sensor
- **Required Notification Topic:** `/obstacle_alert`
- **Required Notification Message Type:** `std_msgs/msg/Bool`
  - Publish `True` when an obstacle is within the threshold distance in front of the robot
  - Publish `False` when the path is clear
- The robot has a LIDAR sensor - you'll need to figure out which topic it's publishing on and what message type it uses
- Once your publisher is working, also write a **subscriber node** that listens to `/obstacle_alert` and prints appropriate log messages depending on the state

You've got access to the simulation environment. Take a look around and let the tools guide you. Good luck!

---

## Before You Start

If this is the first time you are working on any of these exercises, go through the environment setup guide before continuing:

[**Environment Setup →**](../environment_setup.md)

This covers how to access the simulation environment, launch Gazebo, and use the tools you will need throughout the exercises.

---

## Overview

Before starting, launch the robot simulation in one of your tmux panes:

```bash
ros2 launch linorobot2_gazebo gazebo.launch.py spawn_x:=0.5
```

Wait until Gazebo has fully loaded and the robot is visible in the browser before proceeding.

In this assignment you will:

1. Identify the correct LIDAR topic and message type
2. Visualize the LIDAR data in RViz to confirm it's working
3. Write a publisher node that runs the obstacle detection algorithm and publishes to `/obstacle_alert`
4. Write a subscriber node that listens to `/obstacle_alert` and reacts accordingly
5. Use `rqt_graph` to verify your nodes are connected correctly
6. Run an end-to-end test by moving the robot in front of an obstacle

---

## 1. Identify the LIDAR Topic

You've been told the robot has a LIDAR sensor, but nobody told you what topic it's on. Let's find it the proper way.

### 1.1 Find out what message type LIDAR uses

Before hunting through topics, figure out what you're looking for. Open a browser and search:

```
lidar message ros2
```

You're looking for the standard ROS 2 message type used for laser range-finder / LIDAR data. Take note of the **message type** (package and message name). You'll need it in the next step.

> **Hint:** It lives in the `sensor_msgs` package.

---

### 1.2 List all active topics

In your terminal, run:

```bash
ros2 topic list
```

This will print every topic currently being published in the ROS 2 system. You'll see quite a few and that's normal. Your job is to find the one that carries LIDAR data.

---

### 1.3 Check topic types

For each topic that looks like it could be sensor data, check its type:

```bash
ros2 topic info <topic_name>
```

Compare the **Type** field against the message type you found in 1.1. When they match, that's your LIDAR topic.

> **Tip:** You can also use `ros2 topic list -t` to see all topics with their types in one shot.

---

### 1.4 Inspect the data

Once you've identified the topic, verify it's actually streaming data:

```bash
ros2 topic echo <your_lidar_topic>
```

You should see a stream of range readings. Press `Ctrl+C` to stop.

Take note of the **`ranges`** array in the message. This is the array of distance readings your algorithm will use.

---

## 2. Visualize the LIDAR in RViz

Before writing any code, it's always good practice to **see** what your sensor is doing. Let's visualize the LIDAR in RViz.

### 2.1 Launch RViz

```bash
rviz2
```

RViz will open in the KasmVNC window.

### 2.2 Configure the display

Once RViz is open:

1. In the **"Fixed Frame"** field (top left panel), set it to:
   ```
   base_footprint
   ```

2. Click **"Add"** (bottom left) → select **"By topic"** tab

3. Find your LIDAR topic in the list and select its display type → click **OK**

You should now see the laser scan visualized as a ring of dots around the robot. If you look closely, the shape formed by the dots should resemble the silhouette of the simulated world in Gazebo — walls, objects, and obstacles will show up as clusters of points at their respective distances and angles. Move an obstacle close to the robot in Gazebo and watch the scan update in real time.

> This is a great sanity check. If you see data here, your topic identification was correct.

---

## 3. Write the Obstacle Detection Publisher Node

Now it's time to write the node. You'll be creating a ROS 2 Python package from scratch.

> **Reference:** For a sample of how a ROS 2 Python publisher and subscriber are structured, refer to the official tutorial:
> [Writing a simple publisher and subscriber (Python)](https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html)

---

### 3.1 Create your package

Navigate to the linorobot2 directory inside your workspace source:

```bash
cd ~/linorobot2_ws/src/linorobot2
```

> **Tip:** This directory is shared with your host machine. You can open `linorobot2_ws/src/linorobot2` in your favourite IDE on the host and any edits will be immediately visible inside the container.

Create a new package called `obstacle_notification`:

```bash
ros2 pkg create --build-type ament_python obstacle_notification
```

---

### 3.2 Create the publisher node

Navigate into the package:

```bash
cd ~/linorobot2_ws/src/linorobot2/obstacle_notification/obstacle_notification
```

Create a new file called `obstacle_publisher.py` and open it in your editor.

Here is the **algorithm function** you've been given. Your job is to integrate it into a ROS 2 node:

```python
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
```

> **Important:** The algorithm assumes the front of the robot maps to the middle
> index of the `ranges` array. This depends on the LIDAR's scan configuration.
> After running your node, verify it triggers correctly by driving the robot
> toward an obstacle and observing the `/obstacle_alert` output. If detection
> triggers from the wrong direction, the LIDAR's zero-index direction may differ
> from this assumption.

Now write a ROS 2 node around it. Your node should:

- **Subscribe** to the LIDAR topic you identified in Phase 1
- Call `is_obstacle_detected()` using the `ranges` data from each incoming message
- **Publish** the result (`True` or `False`) to `/obstacle_alert` as a `std_msgs/msg/Bool`

```python
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool


def is_obstacle_detected(ranges, threshold=0.5):
    # --- paste the algorithm function here ---
    pass


class ObstaclePublisher(Node):

    def __init__(self):
        super().__init__('obstacle_publisher')

        # TODO: Create a publisher on '/obstacle_alert' with message type Bool, queue size 10

        # TODO: Create a subscriber on your LIDAR topic with message type LaserScan
        #       and bind it to self.lidar_callback

        self.get_logger().info('Obstacle Publisher node started.')

    def lidar_callback(self, msg):
        # TODO: Call is_obstacle_detected() with msg.ranges
        # TODO: Create a Bool message, set its .data field, and publish it
        # TODO: Log whether an obstacle was detected or not
        pass


def main(args=None):
    rclpy.init(args=args)
    node = ObstaclePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

### 3.3 Update package.xml

Open `~/linorobot2_ws/src/linorobot2/obstacle_notification/package.xml` and add these three lines **after the existing `<buildtool_depend>` line**:

```xml
<exec_depend>rclpy</exec_depend>
<exec_depend>std_msgs</exec_depend>
<exec_depend>sensor_msgs</exec_depend>
```

---

### 3.4 Register the entry point

Open `~/linorobot2_ws/src/linorobot2/obstacle_notification/setup.py` and update the `console_scripts` list:

```python
entry_points={
    'console_scripts': [
        'obstacle_publisher = obstacle_notification.obstacle_publisher:main',
    ],
},
```

---

### 3.5 Build and run

`colcon build` is the standard build tool for ROS 2 workspaces. It compiles all packages in your `src/` directory and places the outputs under `install/`. The `--packages-select` flag lets you build only a specific package instead of rebuilding everything in the workspace — useful when you're iterating on a single package.

After building, you **must** run `source install/setup.bash` before running your nodes. This script updates your shell's environment (e.g. `PYTHONPATH`, `AMENT_PREFIX_PATH`) so that ROS 2 can find the newly built package. Without sourcing it, `ros2 run` won't know your package exists.

```bash
cd ~/linorobot2_ws
colcon build --packages-select obstacle_notification
source install/setup.bash
ros2 run obstacle_notification obstacle_publisher
```

You should see log output each time a LIDAR message is received. To verify it's publishing, open a second terminal and echo the output topic:

```bash
ros2 topic echo /obstacle_alert
```

Move an obstacle close to the robot in Gazebo and watch the value change between `True` and `False`.

---

## 4. Write the Subscriber Node

Now write a second node that **listens** to `/obstacle_alert` and reacts to the state.

### 4.1 Create the subscriber file

In the same package directory (`~/linorobot2_ws/src/linorobot2/obstacle_notification/obstacle_notification`), create `obstacle_subscriber.py`:

```python
import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool


class ObstacleSubscriber(Node):

    def __init__(self):
        super().__init__('obstacle_subscriber')

        # TODO: Create a subscriber on '/obstacle_alert' with message type Bool
        #       and bind it to self.alert_callback

        self.get_logger().info('Obstacle Subscriber node started. Listening for alerts...')

    def alert_callback(self, msg):
        # TODO: If msg.data is True, log a WARNING that an obstacle has been detected
        # TODO: If msg.data is False, log an INFO that the path is clear
        pass


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

> **Tip:** Use `self.get_logger().warning(...)` for obstacle alerts and `self.get_logger().info(...)` for clear path messages to make the output easy to read at a glance.

---

### 4.2 Register the entry point

Add the subscriber to `setup.py`:

```python
entry_points={
    'console_scripts': [
        'obstacle_publisher = obstacle_notification.obstacle_publisher:main',
        'obstacle_subscriber = obstacle_notification.obstacle_subscriber:main',
    ],
},
```

---

### 4.3 Rebuild and run

```bash
cd ~/linorobot2_ws
colcon build --packages-select obstacle_notification
source install/setup.bash
ros2 run obstacle_notification obstacle_subscriber
```

With both nodes running (publisher in one terminal, subscriber in another), you should see the subscriber printing log messages as the robot detects or clears obstacles.

---

## 5. End-to-End Test

With both nodes running, it's time to verify the full system works by interacting with the simulation.

### 5.1 Move the robot in front of an obstacle

In Gazebo, use teleop to drive the robot so that it faces an obstacle within 0.5 metres. Run the keyboard teleop in a free pane:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Once running, you will see the following in the terminal:

```
Reading from the keyboard  and Publishing to Twist!
---------------------------
Moving around:
   u    i    o
   j    k    l
   m    ,    .
```

Use these keys to control the robot:

| Key | Action |
|-----|--------|
| `i` | Move forward |
| `,` | Move backward |
| `j` | Turn left |
| `l` | Turn right |
| `k` | Stop |
| `q` / `z` | Increase / decrease speed |

Press `i` to drive the robot forward slowly toward a wall or object. Watch the Gazebo window in your browser to see the robot moving. Once the robot is within 0.5 metres of the obstacle, the detection should trigger.

Press `k` to stop the robot, and `,` to reverse away from the obstacle.

### 5.2 Check the subscriber output

In the pane running `obstacle_subscriber`, you should see warning messages appear as the robot closes in:

```
[WARN] [obstacle_subscriber]: Obstacle detected!
[WARN] [obstacle_subscriber]: Obstacle detected!
```

When you back the robot away, the output should switch to:

```
[INFO] [obstacle_subscriber]: Path is clear.
```

### 5.3 Monitor the topic directly with the CLI

You can also monitor `/obstacle_alert` directly without running the subscriber node, using the ROS 2 CLI. In any free pane:

```bash
ros2 topic echo /obstacle_alert
```

You should see the boolean values streaming in real time:

```
data: false
---
data: false
---
data: true
---
data: true
---
```

The value should flip to `true` when the robot is close to an obstacle and back to `false` when the path is clear. This is a quick way to verify the publisher is working correctly without needing a subscriber node running.

---

## 6. Verify with rqt_graph

With both nodes running, let's use `rqt_graph` to visually confirm that everything is connected correctly.

### 6.1 Launch rqt_graph

Open a new terminal and run:

```bash
rqt_graph
```

### 6.2 Interpret the graph

You should see a graph that looks roughly like this:

```
[/obstacle_publisher] ──/obstacle_alert──► [/obstacle_subscriber]
```

- The **nodes** (ovals) represent your running ROS 2 nodes
- The **arrows** (edges) represent topic connections
- Your LIDAR topic should also appear as an input edge into `/obstacle_publisher`

If a node or topic is missing from the graph, it means that node isn't running or hasn't been remapped correctly. Use this as your debugging tool!

> **Tip:** Use the dropdown at the top of rqt_graph to toggle between different graph views (e.g. hide dead sinks, show all topics).

---

## Completion Checklist

Before calling this done, make sure you can tick everything off:

- [ ] Gazebo simulation launched with the robot spawned
- [ ] Identified the correct LIDAR topic and message type using `ros2 topic list` and `ros2 topic info`
- [ ] Visualized LIDAR data in RViz with `base_footprint` as the fixed frame
- [ ] Obstacle publisher node running and publishing to `/obstacle_alert`
- [ ] Subscriber node prints warnings when obstacle detected, info when path is clear
- [ ] Drove the robot toward an obstacle and confirmed the subscriber output changed
- [ ] `ros2 topic echo /obstacle_alert` shows `true`/`false` values changing in real time
- [ ] `rqt_graph` shows both nodes connected via `/obstacle_alert`

---

## References

- [ROS 2 Jazzy - Writing a simple publisher and subscriber (Python)](https://docs.ros.org/en/jazzy/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html)
- `ros2 topic list` - list all active topics
- `ros2 topic info <topic>` - show type and publisher/subscriber count
- `ros2 topic echo <topic>` - stream live messages from a topic
- `rviz2` - 3D visualization tool for ROS 2
- `rqt_graph` - visualize node and topic connections
