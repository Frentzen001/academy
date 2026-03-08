# Environment Setup: linorobot2 Docker with Tmuxinator

This guide walks you through getting the simulation environment up and running using the linorobot2 Docker setup.

Reference: [linorobot2 Docker documentation](https://linorobot.github.io/linorobot2/docker/)

---

## 1. One-Time Setup

> If the Docker image has already been built and Tmuxinator is installed, skip to Part 2.

### Prerequisites

- Docker and Docker Compose installed on your machine
- The linorobot2 repository cloned locally
- A terminal at the repository root

### 1.1 - Configure the Docker environment

Navigate into the `docker` folder and open the `.env` file:

```bash
cd docker
nano .env
```

> **Note:** The settings below are for the **simulation setup** used in this course.
> If you are setting up a physical robot, you will also need to configure `ROBOT_BASE`,
> `LASER_SENSOR`, and `DEPTH_SENSOR` in the same file — refer to the
> [official docs](https://linorobot.github.io/linorobot2/docker/) for those values.

Set `BASE_IMAGE` to target Gazebo simulation:

```
BASE_IMAGE=gazebo
```

If your machine has an NVIDIA GPU, use this instead for hardware-accelerated rendering:

```
BASE_IMAGE=gazebo-cuda
```

Save and close the file.

### 1.2 - Build the Docker image

From inside the `docker` folder, run the build script:

```bash
./build
```

This will build the image with your host user's permissions so files created inside the container are owned by you. This step may take a few minutes the first time.

### 1.3 - Install Tmuxinator

Tmuxinator manages named tmux sessions from a YAML config. It acts like a launch file for the entire simulation stack, starting all required containers and arranging their output into named panes in one terminal.

Follow the installation instructions at: https://github.com/tmuxinator/tmuxinator?tab=readme-ov-file#installation

A quick install on Ubuntu:

```bash
sudo apt install tmuxinator
```

---

## 2. Starting the Development Session

> Start here if the Docker image has already been built and Tmuxinator is installed.

### Prerequisites

- The linorobot2 Docker image has been built
- Tmuxinator is installed
- A terminal at the repository root

### 2.1 - Set the Tmuxinator config path

Source the tmux setup script to register the linorobot2 profiles with Tmuxinator:

```bash
source docker/setup_tmux.bash
```

Verify that the profiles are detected:

```bash
tmuxinator ls
```

You should see:

```
tmuxinator projects:
dev       hardware  sim
```

### 2.2 - Start the dev session

Launch the dev profile:

> **Note:** This course uses the `dev` profile rather than `sim`. The `sim` profile
> auto-launches a full Nav2 demo stack, whereas `dev` gives you four independent
> bash panes so you can manually launch and control each ROS 2 process yourself.

```bash
tmuxinator start dev
```

This starts the `dev` container and a KasmVNC server, then opens a tmux window with four bash panes ready for development. Once everything is up, open your browser and go to:

```
http://<your_machine_ip>:3000
```

You will see the Gazebo simulation running in the browser window. A robot will be spawned in the world and ready to use.

### Navigating the Tmux Session

Once the session is running, you will see multiple panes in your terminal. Each pane is an interactive shell exec'd into the `dev` container.

Useful key bindings:

| Keys | Action |
|------|--------|
| `Ctrl+B` then arrow keys | Move between panes |
| `Ctrl+B` then `D` | Detach from the session (everything keeps running) |

To reattach to a detached session:

```bash
tmux attach -t dev
```

### 2.3 - Verify the environment

In any free pane, confirm ROS 2 is active:

```bash
ros2 topic list
```

You should see:

```
ros@sim:~/linorobot2_ws$ ros2 topic list
/parameter_events
/rosout
```

This confirms the ROS 2 environment is up. No extra sourcing is needed - the ROS 2 environment is sourced automatically when each pane starts.

To use packages from the linorobot2 workspace, source it once in your pane:

```bash
source ~/linorobot2_ws/install/setup.bash
```

### Stopping the Session

To stop the session, first detach if you are attached (`Ctrl+B` then `D`), then run:

```bash
tmuxinator stop dev
```

To fully remove all running containers:

```bash
cd docker
docker compose down
```

---

## Summary

| Step | Command |
|------|---------|
| Configure | Edit `docker/.env`, set `BASE_IMAGE=gazebo` |
| Build | `cd docker && ./build` |
| Install Tmuxinator | `sudo apt install tmuxinator` |
| Register profiles | `source docker/setup_tmux.bash` |
| Start session | `tmuxinator start dev` |
| Open browser | `http://<host_ip>:3000` |
| Source workspace | `source ~/linorobot2_ws/install/setup.bash` |
| Stop session | `tmuxinator stop dev` |
