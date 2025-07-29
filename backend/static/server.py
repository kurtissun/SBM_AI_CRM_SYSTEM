#!/usr/bin/env python3
"""
Simple HTTP server for React SPA with client-side routing support
"""
import http.server
import socketserver
import os
from urllib.parse import urlparse

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL
        parsed_path = urlparse(self.path)
        
        # If it's a file request (has extension), serve it normally
        if '.' in parsed_path.path:
            return super().do_GET()
        
        # For routes without extensions, serve index.html (React Router)
        if parsed_path.path != '/':
            self.path = '/index.html'
        
        return super().do_GET()

if __name__ == "__main__":
    PORT = 8888
    
    # Change to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), SPAHandler) as httpd:
        print(f"🚀 SBM AI CRM Frontend serving at http://localhost:{PORT}")
        print(f"📱 React Router enabled for client-side navigation")
        print(f"🔑 Login: admin / admin123")
        httpd.serve_forever()