import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import urllib.error

# --- UPGRADED CONFIGURATION ---
# We now define the base path and use the incoming request path
BASE_URL = "http://23.132.164.57/yaarsa" 
PORT = int(os.environ.get("PORT", 8080))

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')

    def handle_request(self, method):
        # Construct the full URL by combining the base and the path from the client's request
        full_target_url = BASE_URL + self.path
        
        # Read incoming data from the browser
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else None
        
        # Prepare headers for the target server, spoofing Chrome
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': full_target_url # Make the referer dynamic and correct
        }
        # Forward essential headers like Cookies
        if 'Cookie' in self.headers:
            headers['Cookie'] = self.headers['Cookie']
        if 'Content-Type' in self.headers:
            headers['Content-Type'] = self.headers['Content-Type']

        try:
            # Send the request to the dynamically constructed URL
            req = urllib.request.Request(full_target_url, data=post_data, headers=headers, method=method)
            with urllib.request.urlopen(req) as response:
                
                # Read the raw data
                raw_data = response.read()
                
                # Send the response back to the Cloudflare Worker
                self.send_response(response.status)
                for key, value in response.headers.items():
                    # Pass back important headers like Set-Cookie
                    if key.lower() in ['set-cookie', 'content-type', 'location']:
                        self.send_header(key, value)
                self.send_header('Content-Length', str(len(raw_data)))
                self.end_headers()
                
                self.wfile.write(raw_data)

        except urllib.error.HTTPError as e:
            # Handle errors gracefully
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Python Proxy Error: {e}".encode())

# --- SERVER STARTUP ---
print(f"[*] Intelligent Proxy starting on 0.0.0.0:{PORT}")
print(f"[*] Forwarding all paths to base: {BASE_URL}")
server = HTTPServer(('0.0.0.0', PORT), ProxyHandler)
server.serve_forever()
