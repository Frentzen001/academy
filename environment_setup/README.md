# Environment Setup Guide

Welcome to the ROS 2 Bootcamp environment setup! 🚀

This guide will help you prepare your computer to run the robot simulations we'll be using in class.

## 🧭 Which path should I choose?

Because ROS 2 (Robot Operating System) runs natively on Linux (Ubuntu), your setup path depends on your computer's operating system.

| IF YOU HAVE... | YOUR PATH IS... | WHAT THIS MEANS... |
| :--- | :--- | :--- |
| **Ubuntu Linux** | **Path A: Local Setup** | You will run everything directly on your own laptop. |
| **Windows / macOS** | **Path B: Cloud Setup** | You will rent a powerful computer on Google Cloud (GCP) and control it remotely. |

---

## Path A: Local Setup (Ubuntu Users)
**Choose this if:** You have a computer running Ubuntu 22.04 or 24.04 physically installed.

1.  Open the [Docker Setup Guide](docker_setup.md).
2.  Follow the instructions from the beginning to set up Docker, build the image, and start the simulation.

---

## Path B: Cloud Setup (Windows / macOS Users)
**Choose this if:** You are using Windows, macOS, or a Linux distribution other than Ubuntu.

Since your OS doesn't support ROS 2 natively in the same way, we will set up a **Virtual Machine (VM)** on Google Cloud Platform. Think of this as renting a powerful Linux computer in the cloud that you can access from your laptop.

### Phase 1: Create the Cloud Machine ☁️
1.  Open the [GCP VM Setup Guide](gcp_vm_setup.md).
2.  Follow **Steps 0 through 8** to create your VM, configure the network, and install the necessary tools.

### Phase 2: Connect to the Machine 🔗
You need a way to control your cloud computer.
1.  Open the [GCP Connection Guide](gcp_connect.md).
2.  We highly recommend **Option 2: VS Code Remote** as it gives you a full code editor experience.

### Phase 3: Install the Project 📦
Now that you are connected to your cloud computer:
1.  Open the [Docker Setup Guide](docker_setup.md).
2.  **Skip the "Prerequisites"** (since we handled them in Phase 1).
3.  Start at **Step 1.0 - Clone the repository**.
4.  Proceed with building the image and starting the session.
