import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import urllib.error
from urllib.parse import urlparse

# --- Configuration ---
BASE_TARGET_URL = "http://23.132.164.57" 
PORT = int(os.environ.get("PORT", 8080))

class ProxyHandler(BaseHTTPRequestHandler):
    def handle_all_requests(self):
        # Construct the full URL for the target server
        full_target_url = BASE_TARGET_URL + self.path

        # Read the body from the incoming request (from Cloudflare)
        content_length = int(self.headers.get('Content-Length', 0))
        request_body = self.rfile.read(content_length) if content_length > 0 else None
        
        # --- THE CRITICAL FIX IS HERE ---
        # We spoof the Referer and Host headers to make the request look legitimate.
        parsed_target = urlparse(full_target_url)
        headers_to_target = {
            'Host': parsed_target.netloc, # Tells the server we are accessing its IP directly
            'Referer': f"{parsed_target.scheme}://{parsed_target.netloc}/", # Pretend we came from the homepage
            'User-Agent': self.headers.get('User-Agent', 'Python-Proxy/2.0'),
            'Cookie': self.headers.get('Cookie', ''),
            'Content-Type': self.headers.get('Content-Type', '')
        }
        # Clean up any empty headers to avoid errors
        headers_to_target = {k: v for k, v in headers_to_target.items() if v}

        try:
            # Create and send the request to the real server
            req = urllib.request.Request(full_target_url, data=request_body, headers=headers_to_target, method=self.command)
            
            with urllib.request.urlopen(req) as response:
                # Forward the response back to Cloudflare
                self.send_response(response.status)
                for key, value in response.headers.items():
                    # Avoid forwarding headers that can cause issues
                    if key.lower() not in ['content-encoding', 'transfer-encoding', 'connection']:
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(502) # Bad Gateway
            self.end_headers()
            self.wfile.write(f"Proxy connection error: {e}".encode())

    # Use the same logic for all HTTP methods
    do_GET = handle_all_requests
    do_POST = handle_all_requests
    do_HEAD = handle_all_requests
    do_PUT = handle_all_requests
    do_DELETE = handle_all_requests

# --- Server Startup ---
print(f"[*] All-Rounder Proxy (v2) starting on port {PORT}")
server = HTTPServer(('0.0.0.0', PORT), ProxyHandler)
server.serve_forever()
