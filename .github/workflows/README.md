# GitHub Actions Setup for Pi Deployment

## Setting up Secrets

1. Go to your repository on GitHub: https://github.com/fieldjoshua/LightBox_2.0
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add these secrets:

### Required Secrets:

#### For Pi Zero W (10x10 Matrix):
- **PI_HOST**: `192.168.0.222`
- **PI_USER**: `fieldjoshua`
- **PI_PASSWORD**: Your Pi Zero password
- **PI_PORT**: `22` (default SSH port)

#### For Pi 3B+ (HUB75 Panel):
- **PI_3B_HOST**: `192.168.0.98`
- **PI_3B_USER**: `joshuafield`
- **PI_3B_PASSWORD**: Your Pi 3B+ password
- **PI_3B_PORT**: `22` (default SSH port)

## Usage

### Automatic Sync
Every push to `main` branch will automatically sync the code to your Pi.

### Manual Sync
1. Go to **Actions** tab in your repository
2. Click on "Sync to Raspberry Pi"
3. Click "Run workflow" → "Run workflow"

## What it does

The sync workflow:
1. Connects to your Pi via SSH
2. Updates the code in `~/LightBox_2.0`
3. Installs/updates Python dependencies
4. Leaves the code ready to run

## After Sync

SSH to your Pi and run:
```bash
cd ~/LightBox_2.0
sudo python3 lightbox.py
```

Or set up as a service for auto-start.