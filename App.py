from flask import Flask, request, jsonify, render_template
from datetime import datetime
import os
import psycopg2

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    return conn

# Initialize the database
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS entries
                 (id SERIAL PRIMARY KEY, date TEXT, description TEXT, amount REAL, type TEXT, balance REAL)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT date, description, amount, type, balance FROM entries')
    entries = c.fetchall()
    conn.close()
    return render_template('index.html', entries=entries)

@app.route('/add_entry', methods=['POST'])
def add_entry():
    data = request.get_json()
    date = data['date']
    amount = data['amount']
    description = data['description']
    entry_type = data['type']
    date_time = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    c = conn.cursor()
    
    # Get the previous balance
    c.execute('SELECT balance FROM entries ORDER BY id DESC LIMIT 
