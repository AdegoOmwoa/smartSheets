import requests
from datetime import datetime
import webbrowser
from pathlib import Path

def fetch_google_sheet_data():
    spreadsheet_id = '1YdBlC_Yz3WDncGG1zhUFdKnItw01V3OVbOvkFrJvsLk'
    api_key = 'AIzaSyCg_XVzvEBJS9vZgSPLGABc5qdjQ-ijZ70'
    range_name = 'Sheet1!A1:E1000000'
    
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}?key={api_key}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('values', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def generate_html(data=None):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transaction Records</title>
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
        }}

        @font-face {{
            font-family: 'Chap';
            src: url('Chap-Regular.ttf') format('truetype');
            font-display: swap;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            background-color: #f5f7fa;
            color: var(--dark);
            font-family: 'Chap', 'Helvetica Neue', Arial, sans-serif;
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
            padding: 0 2rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

         .search-btn {{
            background: var(--accent);
            color: white;
            border: none;
            padding: 0.8rem 1.5rem;  /* Increased padding for better touch targets */
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center; /* Center content better */
            gap: 0.5rem;
            min-width: 100px; /* Ensure minimum width */
        }}
        
        /* Mobile-specific styles */
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}
            
            .search-box {{
                flex-direction: column;
                gap: 0.8rem; /* Reduced gap for mobile */
            }}
            
            .search-input {{
                padding: 0.9rem 1.2rem; /* Slightly larger for mobile */
                width: 100%;
            }}
            
            .search-btn {{
                padding: 1rem 1.5rem; /* Larger padding for mobile */
                width: 100%; /* Full width on mobile */
                font-size: 1.1rem; /* Slightly larger text */
            }}
            
            th, td {{
                padding: 0.75rem;
            }}
        }}
        
        /* Extra small devices */
        @media (max-width: 480px) {{
            .search-btn {{
                padding: 1.1rem 1.5rem; /* Even larger for very small screens */
            }}
        }}
        
        .search-btn:hover {{
            background: #2980b9;
            transform: translateY(-2px);
        }}
        
        .results-container {{
            display: none;
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
        
        .no-results {{
            text-align: center;
            padding: 2rem;
            color: #7f8c8d;
            font-style: italic;
            display: none;
        }}
        
        .result-card {{
            display: none;
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        footer {{
            text-align: center;
            padding: 1.5rem;
            color: #7f8c8d;
            font-size: 0.9rem;
            border-top: 1px solid #eee;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}
            
            .search-box {{
                flex-direction: column;
            }}
            
            th, td {{
                padding: 0.75rem;
            }}
        }}
    </style>
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
                <input type="text" class="search-input" id="search-input" placeholder="Enter name to search...">
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
    
    <footer>
        <p>© {datetime.now().year} Transaction Management System</p>
    </footer>

    <script>
        // Store all data in JavaScript variable
        const allData = {data if data else []};
        
        function displayResults(results) {{
            const tableBody = document.getElementById('table-body');
            const resultsContainer = document.getElementById('results-container');
            const noResults = document.getElementById('no-results');
            
            // Clear previous results
            tableBody.innerHTML = '';
            
            if (results.length === 0) {{
                noResults.style.display = 'block';
                document.getElementById('results-table').style.display = 'none';
            }} else {{
                noResults.style.display = 'none';
                document.getElementById('results-table').style.display = 'table';
                
                results.forEach(row => {{
                    const status = row[4] || 'Unpaid';
                    const statusClass = `status-${{status.toLowerCase()}}`;
                    const statusDisplay = status.charAt(0).toUpperCase() + status.slice(1).toLowerCase();
                    
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
        
        document.getElementById('search-btn').addEventListener('click', function() {{
            const searchTerm = document.getElementById('search-input').value.trim().toLowerCase();
            if (searchTerm) {{
                const filteredData = allData.filter(row => {{
                    // Skip header row if present
                    if (row[0] === 'Name' && row[1] === 'Amount') return false;
                    return row[0]?.toLowerCase().includes(searchTerm);
                }});
                displayResults(filteredData);
            }}
        }});
        
        document.getElementById('search-input').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                document.getElementById('search-btn').click();
            }}
        }});
    </script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
</body>
</html>
    """
    return html_content

def save_and_open_html(content):
    # Save the HTML content to a file
    html_file = Path('transactions.html')
    html_file.write_text(content)

    # Open the file in a web browser
    webbrowser.open(f'file://{html_file.resolve()}')

if __name__ == "__main__":
    data = fetch_google_sheet_data()
    html_content = generate_html(data)
    save_and_open_html(html_content)