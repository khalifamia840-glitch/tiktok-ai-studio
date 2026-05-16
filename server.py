import http.server
import socketserver

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()
    
    def log_message(self, format, *args):
        pass  # Silenciar logs

PORT = 5173
import os
os.chdir("www/tiktok-video-generator")
with socketserver.TCPServer(("", PORT), NoCacheHandler) as httpd:
    print(f"Servidor sin cache en http://localhost:{PORT}")
    httpd.serve_forever()