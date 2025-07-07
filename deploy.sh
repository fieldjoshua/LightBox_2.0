#!/bin/bash

# Deploy LightBox to Raspberry Pi
# Usage: ./deploy.sh

REMOTE_USER="fieldjoshua"
REMOTE_HOST="192.168.0.222"
REMOTE_PATH="/home/fieldjoshua/LightBox"

echo "🚀 Deploying LightBox to $REMOTE_USER@$REMOTE_HOST"
echo "Target directory: $REMOTE_PATH"
echo ""

# Create remote directory
echo "Creating remote directory..."
ssh $REMOTE_USER@$REMOTE_HOST "mkdir -p $REMOTE_PATH"

# Copy all files
echo "Copying files..."
scp -r ./* $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/

# Set permissions
echo "Setting permissions..."
ssh $REMOTE_USER@$REMOTE_HOST "chmod +x $REMOTE_PATH/setup.sh $REMOTE_PATH/CosmicLED.py"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps on the Raspberry Pi:"
echo "1. SSH into your Pi: ssh $REMOTE_USER@$REMOTE_HOST"
echo "2. Navigate to: cd $REMOTE_PATH"
echo "3. Run setup: ./setup.sh"
echo "4. Start LightBox: sudo ./venv/bin/python3 CosmicLED.py"
echo ""
echo "Web interface will be available at:"
echo "  http://$REMOTE_HOST:5000"