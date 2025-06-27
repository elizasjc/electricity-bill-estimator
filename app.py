from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend to prevent tkinter errors
import matplotlib.pyplot as plt
import io
import base64
from flask import redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
import pickle
import numpy as np

# Load the trained model
model = pickle.load(open("model.pkl", "rb"))


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


APPLIANCES = {
    "Fan": 75,
    "Light": 60,
    "AC": 1500,
    "Refrigerator": 200,
    "TV": 100,
    "Computer": 200
}

RATE_PER_KWH = 5.5
USERS = {}  # format: {'username': {'password': hashed_password}}


def create_chart(breakdown, chart_type):
    labels = list(breakdown.keys())
    values = list(breakdown.values())

    plt.figure(figsize=(8, 5))

    if chart_type == "bar":
        plt.bar(labels, values, color='skyblue')
        plt.ylabel('Energy Used (kWh)')
        plt.title('Energy Consumption by Appliance')
    elif chart_type == "pie":
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title('Energy Consumption by Appliance')
    elif chart_type == "bubble":
        sizes = [v * 1000 for v in values]
        plt.scatter(labels, values, s=sizes, alpha=0.5, color='coral')
        plt.ylabel('Energy Used (kWh)')
        plt.title('Energy Consumption by Appliance (Bubble Chart)')

    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode('utf8')
    return img_b64

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template('index.html', appliances=APPLIANCES)

def save_usage_history(username, days, breakdown, total_energy, estimated_bill):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO usage_history (username, timestamp, appliance_data, total_energy, estimated_bill)
        VALUES (?, datetime('now'), ?, ?, ?)
    ''', (username, json.dumps(breakdown), total_energy, estimated_bill))
    conn.commit()
    conn.close()



@app.route('/result', methods=['POST'])
def result():
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        days = int(request.form.get('days', 30))
        chart_type = request.form.get('chart_type', 'bar')

        total_energy = 0
        breakdown = {}
        breakdown_rupees = {}

        for appliance in APPLIANCES:
            qty = int(request.form.get(f'{appliance}_qty', 0))
            hours = float(request.form.get(f'{appliance}_hours', 0))
            energy = (APPLIANCES[appliance] * qty * hours * days) / 1000
            cost = energy * RATE_PER_KWH

            if energy > 0:
                breakdown[appliance] = round(energy, 2)
                breakdown_rupees[appliance] = round(cost, 2)

            total_energy += energy

        total_energy = round(total_energy, 2)
        estimated_bill = round(total_energy * RATE_PER_KWH, 2)

        # Save current usage to database
        save_usage_history(session['user'], days, breakdown, total_energy, estimated_bill)

        # Get previous usage for comparison (offset 1 means second latest)
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
            SELECT total_energy, estimated_bill 
            FROM usage_history 
            WHERE username = ? 
            ORDER BY id DESC 
            LIMIT 1 OFFSET 1
        ''', (session['user'],))
        previous = c.fetchone()
        conn.close()
                # Fetch full history for trend chart
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
            SELECT timestamp, total_energy FROM usage_history 
            WHERE username = ? ORDER BY timestamp
        ''', (session['user'],))
        history_data = c.fetchall()
        conn.close()

        # Prepare lists for plotting
        dates = [row[0][:10] for row in history_data]  # first 10 chars for YYYY-MM-DD
        energies = [row[1] for row in history_data]

        # Plot usage trend
        plt.figure(figsize=(8, 4))
        plt.plot(dates, energies, marker='o', color='green')
        plt.title('Your Energy Usage Trend')
        plt.xlabel('Date')
        plt.ylabel('Total Energy (kWh)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        trend_img = io.BytesIO()
        plt.savefig(trend_img, format='png')
        plt.close()
        trend_img.seek(0)
        trend_img_b64 = base64.b64encode(trend_img.getvalue()).decode('utf8')


        # Calculate difference from previous usage
        usage_diff = round(total_energy - previous[0], 2) if previous else 0
        bill_diff = round(estimated_bill - previous[1], 2) if previous else 0

        # Create chart
        chart_img = create_chart(breakdown, chart_type)

        # Top appliance analysis
        if breakdown:
            top_appliance = max(breakdown.items(), key=lambda x: x[1])
            top_name = top_appliance[0]
            top_percent = round((top_appliance[1] / total_energy) * 100, 1) if total_energy else 0
        else:
            top_name = None
            top_percent = 0

        return render_template('result.html',
                               units=total_energy,
                               bill=estimated_bill,
                               breakdown=breakdown,
                               breakdown_rupees=breakdown_rupees,
                               chart_img=chart_img,
                               selected_chart=chart_type,
                               top_appliance_name=top_name,
                               top_appliance_percent=top_percent,
                               usage_diff=usage_diff,
                               bill_diff=bill_diff,
                               trend_chart=trend_img_b64)
    except Exception as e:
        return f"Error: {e}"



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        if c.fetchone():
            conn.close()
            return render_template('register.html', error="Username already exists")
        
        hashed_password = generate_password_hash(password)
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Create users table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create usage_history table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS usage_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date TEXT NOT NULL,
            appliance_data TEXT NOT NULL,
            total_energy REAL NOT NULL,
            estimated_bill REAL NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login'))

    username = session['user']
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Use correct column: timestamp
    c.execute("SELECT timestamp, total_energy, estimated_bill, appliance_data FROM usage_history WHERE username=? ORDER BY timestamp DESC", (username,))
    rows = c.fetchall()
    conn.close()

    history = []
    for row in rows:
        breakdown = json.loads(row[3])
        history.append({
            'timestamp': row[0],
            'total_energy': row[1],
            'estimated_bill': row[2],
            'breakdown': breakdown
        })

    return render_template('history.html', history=history)


    





if __name__ == '__main__':
    init_db()  # Initializes the DB and creates 'users' table
    app.run(debug=True)


