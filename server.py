import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import urllib.error

# --- Configuration ---
# The base URL of the REAL target server. The path will be added automatically.
BASE_TARGET_URL = "http://23.132.164.57" 

# This port is set by the Render.com environment automatically.
PORT = int(os.environ.get("PORT", 8080))

class ProxyHandler(BaseHTTPRequestHandler):
    def handle_all_requests(self):
        # Construct the full target URL by combining the base URL and the requested path
        # Example: if request is for "/private/createacc.php", this becomes "http://23.132.164.57/private/createacc.php"
        full_target_url = BASE_TARGET_URL + self.path

        # Read the body from the incoming request (from Cloudflare)
        content_length = int(self.headers.get('Content-Length', 0))
        request_body = self.rfile.read(content_length) if content_length > 0 else None
        
        # Prepare headers to be sent to the REAL target server
        headers_to_target = {
            'User-Agent': self.headers.get('User-Agent', 'Python-Proxy'),
            'Cookie': self.headers.get('Cookie', ''),
            'Content-Type': self.headers.get('Content-Type', '')
        }
        # Clean up empty headers
        headers_to_target = {k: v for k, v in headers_to_target.items() if v}

        try:
            # Create and send the request to the real server
            req = urllib.request.Request(full_target_url, data=request_body, headers=headers_to_target, method=self.command)
            
            with urllib.request.urlopen(req) as response:
                # --- Send Response Back to Cloudflare ---
                self.send_response(response.status)
                
                # Forward all headers from the real server back to Cloudflare
                for key, value in response.headers.items():
                    self.send_header(key, value)
                self.end_headers()
                
                # Send the page content (HTML, JSON, etc.) back
                self.wfile.write(response.read())

        except urllib.error.HTTPError as e:
            # If the real server has an error, forward that error
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            # Handle any other connection errors
            self.send_response(502) # Bad Gateway
            self.end_headers()
            self.wfile.write(f"Proxy connection error: {e}".encode())

    # Handle GET, POST, and any other methods with the same logic
    def do_GET(self):
        self.handle_all_requests()

    def do_POST(self):
        self.handle_all_requests()

    def do_HEAD(self):
        self.handle_all_requests()

# --- Server Startup ---
print(f"[*] Simple All-Rounder Proxy starting on port {PORT}")
server = HTTPServer(('0.0.0.0', PORT), ProxyHandler)
server.serve_forever()
