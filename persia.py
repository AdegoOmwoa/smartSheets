import requests
from datetime import datetime
import webbrowser
import os
import http.server
import socketserver
from threading import Thread
from PIL import Image, ImageDraw
import json
import socket

class PWASetup:
    @staticmethod
    def create_pwa_files():
        """Generate all required PWA files in root directory"""
        # Create manifest.json
        manifest = {
            "name": "Transaction Records PWA",
            "short_name": "TxRecords",
            "start_url": "index.html",
            "display": "standalone",
            "background_color": "#2c3e50",
            "theme_color": "#3498db",
            "icons": [{
                "src": "icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            }]
        }
        with open("manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
        
        # Create service worker
        sw_content = """const CACHE_NAME = 'tx-records-v1';
const ASSETS = [
  '/pwa/index.html',
  '/pwa/icon-192.png',
  '/pwa/manifest.json',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
  'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request)
      .then(res => res || fetch(e.request))
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(clients.claim());
});"""
        with open("sw.js", "w") as f:
            f.write(sw_content)
        
        # Generate app icon
        img = Image.new('RGB', (192, 192), color='#3498db')
        draw = ImageDraw.Draw(img)
        draw.text((50, 80), "TRX", fill='white')
        img.save("icon-192.png", "PNG")

class TransactionApp:
    def __init__(self):
        self.data = None
    
    def fetch_google_sheet_data(self):
        """Fetch data from Google Sheets API"""
        spreadsheet_id = '1YdBlC_Yz3WDncGG1zhUFdKnItw01V3OVbOvkFrJvsLk'
        api_key = 'AIzaSyCg_XVzvEBJS9vZgSPLGABc5qdjQ-ijZ70'
        range_name = 'Sheet1!A1:E1000000'
        
        url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}?key={api_key}'
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            self.data = response.json().get('values', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            # Fallback data if API fails
            self.data = [
                ['Name', 'Amount', 'Items', 'Status'],
                ['John Doe', '150', 'Notebook x3', 'Paid'],
                ['Jane Smith', '230', 'Pens x10', 'Unpaid'],
                ['Mike Johnson', '75', 'Markers x5', 'Pending']
            ]
    
    def generate_html(self):
        """Generate complete HTML with all styles and functionality"""
        current_year = datetime.now().strftime('%Y')
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#3498db">
    <title>Transaction Records PWA</title>
    <link rel="manifest" href="manifest.json">
    <style>
        :root {{
            --primary: #2c3e50;
            --secondary: #34495e;
            --accent: #3498db;
            --light: #ecf0f1;
            --dark: #2c3e50;
            --success: #27ae60;
            --danger: #e74c3c;
            --warning: #f39c12;
            --font-main: 'Roboto', sans-serif;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            background-color: #f5f7fa;
            color: var(--dark);
            font-family: var(--font-main);
            line-height: 1.6;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            flex: 1;
        }}
        
        header {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 2rem 0;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        h1 {{
            font-size: 2.5rem;
            font-weight: 300;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
            font-weight: 300;
            opacity: 0.9;
        }}
        
        .search-container {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            margin: 2rem auto;
            max-width: 800px;
            text-align: center;
        }}
        
        .search-box {{
            display: flex;
            gap: 1rem;
            margin-top: 1.5rem;
        }}
        
        .search-input {{
            flex: 1;
            padding: 0.8rem 1.2rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }}
        
        .search-input:focus {{
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
        }}
        
        .search-btn {{
            background: var(--accent);
            color: white;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            min-width: 100px;
        }}
        
        .search-btn:hover {{
            background: #2980b9;
            transform: translateY(-2px);
        }}
        
        .results-container {{
            display: block;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            overflow: hidden;
            margin-top: 2rem;
            animation: fadeIn 0.5s ease;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
        }}
        
        th, td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        
        th {{
            background: var(--secondary);
            color: white;
            font-weight: 400;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.85rem;
        }}
        
        td {{
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .status {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        
        .status-paid {{
            background: var(--success);
            color: white;
        }}
        
        .status-unpaid {{
            background: var(--danger);
            color: white;
        }}
        
        .status-pending {{
            background: var(--warning);
            color: var(--dark);
        }}
        
        .no-results {{
            text-align: center;
            padding: 2rem;
            color: #7f8c8d;
            font-style: italic;
            display: none;
        }}
        
        footer {{
            text-align: center;
            padding: 1.5rem;
            color: #7f8c8d;
            font-size: 0.9rem;
            border-top: 1px solid #eee;
        }}
        
        #install-container {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 100;
        }}
        
        #install-btn {{
            background: var(--accent);
            color: white;
            border: none;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: none;
            justify-content: center;
            align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            cursor: pointer;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}
            
            .search-box {{
                flex-direction: column;
            }}
            
            .search-input, .search-btn {{
                width: 100%;
            }}
            
            th, td {{
                padding: 0.75rem;
                font-size: 0.9rem;
            }}
        }}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>Transaction Records</h1>
            <p class="subtitle">Search our database of transactions</p>
        </div>
    </header>
    
    <main class="container">
        <div class="search-container">
            <h2>Search Transactions</h2>
            <p>Enter a name to find specific records</p>
            
            <div class="search-box">
                <input type="text" class="search-input" id="search-input" placeholder="Enter name to search..." autocomplete="off">
                <button class="search-btn" id="search-btn">
                    <i class="fas fa-search"></i> Search
                </button>
            </div>
        </div>
        
        <div class="results-container" id="results-container">
            <div class="no-results" id="no-results">No matching records found</div>
            <table id="results-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Amount</th>
                        <th>Items</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="table-body">
                    <!-- Results will be inserted here by JavaScript -->
                </tbody>
            </table>
        </div>
    </main>
    
    <div id="install-container">
        <button id="install-btn" title="Install App">
            <i class="fas fa-download"></i>
        </button>
    </div>
    
    <footer>
        <p>© {current_year} Transaction Management System</p>
    </footer>

    <script>
        // Store all data
        const allData = {json.dumps(self.data)};
        
        // DOM elements
        const searchInput = document.getElementById('search-input');
        const searchBtn = document.getElementById('search-btn');
        const resultsContainer = document.getElementById('results-container');
        const tableBody = document.getElementById('table-body');
        const noResults = document.getElementById('no-results');
        const resultsTable = document.getElementById('results-table');
        const installBtn = document.getElementById('install-btn');
        
        // Display search results
        function displayResults(results) {{
            tableBody.innerHTML = '';
            
            if (results.length === 0) {{
                noResults.style.display = 'block';
                resultsTable.style.display = 'none';
            }} else {{
                noResults.style.display = 'none';
                resultsTable.style.display = 'table';
                
                results.forEach(row => {{
                    const status = row[3] || 'Unpaid';
                    const statusClass = `status-${{status.toLowerCase()}}`;
                    const statusDisplay = status.toLowerCase().includes('paid') ? 'Paid' : 'Unpaid';
                    
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${{row[0] || ''}}</td>
                        <td>${{row[1] || ''}}</td>
                        <td>${{row[2] || ''}}</td>
                        <td><span class="status ${{statusClass}}">${{statusDisplay}}</span></td>
                    `;
                    tableBody.appendChild(tr);
                }});
            }}
            
            resultsContainer.style.display = 'block';
        }}
        
        // Search functionality
        function performSearch() {{
            const searchTerm = searchInput.value.trim().toLowerCase();
            if (searchTerm) {{
                const filteredData = allData.filter((row, index) => {{
                    // Skip header row if present
                    if (index === 0 && row[0] === 'Name' && row[1] === 'Amount') return false;
                    return row[0]?.toLowerCase().includes(searchTerm);
                }});
                displayResults(filteredData.length > 0 ? filteredData : []);
            }} else {{
                // Show all data (except header) when search is empty
                displayResults(allData.slice(1));
            }}
        }}
        
        // Event listeners
        searchBtn.addEventListener('click', performSearch);
        searchInput.addEventListener('input', performSearch);
        searchInput.addEventListener('keypress', (e) => {{
            if (e.key === 'Enter') performSearch();
        }});
        
        // PWA Installation
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
            installBtn.style.display = 'flex';
            
            installBtn.addEventListener('click', () => {{
                installBtn.style.display = 'none';
                deferredPrompt.prompt();
                
                deferredPrompt.userChoice.then((choiceResult) => {{
                    if (choiceResult.outcome === 'accepted') {{
                        console.log('User accepted install');
                    }}
                    deferredPrompt = null;
                }});
            }});
        }});
        
        // Register Service Worker
        if ('serviceWorker' in navigator) {{
            window.addEventListener('load', () => {{
                navigator.serviceWorker.register('sw.js')
                    .then(registration => {{
                        console.log('SW registered:', registration.scope);
                    }})
                    .catch(err => {{
                        console.log('SW registration failed:', err);
                    }});
            }});
        }}
        
        // Initial display of all data (without header row)
        displayResults(allData.slice(1));
    </script>
</body>
</html>"""
        return html

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

class Server:
    def __init__(self, port=8000):
        self.port = port
    
    def start(self):
        """Start server with custom request handler"""
        with socketserver.TCPServer(("", self.port), RequestHandler) as httpd:
            print(f"\n🚀 PWA running at: http://localhost:{self.port}")
            print("📱 On mobile devices, connect to the same network and visit:")
            print(f"   http://{self.get_ip()}:{self.port}")
            print("📌 Look for 'Add to Home Screen' prompt in Chrome")
            print("\n🛑 Press Ctrl+C to stop the server")
            httpd.serve_forever()
    
    def get_ip(self):
        """Get local IP address for mobile testing"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = 'localhost'
        finally:
            s.close()
        return ip

def main():
    # 1. Set up PWA infrastructure
    print("🛠️  Setting up PWA files...")
    PWASetup.create_pwa_files()
    
    # 2. Initialize and fetch data
    print("📊 Fetching transaction data...")
    app = TransactionApp()
    app.fetch_google_sheet_data()
    
    # 3. Generate HTML with PWA features
    print("🖥️  Generating PWA interface...")
    html_content = app.generate_html()
    with open("pwa/index.html", "w") as f:
        f.write(html_content)
    
    # 4. Start server with redirection
    server = Server()
    server_thread = Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    
    # 5. Open browser directly to index.html
    webbrowser.open(f"http://localhost:{server.port}")
    
    # Keep running until interrupted
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == "__main__":
    main()