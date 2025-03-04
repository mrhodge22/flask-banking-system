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

@app.before_first_request
def initialize():
    init_db()

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
    c.execute('SELECT balance FROM entries ORDER BY id DESC LIMIT 1')
    row = c.fetchone()
    previous_balance = row[0] if row else 0.0

    # Calculate the new balance
    if entry_type == 'Earnings':
        new_balance = previous_balance + amount
    elif entry_type == 'Expenses':
        new_balance = previous_balance - amount
    elif entry_type == 'Savings':
        new_balance = previous_balance + amount
    
    # Insert the new entry
    c.execute('INSERT INTO entries (date, description, amount, type, balance) VALUES (%s, %s, %s, %s, %s)',
              (date_time, description, amount, entry_type, new_balance))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'new_balance': new_balance})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
