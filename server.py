import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import urllib.error

# --- CONFIGURATION ---
BASE_URL = "http://23.132.164.57/yaarsa" 
PORT = int(os.environ.get("PORT", 8080))

# --- BULLETPROOF REDIRECT HANDLER ---
# This class prevents the server from automatically following redirects (like the one from Render to Google).
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return fp  # Do not follow, just return the redirect response itself
    http_error_301 = http_error_303 = http_error_307 = http_error_302

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self): self.handle_request('GET')
    def do_POST(self): self.handle_request('POST')

    def handle_request(self, method):
        full_target_url = BASE_URL + self.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else None
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}
        if 'Cookie' in self.headers: headers['Cookie'] = self.headers['Cookie']
        if 'Content-Type' in self.headers: headers['Content-Type'] = self.headers['Content-Type']

        try:
            # Build an opener that uses our NoRedirect handler
            opener = urllib.request.build_opener(NoRedirect)
            req = urllib.request.Request(full_target_url, data=post_data, headers=headers, method=method)
            
            # Use the opener to make the request
            with opener.open(req) as response:
                raw_data = response.read()
                self.send_response(response.status)
                for key, value in response.headers.items():
                    if key.lower() in ['set-cookie', 'content-type', 'location']:
                        self.send_header(key, value)
                self.send_header('Content-Length', str(len(raw_data)))
                self.end_headers()
                self.wfile.write(raw_data)

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Python Proxy Error: {e}".encode())

print(f"[*] Intelligent Proxy (v2) starting on 0.0.0.0:{PORT}")
server = HTTPServer(('0.0.0.0', PORT), ProxyHandler)
server.serve_forever()
