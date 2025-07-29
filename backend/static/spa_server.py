#!/usr/bin/env python3
import http.server
import socketserver
import os
from urllib.parse import urlparse

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Serve static files normally
        if '.' in parsed_path.path or parsed_path.path == '/':
            return super().do_GET()
        
        # For all other routes, serve index.html (React Router)
        self.path = '/index.html'
        return super().do_GET()

if __name__ == "__main__":
    PORT = 3030
    HOST = "0.0.0.0"  # Listen on all interfaces
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer((HOST, PORT), SPAHandler) as httpd:
        print(f"🚀 SBM AI CRM Frontend serving on:")
        print(f"   http://localhost:{PORT}")
        print(f"   http://10.1.1.113:{PORT}")
        print(f"   http://127.0.0.1:{PORT}")
        print(f"🔑 Login: admin / admin123")
        httpd.serve_forever()