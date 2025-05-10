import os
import http.server
import socketserver
from threading import Thread
import webbrowser
from pathlib import Path

class PWACreator:
    def __init__(self):
        self.base_dir = Path("pwa")
        self.base_dir.mkdir(exist_ok=True)
        
        # Create a real 192x192 PNG icon (simple red square as example)
        self.create_placeholder_icon()
        
        # Generate all required PWA files
        self.create_manifest()
        self.create_service_worker()
        self.create_index_html()
        
    def create_placeholder_icon(self):
        """Create a minimal PNG icon programmatically"""
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (192, 192), color='red')
        draw = ImageDraw.Draw(img)
        draw.text((10, 80), "PWA", fill='white')
        img.save(self.base_dir / "icon-192.png", "PNG")
        
    def create_manifest(self):
        manifest = """{
            "name": "AutoPWA",
            "short_name": "AutoPWA",
            "start_url": ".",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#4285f4",
            "icons": [{
                "src": "icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            }]
        }"""
        (self.base_dir / "manifest.json").write_text(manifest)
        
    def create_service_worker(self):
        sw = """const CACHE_NAME = 'auto-pwa-v1';
const ASSETS = [
    '/',
    '/index.html',
    '/icon-192.png',
    '/manifest.json'
];

self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(ASSETS))
});

self.addEventListener('fetch', (e) => {
    e.respondWith(
        caches.match(e.request)
            .then(res => res || fetch(e.request))
});"""
        (self.base_dir / "sw.js").write_text(sw)
        
    def create_index_html(self):
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#4285f4">
    <title>AutoPWA</title>
    <link rel="manifest" href="manifest.json">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            padding: 20px;
            text-align: center;
        }
        #status {
            margin-top: 20px;
            padding: 10px;
            background: #f0f0f0;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <h1>Automatic PWA</h1>
    <p>This Progressive Web App activates automatically</p>
    
    <div id="status">Initializing PWA...</div>
    
    <script>
        // Auto-register service worker
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('sw.js')
                    .then(reg => {
                        document.getElementById('status').textContent = 
                            '✓ PWA Ready - Installable on supported browsers';
                        
                        // Auto-show install prompt
                        window.addEventListener('beforeinstallprompt', (e) => {
                            e.preventDefault();
                            setTimeout(() => {
                                e.prompt().then(choice => {
                                    if (choice.outcome === 'accepted') {
                                        document.getElementById('status').textContent = 
                                            '✓ PWA Installed!';
                                    }
                                });
                            }, 3000); // Show prompt after 3 seconds
                        });
                    })
                    .catch(err => {
                        document.getElementById('status').textContent = 
                            '✗ PWA Error: ' + err.message;
                    });
            });
        } else {
            document.getElementById('status').textContent = 
                '✗ PWA not supported in this browser';
        }
    </script>
</body>
</html>"""
        (self.base_dir / "index.html").write_text(html)

class PWAServer:
    def __init__(self, port=8000):
        self.port = port
        
    def start(self):
        os.chdir("pwa")
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", self.port), handler) as httpd:
            print(f"\nPWA serving at: http://localhost:{self.port}")
            print("On mobile Chrome, look for 'Add to Home Screen' prompt")
            print("Press Ctrl+C to stop\n")
            httpd.serve_forever()

def main():
    # 1. Generate all PWA files automatically
    print("Creating PWA files...")
    pwa = PWACreator()
    
    # 2. Start the server
    server = PWAServer()
    server_thread = Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    
    # 3. Open browser automatically
    webbrowser.open(f"http://localhost:{server.port}")
    
    # Keep the program running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nShutting down server...")

if __name__ == "__main__":
    main()