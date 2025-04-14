#!/bin/bash
# Start script for the WTFGEMINIJOBTASKUI application

echo "██╗    ██╗████████╗███████╗     ██████╗ ███████╗███╗   ███╗██╗███╗   ██╗██╗██╗"
echo "██║    ██║╚══██╔══╝██╔════╝    ██╔════╝ ██╔════╝████╗ ████║██║████╗  ██║██║██║"
echo "██║ █╗ ██║   ██║   █████╗      ██║  ███╗█████╗  ██╔████╔██║██║██╔██╗ ██║██║██║"
echo "██║███╗██║   ██║   ██╔══╝      ██║   ██║██╔══╝  ██║╚██╔╝██║██║██║╚██╗██║██║██║"
echo "╚███╔███╔╝   ██║   ██║         ╚██████╔╝███████╗██║ ╚═╝ ██║██║██║ ╚████║██║██║"
echo " ╚══╝╚══╝    ╚═╝   ╚═╝          ╚═════╝ ╚══════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝╚═╝"
echo "                                                                                "
echo "🚀 JobFit Analyzer Pro - Starting up..."
echo "======================================================"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies."
    exit 1
fi

# Create uploads directory if it doesn't exist
if [ ! -d "uploads" ]; then
    echo "📁 Creating uploads directory..."
    mkdir -p uploads
fi

# Check if OpenRouter API key is set
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❓ OPENROUTER_API_KEY environment variable is not set."
    echo "Please enter your OpenRouter API key:"
    read -s api_key
    export OPENROUTER_API_KEY="$api_key"
    echo "✅ API key set temporarily for this session."
fi

# Start the application
echo "🚀 Starting JobFit Analyzer Pro..."
echo "======================================================"
echo "📱 Access the application at: http://localhost:8080"
echo "💡 Press Ctrl+C to stop the application"
echo "======================================================"

python app.py