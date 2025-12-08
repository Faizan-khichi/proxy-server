import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import urllib.error

# --- CONFIGURATION ---
# Base URL of the origin server. We will add the path to this.
ORIGIN_BASE = "http://23.132.164.57/yaarsa/user" 
PORT = int(os.environ.get("PORT", 8080))

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request(method='GET')

    def do_POST(self):
        self.handle_request(method='POST')

    def handle_request(self, method):
        # 1. Read incoming data
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else None
        
        # --- THE CRITICAL FIX IS HERE ---
        # If the path is just "/", default to the main page. Otherwise, use the path from the request.
        request_path = self.path if self.path != "/" else "/create8619.php"
        target_full_url = f"{ORIGIN_BASE}{request_path}"
        
        print(f"[*] Forwarding {method} request to: {target_full_url}") # For debugging

        # 2. Prepare headers for the real server
        headers = { 'User-Agent': 'Mozilla/5.0' }
        if 'Cookie' in self.headers:
            headers['Cookie'] = self.headers['Cookie']
        if 'Content-Type' in self.headers:
            headers['Content-Type'] = self.headers['Content-Type']
        # Set Referer to the base, which is more generic and works for all requests
        headers['Referer'] = f"{ORIGIN_BASE}/create8619.php"

        try:
            # 3. Send Request to Real Server
            req = urllib.request.Request(target_full_url, data=post_data, headers=headers, method=method)
            with urllib.request.urlopen(req) as response:
                
                # 4. Send Response back to Cloudflare
                self.send_response(response.status)
                for key, value in response.headers.items():
                    # Pass through important headers
                    if key.lower() in ['set-cookie', 'content-type', 'location']:
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

print(f"[*] Smart Proxy starting on 0.0.0.0:{PORT}")
server = HTTPServer(('0.0.0.0', PORT), ProxyHandler)
server.serve_forever()
