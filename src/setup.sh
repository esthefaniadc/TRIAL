#!/bin/bash

# Buck Converter Control System Setup Script
# This script sets up the development environment for the ESP32 buck converter project

echo "=================================================="
echo "Buck Converter Control System Setup"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✅ pip3 found"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Check if PlatformIO is installed (optional)
if command -v pio &> /dev/null; then
    echo "✅ PlatformIO found"
    echo "📝 You can build the ESP32 project with: pio run"
    echo "📝 Upload to ESP32 with: pio run --target upload"
else
    echo "⚠️  PlatformIO not found (optional)"
    echo "   Install with: pip install platformio"
    echo "   Or use Arduino IDE to compile esp32_buck_controller.ino"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p data

# Set executable permissions for scripts
chmod +x api_test_client.py

echo ""
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Hardware Setup:"
echo "   - Build the buck converter circuit (see schemes/buck_converter_circuit.md)"
echo "   - Connect ESP32 as specified in the documentation"
echo ""
echo "2. ESP32 Configuration:"
echo "   - Update WiFi credentials in esp32_buck_controller.ino"
echo "   - Update API endpoint URL"
echo "   - Upload code to ESP32"
echo ""
echo "3. Start the API Server:"
echo "   python3 cloud_api.py"
echo ""
echo "4. Test the System:"
echo "   python3 api_test_client.py --command health"
echo "   python3 api_test_client.py --command test --count 10"
echo ""
echo "📚 For detailed instructions, see src/README.md"
echo ""