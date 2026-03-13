# GCP VM Setup Guide — ROS 2 Bootcamp

**For Windows & macOS Users**

This guide covers setting up a **Virtual Machine (VM)** on Google Cloud Platform (GCP).
Think of a VM as a computer that lives in Google's data center. You will rent it by the minute to run our robot simulations.

---

## Before You Start

### 📍 Where to run commands

Throughout this guide, pay attention to the labels telling you **where** to type the commands:

*   **Cloud Shell** (`>_`): The terminal inside your web browser on the GCP website.
*   **Inside the VM** (`🖥️`): The terminal after you have connected to your running machine.

---

## Step 0: Create Google Cloud Account
> 🌐 **Location: Web Browser**

1.  Go to [console.cloud.google.com](https://console.cloud.google.com).
2.  Sign in with your Google Account.
3.  **Activate your Free Trial:** Look for a banner at the top of the page offering **$300** in free credits and activate it.
    *   *Note: Google asks for a credit card to verify you are not a robot, but you will NOT be charged unless you manually upgrade to a paid account. The free credits are more than enough for this course.*

---

## Step 1: Create a Project
> 🌐 **Location: GCP Console**

1.  Click the project dropdown menu at the top left (next to the "Google Cloud" logo).
2.  Click **New Project**.
3.  Name it: `ros2-bootcamp`.
4.  Click **Create**.
5.  **Important:** Wait for the notification saying it's created, then click **SELECT PROJECT** to switch to it.

---

## Step 2: Enable Compute Engine API
> 🌐 **Location: GCP Console**

We need to tell Google we want to use their "Compute Engine" (Virtual Machines).

1.  In the search bar at the very top, type: `Compute Engine API`.
2.  Click on the result labeled **Compute Engine API**.
3.  Click the blue **ENABLE** button.
    *   *This may take a minute or two.*

---

## Step 3: Open Cloud Shell
> 🌐 **Location: GCP Console**

1.  Look for the icon that looks like a terminal prompt `>_` at the top right of the blue bar.
2.  Click it to open **Cloud Shell**.
3.  A terminal window will appear at the bottom of your screen. This is where you will type the setup commands.

---

## Step 4: Configure Setup Variables
> 💻 **Run in: Cloud Shell**

Copy and paste this entire block into the Cloud Shell terminal and press **Enter**.
This sets up shortcuts so you don't have to type long IDs later.

```bash
# Automatically fetch your Project ID and Number
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# Define the name and location for your VM
VM_NAME="ros2-bootcamp-vm" 
ZONE="asia-southeast1-b"
REGION="asia-southeast1"

# Verify everything looks correct
echo "--------------------------------------"
echo "Project ID:   $PROJECT_ID"
echo "VM Name:      $VM_NAME"
echo "Zone:         $ZONE"
echo "--------------------------------------"
```

> **Check:** If `Project ID` is empty, you didn't select your project in Step 1. Select it and try again.

---

## Step 5: Create the VM Template
> 💻 **Run in: Cloud Shell**

We will create a "template" that defines how powerful our computer should be. We are using a **c2-standard-8** machine (8 CPUs) because robot simulation requires a lot of processing power.

```bash
gcloud beta compute instance-templates create $VM_NAME-template \
  --project=$PROJECT_ID \
  --machine-type=c2-standard-8 \
  --network-interface=network=default,network-tier=PREMIUM,stack-type=IPV4_ONLY \
  --instance-template-region=$REGION \
  --no-restart-on-failure \
  --maintenance-policy=TERMINATE \
  --provisioning-model=SPOT \
  --instance-termination-action=STOP \
  --service-account=$PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/trace.append \
  --create-disk=auto-delete=yes,boot=yes,device-name=$VM_NAME-template,image=projects/ubuntu-os-cloud/global/images/ubuntu-minimal-2404-noble-amd64-v20251217,mode=rw,size=30,type=pd-balanced \
  --create-disk=device-name=persistent-disk-1,mode=rw,size=150,type=pd-standard \
  --no-shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring \
  --reservation-affinity=none
```

> **Note:** We use "SPOT" provisioning. This saves ~60-90% of the cost! Google might turn off your VM if they need the capacity back, but for learning, it's perfect.

---

## Step 6: Create the VM
> 💻 **Run in: Cloud Shell**

Now, create the actual machine from that template.

```bash
gcloud compute instances create $VM_NAME \
  --project=$PROJECT_ID \
  --zone=$ZONE \
  --source-instance-template=https://www.googleapis.com/compute/beta/projects/$PROJECT_ID/regions/$REGION/instanceTemplates/$VM_NAME-template
```

---

## Step 7: Network Setup (Firewall & Static IP)
> 💻 **Run in: Cloud Shell**

We need to open a "door" (port 3000) so you can see the robot simulation in your web browser.

```bash
# 1. Allow browser traffic on port 3000
gcloud compute firewall-rules create allow-kasmvnc \
  --project=$PROJECT_ID \
  --allow=tcp:3000 \
  --source-ranges=0.0.0.0/0 \
  --description="Allow KasmVNC simulation viewer"

# 2. Reserve a Static IP (so your VM address doesn't change)
gcloud compute addresses create $VM_NAME-static-ip \
  --project=$PROJECT_ID \
  --region=$REGION

# 3. Attach the Static IP to your VM
gcloud compute instances delete-access-config $VM_NAME \
  --zone=$ZONE \
  --access-config-name="external-nat"

gcloud compute instances add-access-config $VM_NAME \
  --zone=$ZONE \
  --address=$(gcloud compute addresses describe $VM_NAME-static-ip --region=$REGION --format="value(address)")

echo "Setup Complete! Static IP assigned."
```

---

## Step 8: Connect and Install Software (The Final Step!)
> 💻 **Run in: Cloud Shell**

Now we will log into your new computer to install Docker.

1.  **SSH into the VM:**
    ```bash
    gcloud compute ssh $VM_NAME --zone=$ZONE --project=$PROJECT_ID
    ```
    *(If asked to create SSH keys, just press **Enter** (for Y) and **Enter** twice for no password)*

2.  **Install Tools (Copy-Paste this Block into the VM terminal 🖥️):**
    
    ```bash
    # Update the Linux system
    sudo apt-get update && sudo apt-get upgrade -y
    
    # Install useful tools
    sudo apt-get install -y git nano tmux ruby-full acpid
    
    # Install Tmuxinator (helps run simulation commands)
    sudo gem install tmuxinator
    
    # Install Docker (runs our robot software)
    curl -fsSL https://get.docker.com | sudo sh
    
    # Allow running Docker without 'sudo'
    sudo usermod -aG docker $USER
    
    # Configure auto-shutdown (Saves money! Stops VM if inactive for 5 mins)
    cat <<'EOF' | sudo tee /etc/cron.d/auto_shutdown
    */5 * * * * root [ $(who | wc -l) -eq 0 ] && sudo shutdown -h now
    EOF
    
    echo "🎉 Installation Complete!"
    ```

---

## 🛑 COST MANAGEMENT (READ THIS!)

**You are paying by the second while this VM is running.**

If you leave it running overnight, you will waste your free credits.
**ALWAYS STOP YOUR VM WHEN YOU ARE DONE.**

**How to Stop:**
*   **Web Console:** Go to Compute Engine -> VM Instances -> Select VM -> Click **STOP** (Square icon).
*   **Terminal:** `sudo poweroff`

---

## Next Steps

Your cloud computer is ready! 
Now you need to connect to it properly so you can write code.

👉 **Go to the [Connection Guide](gcp_connect.md)**
