#!/bin/bash

# =============================================================================
# Create macOS Desktop Application for N8n Agent
# =============================================================================

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_NAME="N8n Agent"
APP_DIR="$HOME/Applications/$APP_NAME.app"

echo "Creating macOS application bundle..."

# Create app bundle structure
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Create Info.plist
cat > "$APP_DIR/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>N8n Agent</string>
    <key>CFBundleDisplayName</key>
    <string>N8n Agent</string>
    <key>CFBundleIdentifier</key>
    <string>com.modini.n8n-agent</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleExecutable</key>
    <string>N8nAgent</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Create launcher script
cat > "$APP_DIR/Contents/MacOS/N8nAgent" << EOF
#!/bin/bash

# Set working directory
cd "$SCRIPT_DIR"

# Launch in a new Terminal window
osascript -e 'tell application "Terminal"
    do script "cd \"$SCRIPT_DIR\" && ./launch_n8n_agent.sh desktop open && echo \"\" && echo \"N8n Agent is running!\" && echo \"Close this window to keep it running in background.\" && sleep 5"
    activate
end tell'
EOF

chmod +x "$APP_DIR/Contents/MacOS/N8nAgent"

# Create a simple icon (using emoji as placeholder)
# For a proper icon, you would create an .icns file
cat > "$APP_DIR/Contents/Resources/AppIcon.icns" << 'EOF'
This is a placeholder. For a real icon, create an .icns file.
EOF

echo "Application created at: $APP_DIR"
echo ""
echo "To use:"
echo "1. Open Finder"
echo "2. Navigate to ~/Applications"
echo "3. Double-click 'N8n Agent.app'"
echo ""
echo "To add to Dock:"
echo "1. Open the app once"
echo "2. Right-click the Dock icon"
echo "3. Select 'Options > Keep in Dock'"
echo ""

# Create a simple Alfred/Spotlight launcher
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/n8n-agent" << EOF
#!/bin/bash
cd "$SCRIPT_DIR"
./launch_n8n_agent.sh "\$@"
EOF
chmod +x "$HOME/.local/bin/n8n-agent"

echo "Command-line launcher created: n8n-agent"
echo "Usage: n8n-agent [minimal|desktop|open|foreground]"
