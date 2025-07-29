#!/bin/bash

echo "🚀 Starting SBM AI CRM Frontend..."
echo "📂 Building production version..."

npm run build

echo "🌐 Starting server on port 9000..."
cd dist

# Try multiple server options
if command -v python3 &> /dev/null; then
    echo "Using Python HTTP Server"
    python3 -m http.server 9000
elif command -v serve &> /dev/null; then
    echo "Using Node.js serve"
    serve -s . -l 9000
elif command -v php &> /dev/null; then
    echo "Using PHP built-in server"
    php -S localhost:9000
else
    echo "❌ No suitable server found"
    exit 1
fi