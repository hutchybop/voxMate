#!/bin/bash
# librespot_update.sh - Simple update script for librespot

set -e  # Exit on any error

echo "🔄 Updating librespot..."

# Navigate to source directory
cd ~/downloads/librespot || {
    echo "❌ Error: Cannot find librespot directory"
    exit 1
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull

# Verify build dependencies
echo "🔍 Checking build dependencies..."
if ! cargo build --release --no-default-features --features alsa-backend,pulseaudio-backend,native-tls; then
    echo "❌ Error: Dependency check failed"
    exit 1
fi

# Build latest version
echo "🔨 Building librespot..."
if ! cargo build --release --no-default-features --features alsa-backend,pulseaudio-backend,native-tls; then
    echo "❌ Error: Build failed"
    exit 1
fi

# Verify binary was created
if [ ! -f "target/release/librespot" ]; then
    echo "❌ Error: Build completed but binary not found"
    exit 1
fi

# Copy to system location
echo "📦 Installing new binary..."
if ! sudo cp target/release/librespot /usr/bin/; then
    echo "❌ Error: Failed to copy binary"
    exit 1
fi

# Restart service
echo "🔄 Restarting librespot service..."
if ! sudo systemctl restart librespot; then
    echo "❌ Error: Failed to restart service"
    exit 1
fi

# Wait a moment for service to start
sleep 3

# Check service status
echo "✅ Checking service status..."
if sudo systemctl is-active --quiet librespot; then
    echo "🎉 librespot updated and running successfully!"
else
    echo "⚠️  Warning: Service may not be running properly"
    echo "Check logs with: sudo journalctl -u librespot -f"
fi

# Show new version
echo "📋 New version info:"
/usr/bin/librespot --version 2>/dev/null || echo "Version check failed"

echo "🎊 Update complete!"
