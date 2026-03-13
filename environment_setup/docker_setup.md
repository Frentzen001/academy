# Docker Simulation Setup Guide

> **Target Audience:** Everyone! (Whether you are on a Local Ubuntu machine or a Cloud VM).

This guide will install the **linorobot2** simulation environment. We use **Docker** to run the simulation.

Reference: [linorobot2 Docker documentation](https://linorobot.github.io/linorobot2/docker/)

Think of Docker like a "shipping container" — everything the robot needs (ROS 2, Gazebo, libraries) is packed inside. You just run the container, and it works, without messing up your own computer.

---

## Prerequisites (Locals Only) 🛠️

> **GCP Users:** You installed Docker in the previous guide. **Skip to Step 1.**

**Local Ubuntu Users:**
You need Docker installed on your laptop to run the robot container.

1.  **Check if you have it:**
    ```bash
    docker --version
    ```
    If you see a version number, you are ready!

2.  **If not installed:**
    Run this to install it and configure permissions:
    ```bash
    # Install Docker
    curl -fsSL https://get.docker.com | sudo sh

    # Allow running without 'sudo'
    sudo usermod -aG docker $USER
    ```
    ⚠️ **Important:** After installing, **restart your computer** (or log out and back in) for the permission changes to work.

---

## Step 1: Clone the Repository
*Where to run: In your terminal (Local Ubuntu terminal or VS Code SSH terminal).*

Download the simulation code:

```bash
git clone https://github.com/linorobot/linorobot2
cd linorobot2
```

> **Note:** All future commands must be run from inside this `linorobot2` folder.

---

## Step 2: Configure the Environment

We need to tell Docker if you have a graphics card (GPU) or not.

1.  Enter the docker folder:
    ```bash
    cd docker
    ```
2.  Open the settings file:
    ```bash
    nano .env
    ```
3.  **Edit the `BASE_IMAGE` line:**

    *   **For GCP VM Users:** Change it to `gazebo` (GCP VMs don't have GPUs).
    *   **For Local Users (No NVIDIA GPU):** Change it to `gazebo`.
    *   **For Local Users (With NVIDIA GPU):** Keep it as `gazebo-cuda`.

    It should look like this (for most of you):
    ```bash
    BASE_IMAGE=gazebo
    ```

4.  **Save & Exit:** Press `Ctrl+O` -> `Enter` -> `Ctrl+X`.

---

## Step 3: Build the Docker Image

This step effectively "installs" the robot computer. It downloads about 3-4GB of data and compiles it.

```bash
./build
```

This will build the image with your host user's permissions so files created inside the container are owned by you. This step may take a few minutes the first time.

### 1.3 - Install Tmuxinator

Tmuxinator manages named tmux sessions from a YAML config. It acts like a launch file for the entire simulation stack, starting all required containers and arranging their output into named panes in one terminal.

Follow the installation instructions at: https://github.com/tmuxinator/tmuxinator?tab=readme-ov-file#installation

For Ubuntu / Debian (inside your VM or local machine):

```bash
sudo apt update
sudo apt install -y tmuxinator
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
cd docker
source setup_tmux.bash
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

This starts the `dev` container and a KasmVNC server, then opens a tmux window with four bash panes ready for development.

> **Tip:** The `linorobot2_ws/src` directory inside the container is a shared volume — it maps directly to the `linorobot2_ws/src` folder inside the cloned repository on your host machine. This means you can open and edit files from your host using your favourite IDE, and changes will be immediately visible inside the container without any copying or syncing.

Once everything is up, open your browser and go to:

- **Local / SSH Tunnel:** `http://localhost:3000`
- **GCP Static IP:** `http://<YOUR_STATIC_IP>:3000`

You will see the Gazebo simulation running in the browser window. A robot will be spawned in the world and ready to use. The tmux session opens 6 independent terminals you can use to follow the exercises in this repository.

> **Note:** The first time you use any of the 6 terminals, remember to source the workspace:
> ```bash
> source ~/linorobot2_ws/install/setup.bash
> ```

> **Note:** The standard way to work with ROS is through a native system installation (see [Ubuntu Development Setup](https://docs.ros.org/en/jazzy/Installation/Alternatives/Ubuntu-Development-Setup.html)). This Docker + Tmuxinator approach is simply a convenient way to quickly get through the exercises in this repository without a full system install.

### Navigating the Tmux Session

Once the session is running, you will see multiple panes in your terminal. Each pane is an interactive shell exec'd into the `dev` container.

This setup uses **tmux** (terminal multiplexer). Here are the essential commands:

| Action | Key Binding |
| :--- | :--- |
| **Move between panes** | `Ctrl+B` then `Arrow Keys` |
| **Close current pane** | `Ctrl+D` (or type `exit`) |
| **Detach session** (keep running) | `Ctrl+B` then `D` |
| **Scroll Mode** (view history) | `Ctrl+B` then `[` (Use arrows/PgUp/PgDn, press `q` to exit) |
| **Zoom Pane** (maximize/restore) | `Ctrl+B` then `z` |

💡 **Pro Tip:** If your terminal seems frozen, check if you accidentally pressed `Ctrl+S` (flow control off). Press `Ctrl+Q` to unfreeze it.

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

## Useful Commands

| Step | Command |
|------|---------|
| Clone | `git clone https://github.com/linorobot/linorobot2 && cd linorobot2` |
| Configure | Edit `docker/.env`, set `BASE_IMAGE=gazebo` |
| Build | `cd docker && ./build` |
| Install Tmuxinator | `sudo apt install tmuxinator` |
| Register profiles | `source docker/setup_tmux.bash` |
| Start session | `tmuxinator start dev` |
| Open browser | `http://<host_ip>:3000` |
| Source workspace | `source ~/linorobot2_ws/install/setup.bash` |
| Stop session | `tmuxinator stop dev` |


## Shutting Down

When you are finished with your session:

1.  **Stop the simulation:**
    Press `Ctrl+B` then type `:kill-session` and press `Enter`.
    *Or run `tmuxinator stop dev` if you are detached.*

2.  **Stop your VM (Important for GCP Users!):**
    Don't forget to stop your cloud instance to save credits.