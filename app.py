from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

DATABASE = 'users.db'

# Function to create the users table if not exists
def create_table():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    balance INTEGER NOT NULL DEFAULT 1000
                )''')
    conn.commit()
    conn.close()

# Function to register a new user
def register_user(username, password):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

# Function to get user data by username
def get_user(username):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user

# Function to update user balance
def update_balance(username, new_balance):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("UPDATE users SET balance=? WHERE username=?", (new_balance, username))
    conn.commit()
    conn.close()

# Define route for the homepage
@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', balance=session['balance'])
    else:
        return redirect(url_for('login'))

# Define route for the betting page
@app.route('/bet', methods=['GET', 'POST'])
def bet():
    if 'username' not in session:
        return redirect(url_for('login'))

    bet_amount = request.form.get('bet_amount', type=int)
    color = request.form.get('color')
    number = request.form.get('number')
    big_small = request.form.get('big_small')

    if request.method == 'POST' and bet_amount is not None:
        if bet_amount <= 0 or bet_amount > session['balance']:
            return jsonify({"success": False, "message": "Invalid bet amount."})

        if not color and not number and not big_small:
            return jsonify({"success": False, "message": "Select at least one option to bet."})

        num_options = sum([1 for option in [color, number, big_small] if option])
        individual_bet_amount = bet_amount // num_options

        winning_amount = 0

        colors = ['red', 'green', 'violet']
        numbers = list(range(10))

        winning_color = random.choice(colors)
        winning_number = random.choice(numbers)
        winning_big_small = 'big' if winning_number >= 5 else 'small'

        if color and color == winning_color:
            winning_amount += individual_bet_amount
        if number and int(number) == winning_number:
            winning_amount += individual_bet_amount
        if big_small and big_small == winning_big_small:
            winning_amount += individual_bet_amount

        new_balance = session['balance'] - bet_amount + winning_amount * 2
        update_balance(session['username'], new_balance)
        session['balance'] = new_balance

        return redirect(url_for('result'))

    return render_template('bet.html', balance=session['balance'])

# Define route for the result page
@app.route('/result')
def result():
    return render_template('result.html', balance=session['balance'])

# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        register_user(username, password)
        return redirect(url_for('login'))
    return render_template('register.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user and user[2] == password:
            session['username'] = username
            session['balance'] = user[3]
            return redirect(url_for('index'))
        else:
            return "Invalid username or password"
    return render_template('login.html')

# Route for the logout functionality
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('balance', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    create_table()
    app.run(host='0.0.0.p', port=8080, debug=True)
