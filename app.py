from flask import Flask, request, jsonify, render_template_string
import os, requests, sqlite3, jwt, datetime, stripe
from functools import wraps

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'titanium_ultra_secret_2026')

# --- CONFIG ---
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "dev")
STRIPE_SECRET = os.getenv("STRIPE_SECRET")
DB_PATH = "titanium_v2.db"

# --- DB INIT ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS revenue (id INTEGER PRIMARY KEY, amount REAL, currency TEXT, date TEXT)")
    # Teszt adat, ha üres (opcionális)
    conn.commit()
    conn.close()

init_db()

# --- UI TEMPLATE (HTML + Tailwind + Chart.js) ---
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Titanium Admin Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-gray-900 text-white font-sans">
    <div class="min-h-screen flex flex-col">
        <nav class="bg-gray-800 p-4 border-b border-blue-500 shadow-lg">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-2xl font-bold text-blue-400">TITANIUM V2 <span class="text-xs text-gray-400">PRO</span></h1>
                <div id="status" class="text-green-500">● Rendszer Online</div>
            </div>
        </nav>

        <main class="container mx-auto p-6 flex-grow">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow-xl">
                    <h3 class="text-gray-400 text-sm uppercase">Összes Bevétel</h3>
                    <p id="total-revenue" class="text-3xl font-bold text-green-400">0.00 EUR</p>
                </div>
                <div class="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow-xl">
                    <h3 class="text-gray-400 text-sm uppercase">Tranzakciók</h3>
                    <p id="tx-count" class="text-3xl font-bold text-blue-400">0</p>
                </div>
                <div class="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow-xl">
                    <h3 class="text-gray-400 text-sm uppercase">AI Szerver Állapot</h3>
                    <p class="text-3xl font-bold text-purple-400 italic">Aktív</p>
                </div>
            </div>

            <div class="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow-xl">
                <h3 class="mb-4 text-xl font-semibold">Bevételi trendek</h3>
                <canvas id="revenueChart" class="w-full h-64"></canvas>
            </div>
        </main>
    </div>

    <script>
        async function loadStats() {
            // A kérésnél használd a saját ADMIN_TOKEN-edet a Bearer után!
            const res = await fetch('/api/admin/data', {
                headers: { 'Authorization': 'Bearer ' + 'dev' } 
            });
            const data = await res.json();
            
            document.getElementById('total-revenue').innerText = data.total_revenue + ' EUR';
            document.getElementById('tx-count').innerText = data.count;

            const ctx = document.getElementById('revenueChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.dates,
                    datasets: [{
                        label: 'Bevétel (EUR)',
                        data: data.values,
                        borderColor: '#60a5fa',
                        tension: 0.3,
                        fill: true,
                        backgroundColor: 'rgba(96, 165, 250, 0.1)'
                    }]
                },
                options: { responsive: true, scales: { y: { beginAtZero: true } } }
            });
        }
        loadStats();
    </script>
</body>
</html>
"""

# --- ROUTES ---
@app.route("/admin")
def dashboard():
    # Ezt csak te éred el a böngészőből
    return render_template_string(DASHBOARD_HTML)

@app.route("/api/admin/data")
def admin_data():
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {ADMIN_TOKEN}":
        return jsonify({"error": "unauthorized"}), 401

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT SUM(amount), COUNT(*) FROM revenue")
    row = c.fetchone()
    
    # Utolsó 7 nap adatai a grafikonhoz
    c.execute("SELECT date, amount FROM revenue ORDER BY date DESC LIMIT 7")
    rows = c.fetchall()
    conn.close()

    return jsonify({
        "total_revenue": round(row[0] or 0, 2),
        "count": row[1],
        "dates": [r[0][:10] for r in reversed(rows)],
        "values": [r[1] for r in reversed(rows)]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
