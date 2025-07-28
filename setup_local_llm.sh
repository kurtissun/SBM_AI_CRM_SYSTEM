#!/bin/bash

# Setup Local LLM for Cost-Free Generative Segmentation
echo "🚀 Setting up Local LLM for Customer Segmentation..."

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Ollama if not present
if ! command_exists ollama; then
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    
    if [ $? -eq 0 ]; then
        echo "✅ Ollama installed successfully"
    else
        echo "❌ Ollama installation failed"
        exit 1
    fi
else
    echo "✅ Ollama already installed"
fi

# Start Ollama service
echo "🔄 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for service to start
sleep 5

# Pull required models
echo "📥 Downloading LLM models (this may take a few minutes)..."

echo "Pulling Llama 3.2 3B model..."
ollama pull llama3.2:3b

if [ $? -eq 0 ]; then
    echo "✅ Llama 3.2 3B model downloaded"
else
    echo "⚠️  Llama 3.2 failed, trying Qwen 2.5..."
    ollama pull qwen2.5:3b
    
    if [ $? -eq 0 ]; then
        echo "✅ Qwen 2.5 3B model downloaded"
    else
        echo "❌ All model downloads failed"
        kill $OLLAMA_PID 2>/dev/null
        exit 1
    fi
fi

# Test the installation
echo "🧪 Testing LLM functionality..."
TEST_RESPONSE=$(ollama run llama3.2:3b "Say 'LLM Ready' in one line" 2>/dev/null)

if [[ $TEST_RESPONSE == *"LLM Ready"* ]]; then
    echo "✅ LLM test successful!"
    echo "🎉 Local LLM setup complete!"
    echo ""
    echo "📋 What's been installed:"
    echo "  • Ollama (local LLM runtime)"
    echo "  • Llama 3.2 3B or Qwen 2.5 3B model"
    echo "  • Service running on localhost:11434"
    echo ""
    echo "💡 Your system now supports:"
    echo "  • Cost-free generative customer segmentation"
    echo "  • Intelligent segment naming and insights"
    echo "  • Context-aware Chinese market analysis"
    echo "  • Flexible, adaptive customer profiling"
    echo ""
    echo "🚀 Ready to use generative segmentation!"
else
    echo "⚠️  LLM test failed, but installation may still work"
    echo "   Try: ollama run llama3.2:3b 'Hello world'"
fi

# Keep Ollama running
echo "🔄 Ollama service will continue running in background"
echo "   To stop: killall ollama"
echo "   To restart: ollama serve"

# Install Python requirements
if [ -f "requirements_llm.txt" ]; then
    echo "📦 Installing Python LLM requirements..."
    pip install -r requirements_llm.txt
    echo "✅ Python requirements installed"
fi

echo ""
echo "🎯 Next steps:"
echo "1. Upload customer data via the interface"
echo "2. Enable 'Auto-segment customers' option"
echo "3. Watch as the LLM generates intelligent segments!"
echo "4. Review generative insights and recommendations"