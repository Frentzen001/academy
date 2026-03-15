# 🤖 Autonomous Navigation Mini Challenge

Welcome to the Autonomous Navigation Mini Challenge! In this repository, you will find the base workspace required to complete the integration of an Action Server with the Nav2 stack. 

Your mission is to act as the systems integrator: build the "brain" of the robot to bridge high-level command requests with low-level navigation and mapping, utilizing a provided path-optimization algorithm.



## 📑 Table of Contents
- [Overview](#-overview)
- [System Architecture & Rules](#-system-architecture--rules)
- [Your Mission](#-your-mission)
- [Provided Tools](#-provided-tools)
- [Getting Started](#-getting-started)
- [How to Run](#-how-to-run)

---

## 📋 Overview

You are provided with three ROS2 packages, including an Action Client, an Action Server, and a predefined Action Interface. You need to put these three packages into the existing [Linorobot2 Repo](https://github.com/linorobot/linorobot2/tree/jazzy) src to start.

Your goal is to implement the **Action Server**, integrate the waypoint optimizer, and tune the **SLAM/Nav2 stack** so the robot can smoothly and efficiently execute the optimized route without violating physical constraints.

---

## 🏗️ System Architecture & Rules

To ensure a level playing field, certain parts of the system are strictly locked (Do Not Modify). Focus your engineering efforts entirely on the Action Server logic and navigation tuning.

### Modifiability Matrix

| Component | Status | Description |
| :--- | :---: | :--- |
| **Action Client** | 🔒 **LOCKED** | Initiates the task and sends the goal. Do not modify. |
| **Action Interfaces** | 🔒 **LOCKED** | The `.action` files defining the structure of the goal, feedback, and result. |
| **Robot Physics/Kinematics** | 🔒 **LOCKED** | Start point, max/min velocity, acceleration, mass, inertia, and any other physics properties. |
| **Action Server** | 🛠️ **MODIFIABLE** | **Your core deliverable.** Implement your state machine and logic here. |
| **SLAM & Nav2 Stack** | 🛠️ **MODIFIABLE** | Tune parameters (costmaps, planners, inflation radii) to ensure efficient movement. |

> **⚠️ STRICT RULE:** You may not "cheat" the physics. Altering the robot's physical constraints (e.g., cranking up max velocity, modifying inertia) or manually changing the starting pose is strictly prohibited and will result in a failed evaluation. Your performance relies purely on efficient software integration and parameter tuning.

---

## 🚀 Your Mission

Your primary task is to modify the Action Server node (navwaypoints_server) and tune the navigation stack configurations. 

Your Action Server must successfully:
1. **Receive Goal & Send Feedback, Result:** Accept the goal from the fixed Action Client, and send back feedback and result.
2. **Optimize the Route:** Pass the necessary target data into the provided **Waypoint Optimizer Function** to calculate the best sequence of waypoints.
3. **Execute the Sequence:** Communicate the waypoints sequentially to the Nav2 stack.
4. **Return Feedback & Result:** Pipe standard progress feedback and the final completion result back to the Action Client using the locked Action Interfaces.

Below is the structure of the action interface:
- Request: geometry_msgs/Point[4] waypoints (Array of exactly 4 coordinates for the 2D map)
- Feedback: geometry_msgs/Point last_passed_waypoint (The latest coordinate the robot just passed through)
- Result: int32 status (Server should send 1 when all coordinates are successfully completed)

---

## 💻 Getting Started

### Installation

1. Create a workspace and clone the repository
   ```bash
   cd ~/linorobot2/  # navigate to linorobot2 directory
   git clone https://github.com/humjie/academy.git
   git pull
   git checkout bootcamp-challenge-rules
   cd ~/linorobot2/academy/challenges/  # you can see the provided packages here
   ```
   Then, move the world files into linorobot2_gazebo
   ```bash
   cd ~/linorobot2/academy/challenges/challenge_maps/
   mv final_challenge_map/ ~/linorobot2/linorobot2_gazebo/models/
   mv final_challenge_map.sdf  ~/linorobot2/linorobot2_gazebo/worlds/
   ```

3. Setup your tmux and docker
   ```bash
   cd ~/linorobot2_ws/docker/
   source setup_tmux.bash
   tmuxinator start dev
   ```

4. In your docker, build and run
   ```bash
   cd ~/linorobot2_ws
   colcon build
   source install/setup.bash
   # Run your tasks
   ```

5. If you see the challenge world in gazebo, you are ready and its time to map!

6. Once you are done with mapping, test running navigation in your new map, you should have equipped yourself with all the skills needed from the 'autonomous_navigation' exercise yesterday!

7. The real challenge (Travelling Salesman Problem)
   ```bash
   cd ~/linorobot2/academy/challenges/navigation_waypoints_action
   ```
   Your new challenge starts there! Have fun!

---

## 🏃 How to Run (Shortcut)

For the final challenge, you can use the provided **Tmuxinator** profile to launch all necessary nodes at once (Simulation, Navigation, and your Action Server).

### 1. Setup the Tmuxinator Profile
Copy the `sim_waypoints.yml` file from the challenge folder to your local tmuxinator config directory:
```bash
cp ~/linorobot2/academy/challenges/sim_waypoints.yml ~/linorobot2/docker/profiles
```

### 2. Launch the Environment
Run the following command to start the simulation and your server:
```bash
# Ensure you are in the docker directory where the setup script resides
cd ~/linorobot2_ws/docker/
source setup_tmux.bash
tmuxinator start sim_waypoints
```
This will open a tmux session with:
- **KasmVNC**: For visualizing the simulation.
- **Gazebo**: The simulation environment.
- **Nav2 Stack**: The navigation system.
- **Your Action Server**: Automatically launched via `ros2 run navwaypoints_server ...`.

### 3. Start the Challenge
Once everything is running and you are ready to begin the run:
```bash
# In a new terminal pane or window inside the docker container:
ros2 run navwaypoints_client navwaypoints_client
```

### 4. Retrieve Results (Post-Run)
After the run is complete, retrieve your results for submission:
```bash
# Copy the results file from the container's temp directory
cp /tmp/challenge_results/waypoint_results.pk ~/linorobot2_ws/src/linorobot2/

# (Organisers only) Verify the results
python3 print_results.py ~/linorobot2_ws/src/linorobot2/waypoint_results.pkl
```