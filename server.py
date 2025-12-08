import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
BASE_TARGET_URL = "https://proxy-server-63m7.onrender.com"
LOGO_URL = "https://n.f-a-k.workers.dev/screenshot20251207010923.png"
PORT = int(os.environ.get("PORT", 8080)) # Vital for cloud deployment

def modify_html(html_content):
    """Rebrands and re-styles the HTML content."""
    
    # Use BeautifulSoup to safely manipulate the HTML structure
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. Remove unwanted elements
    for element in soup.select('.header-msg, .watermark'):
        element.decompose()
        
    # 2. Inject the beautiful dark theme and logo as favicon
    if soup.head:
        css_tag = soup.new_tag('style')
        css_tag.string = get_theme_css()
        
        favicon_tag = soup.new_tag('link', rel='icon', type='image/png', href=LOGO_URL)
        meta_theme_tag = soup.new_tag('meta', attrs={'name': 'theme-color', 'content': '#111827'})
        
        soup.head.append(css_tag)
        soup.head.append(favicon_tag)
        soup.head.append(meta_theme_tag)

    # 3. Inject Logos
    login_form = soup.select_one('.login-form')
    if login_form:
        logo_img = soup.new_tag('img', src=LOGO_URL, alt='Logo', style="width:100px; height:100px; margin-bottom: 20px; filter: drop-shadow(0 0 10px rgba(59, 130, 246, 0.3));")
        login_form.insert(0, logo_img)
        
    navbar_brand = soup.select_one('.navbar-brand')
    if navbar_brand:
        logo_icon = soup.new_tag('img', src=LOGO_URL, alt='Icon', style="width:32px; height:32px;")
        navbar_brand.insert(0, logo_icon)

    # Convert back to string for text replacement
    modified_html = str(soup)

    # 4. Perform reliable text and link replacements
    modified_html = modified_html.replace('https://t.me/BTMOB1', 'https://t.me/ZeroDefenceTeam')
    modified_html = modified_html.replace('@BTMOB1', '@ZeroDefenceTeam')
    modified_html = modified_html.replace('Admin Panel', 'ZΞЯO ᗪᗴᖴᗴᑎᑕᗴ')
    modified_html = modified_html.replace('User Management', 'Client List')
    modified_html = modified_html.replace('Admin Key', 'License Key')
    modified_html = modified_html.replace('Key Enter', 'License Key')
    modified_html = modified_html.replace('>Enter<', '>Authenticate<')
    modified_html = modified_html.replace('>Add User<', '>Create Client<')

    return modified_html

def get_theme_css():
    """Returns the full CSS string for the beautiful dark theme."""
    return """
      :root {
        --bg-dark: #111827; --card-dark: #1F2937; --text-light: #E5E7EB;
        --text-secondary: #9CA3AF; --accent-color: #3B82F6; --border-color: #374151;
        color-scheme: dark;
      }
      @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
      @keyframes moveGradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
      body { background-color: var(--bg-dark) !important; color: var(--text-light) !important; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important; overflow-y: auto !important; }
      body::before { content: '' !important; display: block !important; position: fixed !important; top: 0; left: 0; width: 100%; height: 100vh; z-index: -1; background: radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.15), transparent 40%), radial-gradient(circle at 80% 70%, rgba(59, 130, 246, 0.15), transparent 40%); background-size: 200% 200%; animation: moveGradient 20s ease infinite; }
      .navbar { background-color: rgba(31, 41, 55, 0.8) !important; backdrop-filter: blur(10px); border-bottom: 1px solid var(--border-color) !important; padding: 10px 20px !important; animation: fadeIn 0.5s ease-out; }
      .navbar-brand { gap: 12px; } .navbar-brand, .navbar-brand a { display:flex; align-items:center; color: var(--text-light) !important; font-weight: 700; text-decoration:none; }
      .card, .modal-content { background-color: var(--card-dark) !important; border: 1px solid var(--border-color) !important; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); animation: fadeIn 0.6s ease-out; }
      .table-responsive { background-color: var(--card-dark) !important; border-radius: 12px; padding:15px; border: 1px solid var(--border-color); }
      .table { border-collapse: separate; border-spacing: 0; }
      .table td, .table th { color: var(--text-light) !important; background-color: transparent !important; border-bottom: 1px solid var(--border-color) !important; }
      .table thead th { font-weight: 600; color: var(--text-secondary) !important; } .table tbody tr { transition: background-color 0.2s ease; } .table tbody tr:hover { background-color: rgba(255,255,255,0.05) !important; }
      .table a { color: var(--accent-color) !important; font-weight: 600 !important; } .table svg { fill: var(--text-light) !important; }
      .form-control, .form-select { background-color: var(--bg-dark) !important; color: var(--text-light) !important; border: 1px solid var(--border-color) !important; border-radius: 8px; transition: all 0.2s ease; }
      .form-control:focus, .form-select:focus { border-color: var(--accent-color) !important; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3) !important; }
      .btn-primary { background-color: var(--accent-color) !important; border: none; font-weight:600; transition: all 0.2s ease; }
      .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3); }
      .btn-danger, .btn-info { background: transparent !important; border: 1px solid var(--border-color) !important; transition: all 0.2s ease; }
      .btn-danger:hover { background: #dc3545 !important; border-color: #dc3545 !important; } .btn-info:hover { background: #0dcaf0 !important; border-color: #0dcaf0 !important; }
      .login-form input[type="password"] { background-color: var(--bg-dark) !important; }
    """

class ProxyHandler(BaseHTTPRequestHandler):
    def handle_request(self):
        # Construct the full target URL, preserving the path
        target_url = BASE_TARGET_URL + self.path

        # Read the body if it's a POST request
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else None

        # Forward headers, especially cookies
        forward_headers = {key: value for key, value in self.headers.items()}
        
        try:
            # Make the request to the target server
            resp = requests.request(
                method=self.command,
                url=target_url,
                headers=forward_headers,
                data=post_data,
                allow_redirects=False # Let the client handle redirects
            )
            
            # --- INTELLIGENT CONTENT HANDLING ---
            self.send_response(resp.status_code)
            
            content_type = resp.headers.get('Content-Type', '')
            
            # Forward most headers back to the client
            for key, value in resp.headers.items():
                if key.lower() not in ['content-encoding', 'content-length', 'transfer-encoding']:
                    self.send_header(key, value)
            
            # If it's HTML, modify it
            if 'text/html' in content_type:
                if resp.status_code == 404:
                    body = get_logout_page_html(LOGO_URL).encode('utf-8')
                    self.send_response(200) # Override status to 200 OK
                else:
                    body = modify_html(resp.text).encode('utf-8')
            else:
                # For JSON, JS, images, etc., pass them through untouched
                body = resp.content
            
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        except requests.exceptions.RequestException as e:
            self.send_error(502, f"Proxy Error: {e}")

    def do_GET(self):
        self.handle_request()
    def do_POST(self):
        self.handle_request()
    # Add other methods if needed
    def do_HEAD(self): self.handle_request()
    def do_OPTIONS(self): self.handle_request()


def get_logout_page_html(logo_url):
  return f'<!DOCTYPE html><html><head><title>Logged Out</title><meta name="viewport" content="width=device-width, initial-scale=1"><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"><link rel="icon" type="image/png" href="{logo_url}"></head><body style="background-color:#111827;"><div class="container" style="margin-top:100px; text-align:center;"><div class="card p-5" style="background-color:#1F2937; border:1px solid #374151; color:#E5E7EB;"><img src="{logo_url}" alt="Logo" style="width:80px; height:80px; margin: 0 auto 20px auto;"><h2 style="color:#fff;">Session Ended</h2><p style="color:#9CA3AF;">You have been logged out successfully.</p><br><a href="/" class="btn btn-primary">Log In Again</a></div></div></body></html>'

if __name__ == "__main__":
    server_address = ('0.0.0.0', PORT)
    httpd = HTTPServer(server_address, ProxyHandler)
    print(f"[*] Starting ZΞЯO ᗪᗴᖴᗴᑎᑕᗴ proxy on port {PORT}...")
    httpd.serve_forever()
