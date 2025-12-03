# librespot Installation Guide

## Quick Overview
This guide helps you install librespot with working Spotify Connect functionality on your Raspberry Pi.

---

## Step 1: Check GitHub Repository Status
**Always check latest status first:**
- [Official librespot](https://github.com/librespot-org/librespot) - Primary choice
- [tdgroot fork](https://github.com/tdgroot/librespot/tree/20250807_fixes) - Backup option

**Current Status (3 Dec 2025):**
- Official dev branch: **Recently updated (11 hours ago)** - RECOMMENDED
- tdgroot fork: Last update Aug 7, 2025 - Use as fallback

---

## Step 2: Clone the Repository

### Option A: Official Repository (Recommended)
```bash
cd ~/downloads
git clone https://github.com/librespot-org/librespot.git
cd librespot
git checkout dev  # Use development branch
git pull  # Get latest changes
```

### Option B: tdgroot Fork (Backup if official fails)
```bash
cd ~/downloads
git clone -b 20250807_fixes https://github.com/tdgroot/librespot.git
cd librespot
```

---

## Step 3: Install Dependencies
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required build dependencies
sudo apt install build-essential libasound2-dev libpulse-dev libavahi-compat-libdnssd-dev -y
```

---

## Step 4: Build librespot
```bash
# Build with ALSA + PulseAudio + Native TLS (release mode)
cargo build --release --no-default-features --features alsa-backend,pulseaudio-backend,native-tls

# Verify build completed successfully
ls target/release/librespot
```

---

## Step 5: Install System-Wide
```bash
# Copy binary to system location
sudo cp target/release/librespot /usr/bin/

# Set proper ownership and permissions
sudo chown root:root /usr/bin/librespot
sudo chmod 755 /usr/bin/librespot
```

---

## Step 6: Initial Spotify Authentication
**Important: Do this as your user (not root)**

```bash
# Run OAuth authentication once
/usr/bin/librespot --name "voxMate Pi" --backend pulseaudio --enable-oauth --cache /var/lib/librespot/credentials.json
```

**Authentication Process:**
1. A URL will be displayed in terminal
2. Open this URL in your browser (on any device)
3. Login with your Spotify Premium account
4. Copy the redirect URL from browser
5. Paste it back in the terminal
6. Credentials will be saved to `/var/lib/librespot/credentials.json`

---

## Step 7: Configure systemd Service

### Create Main Service File
```bash
sudo nano /etc/systemd/system/librespot.service
```

**Add this configuration:**
```ini
[Unit]
Description=Librespot Spotify Connect
After=network.target sound.target
Requires=avahi-daemon.service

[Service]
Environment="DEVICE_IP=$(hostname -I | awk '{print $1}')"
Environment="PULSE_SERVER=unix:/run/user/1000/pulse/native"
Environment="XDG_RUNTIME_DIR=/run/user/1000"
ExecStart=/usr/bin/librespot \
    --name "voxMate Pi" \
    --backend pulseaudio \
    --device alsa_output.usb-Jieli_Technology_UACDemoV1.0_4150344C3631390E-00.analog-stereo \
    --cache /var/lib/librespot/credentials.json \
    --bitrate 320 \
    --disable-audio-cache \
    --enable-volume-normalisation \
    --initial-volume 75 \
    --autoplay on \
    --device-type speaker

Restart=unless-stopped
RestartSec=5
User=hutch
Group=hutch

[Install]
WantedBy=multi-user.target
```

### Create Override for Dynamic IP
```bash
sudo mkdir -p /etc/systemd/system/librespot.service.d
sudo nano /etc/systemd/system/librespot.service.d/override.conf
```

**Add this content:**
```ini
[Service]
Environment="DEVICE_IP=$(hostname -I | awk '{print $1}')"
```

---

## Step 8: Enable and Start Service
```bash
# Reload systemd to recognize changes
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable librespot

# Start the service now
sudo systemctl start librespot

# Check service status
sudo systemctl status librespot
```

**Expected output:** `Active: active (running)` in green text.

---

## Step 9: Test Spotify Connect
1. Open Spotify app on your phone
2. Look for "voxMate Pi" in available devices
3. Play music - should hear audio through your USB device

---

## Troubleshooting

### If Tracks Don't Play (HTTP 500 Errors)
**Try these solutions in order:**

1. **Update to latest official dev:**
   ```bash
   cd ~/downloads/librespot
   git pull
   cargo build --release --no-default-features --features alsa-backend,pulseaudio-backend
   sudo cp target/release/librespot /usr/bin/
   sudo systemctl restart librespot
   ```

2. **Try tdgroot fork:**
   ```bash
   cd ~/downloads
   git clone -b 20250807_fixes https://github.com/tdgroot/librespot.git
   cd librespot
   cargo build --release --no-default-features --features alsa-backend,pulseaudio-backend
   sudo cp target/release/librespot /usr/bin/
   sudo systemctl restart librespot
   ```

3. **Try stable v0.4.2 (last resort):**
   ```bash
   cd ~/downloads
   git clone -b v0.4.2 https://github.com/librespot-org/librespot.git
   cd librespot
   cargo build --release --no-default-features --features alsa-backend,pulseaudio-backend
   sudo cp target/release/librespot /usr/bin/
   sudo systemctl restart librespot
   ```

### Common Issues
- **Permission denied:** Ensure `/var/lib/librespot/` exists and user `hutch` owns it
- **Audio not working:** Check PulseAudio sink names with `pactl list sinks`
- **Service fails:** Check logs with `sudo journalctl -u librespot -f`

### Update Process
**Whenever you want to update librespot:**
1. `cd ~/downloads/librespot`
2. `git pull`
3. `cargo build --release --no-default-features --features alsa-backend,pulseaudio-backend`
4. `sudo cp target/release/librespot /usr/bin/`
5. `sudo systemctl restart librespot`

---

## Notes
- This guide uses PulseAudio backend for better compatibility with voxMate
- Always backup working credentials before major changes
- Spotify Premium account required for librespot functionality
- USB audio device: `alsa_output.usb-Jieli_Technology_UACDemoV1.0_4150344C3631390E-00.analog-stereo`

---

## Step 10: Easy Updates with Update Script

### Create Update Script
The update script has been created at `~/voxMate/librespot_update.sh`

### Usage
```bash
# Run update anytime new librespot fixes are available
~/downloads/librespot_update.sh
```

### What the Script Does
1. ✅ Navigates to your librespot directory
2. 📥 Pulls latest changes from git
3. 🔍 Verifies build dependencies
4. 🔨 Builds new binary with your settings
5. 📦 Copies binary to system location
6. 🔄 Restarts librespot service
7. ✅ Verifies service is running
8. 📋 Shows new version info

### Manual Update Steps (Alternative)
If you prefer manual updates:
```bash
cd ~/downloads/librespot
git pull
cargo build --release --no-default-features --features alsa-backend,pulseaudio-backend
sudo cp target/release/librespot /usr/bin/
sudo systemctl restart librespot
```

### Quick Update Commands
```bash
# Check for updates first
cd ~/downloads/librespot && git log --oneline -3

# If updates available, run:
~/downloads/librespot_update.sh

# Check current version
/usr/bin/librespot --version

# Check service status
sudo systemctl status librespot
```

---

## Quick Reference Commands

| Purpose | Command |
|----------|----------|
| **Update librespot** | `~/downloads/librespot_update.sh` |
| **Check version** | `/usr/bin/librespot --version` |
| **Check service** | `sudo systemctl status librespot` |
| **View logs** | `sudo journalctl -u librespot -f` |
| **Check for updates** | `cd ~/downloads/librespot && git log --oneline -3` |

