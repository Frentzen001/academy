# Daily Development Workflow ⚡

> **Prerequisite:** You must have completed the [Environment Setup](README.md) before using this guide.

Use this guide every time you want to start working on the robot exercises.

---

## 1. Start Your Cloud VM (GCP Users Only)

> **Skip this if acts as a local Ubuntu machine.**

Your cloud computer costs money while it is running. Only start it when you are ready to work.

**Method A: Visual Console**
1.  Go to [GCP Compute Instances](https://console.cloud.google.com/compute/instances).
2.  Check the box next to your VM instance.
3.  Click **Start / Resume** (Play icon) at the top.
4.  **Wait** for the green checkmark and copy the **External IP** (it often changes!).

**Method B: Command Line**
(If you have `gcloud` configured locally)
```bash
gcloud compute instances start YOUR_VM_NAME --zone=YOUR_ZONE
```

---

## 2. Connect to the Machine

**Option 1: Local Terminal (Recommended for Running Robot)**
Use this for `tmuxinator` commands and controlling the robot.
```bash
# Replace with your actual username and IP
ssh -i ~/.ssh/gcp_key -L 3000:localhost:3000 YOUR_USERNAME@YOUR_VM_IP
```

**Option 2: VS Code (Recommended for Coding)**
Use this for writing code.
1.  Open VS Code.
2.  `F1` -> `Remote-SSH: Connect to Host...`.
3.  (If IP changed) `Remote-SSH: Open Configuration File...` and update the `HostName` with the new IP.
4.  Connect.

---

## 3. Start the Simulation

1.  **Navigate to the docker folder:**
    ```bash
    cd ~/linorobot2/docker
    ```

2.  **Register Tmux Profiles:** (Required every time)
    ```bash
    source setup_tmux.bash
    ```

3.  **Choose your mode:**

    | Mode | Command | Best For... |
    | :--- | :--- | :--- |
    | **Quick Launch** | `tmuxinator start sim` | Verify the setup. Automatically launches the robot & world. |
    | **Development** | `tmuxinator start dev` | **Class Exercises.** Gives you empty terminals to run commands yourself. |

4.  **View the Simulation:**
    Open [http://localhost:3000](http://localhost:3000) in your web browser.

**Optional: Enable Mouse Support**  
Run this command once to enable mouse support (scrolling, clicking panes). If asked, this also reloads the configuration:
```bash
echo "set -g mouse on" > ~/.tmux.conf && tmux source-file ~/.tmux.conf
```

This setup uses **tmux** (terminal multiplexer). Here are the essential commands:

| Action | Key Binding |
| :--- | :--- |
| **Move between panes** | `Ctrl+B` then `Arrow Keys` (Note: Often unreliable in VS Code) |
| **Switch pane by number** | `Ctrl+B` then `q` then `Pane Number` (Recommended for VS Code) |
| **Close current pane** | `Ctrl+D` (or type `exit`) |
| **Detach session** (keep running) | `Ctrl+B` then `D` |
| **Scroll Mode** (view history) | `Ctrl+B` then `[` (Use arrows/PgUp/PgDn, press `q` to exit) |
| **Zoom Pane** (maximize/restore) | `Ctrl+B` then `z` |

💡 **Pro Tip:** If your terminal seems frozen, check if you accidentally pressed `Ctrl+S` (flow control off). Press `Ctrl+Q` to unfreeze it.

---

## Alternative: Manual Terminal Workflow (No Tmux)

If you find `tmux` confusing or hard to navigate, you can use standard terminal windows instead. Instead of running `tmuxinator`, follow these steps for **every new terminal** you need:

1.  **Open a new terminal** in VS Code (`Terminal` -> `New Terminal`).
2.  **Navigate to the docker folder:**
    ```bash
    cd ~/linorobot2/docker
    ```
3.  **Enter the development environment:**
    ```bash
    export DISPLAY=200 && ./dev
    ```

You can repeat this process as many times as needed to have multiple terminals open. Each `./dev` command places you inside the same running Docker container.

---

## 4. Stopping Your Session (Critical) 🛑

When you are done, you **must** shut everything down to avoid losing work or paying for idle cloud time.

**Step 1: Stop the Simulation**

To ensure your computer doesn't get slow and to prevent errors next time you start, you must stop the running Docker containers.

*   **If using Tmux:**
    1.  Press `Ctrl+B`, then type `:kill-session` and press `Enter`.
    2.  *(Or run `tmuxinator stop dev` in a terminal)*.

*   **If using Manual Terminals:**
    1.  If you have programs running (like the robot simulation), press `Ctrl+C` in their terminals to stop them.
    2.  Type `exit` in each terminal to leave the Docker container. You will see your command prompt change back to the normal one.
    3.  **Important:** Run this command to stop the Docker background processes:
        ```bash
        # Run this in the ~/linorobot2/docker folder
        docker compose down
        ```

**Step 2: Stop the Cloud VM**
**⚠️ YOU MUST DO THIS TO STOP BILLING.**

1.  Go to [GCP Compute Instances](https://console.cloud.google.com/compute/instances).
2.  Select your VM.
3.  Click **Stop**.

*(Or use the command line: `gcloud compute instances stop YOUR_VM_NAME`)*
