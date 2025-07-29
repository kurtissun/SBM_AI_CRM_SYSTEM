#!/usr/bin/env python3
"""
VPN-compatible React development server
Bypasses VPN localhost blocking by binding to all available interfaces
"""
import http.server
import socketserver
import os
import sys
import socket
from urllib.parse import urlparse

class ReactSPAHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for React SPA with client-side routing"""
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Serve static assets normally
        if ('.' in parsed_path.path and 
            any(parsed_path.path.endswith(ext) for ext in ['.js', '.css', '.png', '.jpg', '.svg', '.ico'])):
            return super().do_GET()
        
        # For all routes, serve index.html (React Router)
        if parsed_path.path != '/':
            self.path = '/index.html'
        
        return super().do_GET()
    
    def end_headers(self):
        # Add CORS headers for VPN compatibility
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

def get_available_interfaces():
    """Get all available network interfaces"""
    interfaces = []
    
    # Standard localhost variants
    interfaces.extend(['127.0.0.1', 'localhost'])
    
    # Get actual network interfaces
    try:
        hostname = socket.gethostname()
        local_ips = socket.gethostbyname_ex(hostname)[2]
        interfaces.extend([ip for ip in local_ips if not ip.startswith("127.")])
    except:
        pass
    
    # Try common network ranges
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        if local_ip not in interfaces:
            interfaces.append(local_ip)
    except:
        pass
    
    return interfaces

def find_free_port(start_port=3000, max_attempts=100):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None

def start_server():
    """Start the React development server"""
    
    # Change to dist directory
    dist_dir = os.path.join(os.path.dirname(__file__), 'dist')
    if not os.path.exists(dist_dir):
        print("❌ No dist directory found. Please run 'npm run build' first.")
        sys.exit(1)
    
    os.chdir(dist_dir)
    
    # Find available port
    port = find_free_port(3000)
    if not port:
        print("❌ No available ports found")
        sys.exit(1)
    
    # Get available interfaces
    interfaces = get_available_interfaces()
    
    print("🚀 Starting SBM AI CRM React Frontend...")
    print(f"📁 Serving from: {dist_dir}")
    print(f"🌐 Port: {port}")
    print(f"🔧 VPN Bypass: Binding to 0.0.0.0")
    print()
    print("🎯 Access URLs:")
    
    for interface in interfaces:
        print(f"   • http://{interface}:{port}")
    
    print()
    print("🔑 Login: admin / admin123")
    print("📚 Features: 16 modules, 22 AI engines")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    try:
        # Start server on all interfaces
        with socketserver.TCPServer(("0.0.0.0", port), ReactSPAHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 SBM AI CRM Frontend stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()