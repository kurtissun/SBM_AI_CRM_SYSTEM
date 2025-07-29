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

PORT = 3030
with socketserver.TCPServer(("0.0.0.0", PORT), SPAHandler) as httpd:
    print(f"🎯 SBM AI CRM Frontend running on:")
    print(f"   http://localhost:{PORT}")
    print(f"   http://10.1.1.113:{PORT}")
    print(f"   http://127.0.0.1:{PORT}")
    print(f"🔑 Login: admin / admin123")
    httpd.serve_forever()
