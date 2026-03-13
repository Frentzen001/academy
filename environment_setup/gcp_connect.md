# GCP VM Connection Guide

Now that your Cloud VM is running, you need a way to control it.

We offer two ways to connect. **We strongly recommend Option 2** for the best experience.

| Option | Best For... | Description |
| :--- | :--- | :--- |
| **Option 1: Quick Connect** | Quick fixes | Use the terminal in your browser. Fast, but hard to write code. |
| **Option 2: VS Code** | **Writing Code** | Makes the cloud computer feel like it's on your laptop. Full file explorer, code completion, etc. |

---

## Option 1: Quick Connect (Terminal)

This uses the "SSH Tunnel" method to securely forward the simulation viewer to your laptop.

1.  Open **Google Cloud Shell** (`>_` icon at [console.cloud.google.com](https://console.cloud.google.com)).
2.  Copy and paste this "Magic Command". It detects your VM and connects:

```bash
export PROJECT_ID=$(gcloud projects list --format='value(projectId)') && export ZONE=$(gcloud compute instances list --project=$PROJECT_ID --format='value(zone)') && export VM_NAME=$(gcloud compute instances list --project=$PROJECT_ID --format='value(name)') && export PORT=3000 && echo "PROJECT_ID: $PROJECT_ID" && echo "ZONE: $ZONE" && echo "VM_NAME: $VM_NAME" && echo "PORT: $PORT"
```

It will output something like:
```
PROJECT_ID: development-vm-402010
ZONE: asia-southeast1-b
VM_NAME: my-vm
PORT: 3000
```

### Step 3: SSH with Port Forwarding

```bash
gcloud compute ssh $VM_NAME \
  --zone=$ZONE \
  --tunnel-through-iap \
  --project=$PROJECT_ID \
  -- -L $PORT:localhost:$PORT
```

3.  Once connected, you can open `http://localhost:3000` in your **local** Chrome/Edge browser to see the simulator (when it's running).

---

## Option 2: VS Code Remote (Recommended) 🏆

This setup allows you to use your local VS Code to edit files that are actually sitting on the Google Cloud Server.

### Phase 1: Preparation (Do this once)

**Step 1: Install Prerequisites**
1.  Install **VS Code** on your laptop.
2.  Open VS Code -> Extensions (Square icon on left).
3.  Search for `Remote-SSH` (by Microsoft) and install it.

**Step 2: Find your Username**
1.  Go to the [GCP Cloud Shell](https://ssh.cloud.google.com/cloudshell).
2.  Run the command `whoami`.
3.  **Write this down.** This is your Linux username (e.g., `john_doe`). You MUST use this exact name so you can access your files.

**Step 3: Generate an SSH Key Key**
This creates a digital "key card" on your laptop to unlock the cloud computer.
Open **PowerShell** (Windows) or **Terminal** (Mac/Linux) on your laptop and run:

**Windows (PowerShell):**
```powershell
# Create the .ssh folder if it doesn't exist
mkdir $HOME\.ssh -ErrorAction SilentlyContinue

# Generate the key (Replace 'john_doe' with YOUR username from Step 2)
ssh-keygen -t rsa -f $HOME\.ssh\gcp_key -C "john_doe"
```

**macOS / Linux:**
```bash
# Create folder
mkdir -p ~/.ssh

# Generate key (Replace 'john_doe' with YOUR username from Step 2)
ssh-keygen -t rsa -f ~/.ssh/gcp_key -C "john_doe"
```
*(Press Enter twice to skip adding a password).*

**Step 4: Upload the Key to Google**
1.  Get the text of your public key:
    *   **Windows:** `Get-Content $HOME\.ssh\gcp_key.pub`
    *   **Mac/Linux:** `cat ~/.ssh/gcp_key.pub`
2.  Copy the **entire output** (starts with `ssh-rsa`... ends with your username).
3.  Go to [GCP Console -> Compute Engine -> VM Instances](https://console.cloud.google.com/compute/instances).
4.  Click **Your VM Instance Name** -> **Edit** -> Scroll down and find SSH keys -> **Add Item**.
5.  Paste your public key and click **Save**.

### Phase 2: Connecting (Do this daily)

1.  Find your VM's **External IP Address** (Go to [VM Instances page](https://console.cloud.google.com/compute/instances)).
2.  Open **VS Code**.
3.  Press `F1` (or Ctrl+Shift+P) and type: `Remote-SSH: Connect to Host...`.
4.  Select **Add New SSH Host...**
5.  Enter this command (replace with your details):
    ```bash
    ssh -i ~/.ssh/gcp_key YOUR_USERNAME@YOUR_VM_IP
    ```
    *(Example: `ssh -i ~/.ssh/gcp_key john_doe@34.12.123.44`)*
6.  Select the configuration file to save to (usually the first option).
7.  Click **Connect** on the popup (bottom right).
8.  Select **Linux** as the platform.
9.  Select **Continue** if asked about the fingerprint.

You are now connected! The bottom-left corner of VS Code should show the IP address.

🎉 **Success!** You will see a green bar at the bottom left showing the SSH connection. You can now Open Folder -> `/home/your_username/` to see your files.

---

## Next Steps

Now you have a computer and a connection!
Let's install the actual robot software.

👉 **Go to the [Docker Setup Guide](docker_setup.md)**


## Appendix: Manual Connection (For Multiple VMs)

If you have multiple VM instances, the auto-detection script in Option 1 might pick the wrong one. Use this manual method instead.

### Step 1: Open Google Cloud Shell

Go to [https://shell.cloud.google.com/](https://shell.cloud.google.com/) and open a Cloud Shell session.

### Step 2: List All Projects and Instances

Run this to see all available projects and instances:

```bash
PROJECT_ID=$(gcloud projects list --format='value(projectId)') && echo "PROJECT_ID: $PROJECT_ID" && gcloud compute instances list --project=$PROJECT_ID --format="table(name:label=VM_NAME,zone:label=ZONE)"
```

It will output something like:
```
PROJECT_ID: development-vm-402010
VM_NAME      ZONE
my-vm-1      asia-southeast1-b
my-vm-2      asia-southeast1-b
my-vm-3      us-central1-a
```

### Step 3: Set Environment Variables

Pick the instance you want to connect to and set the variables manually:

```bash
export PROJECT_ID="<YOUR_PROJECT_ID>"
export ZONE="<YOUR_ZONE>"
export VM_NAME="<YOUR_VM_NAME>"
export PORT=3000
```

### Step 4: SSH with Port Forwarding

```bash
gcloud compute ssh $VM_NAME \
  --zone=$ZONE \
  --tunnel-through-iap \
  --project=$PROJECT_ID \
  -- -L $PORT:localhost:$PORT
```

Once connected, your VM's port `3000` will be accessible at `localhost:3000` in your browser or local tools.

---

## Notes

### About `PORT`
- Port is always `3000` for this setup — no changes needed.
