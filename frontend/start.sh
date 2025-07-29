#!/bin/bash

echo "🚀 Starting SBM AI CRM Frontend..."

# Try different ports in case of conflicts
for PORT in 3030 4040 5050 6060; do
    echo "Trying port $PORT..."
    
    # Check if port is free
    if ! lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
        echo "✅ Port $PORT is available"
        
        cd /Users/kurtis/SBM_AI_CRM_SYSTEM/frontend/dist
        
        cat > temp_server.py << EOF
import http.server
import socketserver
import os
from urllib.parse import urlparse

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if '.' in parsed_path.path or parsed_path.path == '/':
            return super().do_GET()
        self.path = '/index.html'
        return super().do_GET()

PORT = $PORT
with socketserver.TCPServer(("0.0.0.0", PORT), SPAHandler) as httpd:
    print(f"🎯 SBM AI CRM Frontend running on:")
    print(f"   http://localhost:{PORT}")
    print(f"   http://10.1.1.113:{PORT}")
    print(f"   http://127.0.0.1:{PORT}")
    print(f"🔑 Login: admin / admin123")
    httpd.serve_forever()
EOF
        
        python3 temp_server.py
        break
    else
        echo "❌ Port $PORT is busy"
    fi
done