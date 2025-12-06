import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request
import urllib.error
import sys

# --- CONFIGURATION ---
TARGET_URL = "http://23.132.164.57/yaarsa/user/create8619.php"

# CRITICAL FOR CLOUD: Get the port from the environment, default to 8080 if testing locally
PORT = int(os.environ.get("PORT", 8080))

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request(method='GET')

    def do_POST(self):
        self.handle_request(method='POST')

    def handle_request(self, method):
        # 1. Read incoming headers/body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else None
        
        # 2. Prepare headers (Spoofing Chrome)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': TARGET_URL
        }
        # Pass Cookies and Content-Type to keep login working
        if 'Cookie' in self.headers:
            headers['Cookie'] = self.headers['Cookie']
        if 'Content-Type' in self.headers:
            headers['Content-Type'] = self.headers['Content-Type']

        try:
            # 3. Request to Real Server
            req = urllib.request.Request(TARGET_URL, data=post_data, headers=headers, method=method)
            with urllib.request.urlopen(req) as response:
                
                # 4. Read and Modify Data
                raw_data = response.read()

                try:
                    # Decode to text
                    html_content = raw_data.decode('utf-8')
                    
                    # --- YOUR MODIFICATIONS ---
                    html_content = html_content.replace('Admin Key', 'Key Enter')
                    html_content = html_content.replace('>Enter<', '>Submit Key<')
                    # --------------------------
                    
                    final_data = html_content.encode('utf-8')
                except:
                    # If image/binary, leave it alone
                    final_data = raw_data

                # 5. Send Response
                self.send_response(response.status)
                
                # Forward headers (except length)
                for key, value in response.headers.items():
                    if key.lower() == 'content-length': continue
                    if key.lower() in ['set-cookie', 'content-type', 'location']:
                        self.send_header(key, value)
                
                self.send_header('Content-Length', str(len(final_data)))
                self.end_headers()
                
                self.wfile.write(final_data)

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

# 0.0.0.0 is required for Cloud Servers to expose the app
print(f"[*] Proxy starting on 0.0.0.0:{PORT}")
server = HTTPServer(('0.0.0.0', PORT), ProxyHandler)
server.serve_forever()