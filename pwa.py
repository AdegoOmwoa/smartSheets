import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread

class PWAGenerator:
    def __init__(self):
        self.pwa_files = {
            'manifest.json': """{
                "name": "AutoPWA",
                "short_name": "AutoPWA",
                "start_url": "/",
                "display": "standalone",
                "background_color": "#ffffff",
                "theme_color": "#4285f4",
                "icons": [
                    {
                        "src": "mobile_money.png",
                        "sizes": "192x192",
                        "type": "mobile_money/png"
                    }
                ]
            }""",
            
            'sw.js': """const CACHE_NAME = 'auto-pwa-v1';
            const ASSETS = ['/', '/index.html'];
            
            self.addEventListener('install', (e) => {
                e.waitUntil(
                    caches.open(CACHE_NAME)
                        .then(cache => cache.addAll(ASSETS))
                );
            });
            
            self.addEventListener('fetch', (e) => {
                e.respondWith(
                    caches.match(e.request)
                        .then(res => res || fetch(e.request))
                );
            });""",
            
            'index.html': """<!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta name="theme-color" content="#4285f4">
                <title>AutoPWA</title>
                <link rel="manifest" href="/manifest.json">
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    #status { margin-top: 20px; font-weight: bold; }
                </style>
            </head>
            <body>
                <h1>Auto-Enabled PWA</h1>
                <p>This PWA activates automatically on page load</p>
                <div id="status">Checking PWA capabilities...</div>
                
                <script>
                    // Auto-register service worker
                    if ('serviceWorker' in navigator) {
                        navigator.serviceWorker.register('/sw.js')
                            .then(reg => {
                                document.getElementById('status').textContent = 
                                    'PWA ready! Installable on supported browsers';
                                console.log('ServiceWorker registration successful');
                            })
                            .catch(err => {
                                document.getElementById('status').textContent = 
                                    'PWA support limited: ' + err;
                                console.log('ServiceWorker registration failed: ', err);
                            });
                    } else {
                        document.getElementById('status').textContent = 
                            'PWA not supported in this browser';
                    }
                    
                    // Auto-show install prompt when available
                    window.addEventListener('beforeinstallprompt', (e) => {
                        e.preventDefault();
                        setTimeout(() => e.prompt(), 1000);
                    });
                </script>
            </body>
            </html>"""
        }
    
    def generate_icon(self):
        # In a real app, replace this with actual PNG generation
        with open('icon.png', 'wb') as f:
            f.write(b'PNG placeholder')  # Should be real 192x192 PNG data

    def create_pwa_files(self):
        os.makedirs('pwa', exist_ok=True)
        for filename, content in self.pwa_files.items():
            with open(f'pwa/{filename}', 'w') as f:
                f.write(content)
        self.generate_icon()
        print("PWA files generated in /pwa directory")

class PWAServer:
    def __init__(self, port=8000):
        self.port = port
        self.server = HTTPServer(('', port), SimpleHTTPRequestHandler)
    
    def start(self):
        os.chdir('pwa')  # Serve from the PWA directory
        print(f"PWA serving at http://localhost:{self.port}")
        print("On Android Chrome, look for 'Add to Home Screen' prompt")
        self.server.serve_forever()

def main():
    # 1. Generate PWA files automatically
    pwa = PWAGenerator()
    pwa.create_pwa_files()
    
    # 2. Start server automatically
    server = PWAServer()
    Thread(target=server.start).start()
    
    # 3. (Optional) Auto-open browser
    import webbrowser
    webbrowser.open(f'http://localhost:{server.port}')

if __name__ == "__main__":
    main()