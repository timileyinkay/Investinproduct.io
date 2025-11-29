from flask import Flask, request, jsonify, session, render_template_string
import sqlite3
import time
import threading
from functools import wraps

app = Flask(__name__)
app.secret_key = 'insecure_secret_key'

# Simple in-memory "database" for demonstration
users = {
    'user1': {'password': 'pass1', 'balance': 1000},
    'user2': {'password': 'pass2', 'balance': 500}
}

# Rate limiting storage (vulnerable to race conditions)
rate_limit_attempts = {}
transfer_lock = threading.Lock()

# HTML templates for demonstration
LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Bank Login</title>
</head>
<body>
    <h2>Vulnerable Bank Login</h2>
    <form method="post">
        <input type="text" name="username" placeholder="Username" required><br>
        <input type="password" name="password" placeholder="Password" required><br>
        <button type="submit">Login</button>
    </form>
    <p>{{ message }}</p>
</body>
</html>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Bank Dashboard</title>
</head>
<body>
    <h2>Welcome, {{ username }}!</h2>
    <p>Balance: ${{ balance }}</p>
    
    <h3>Transfer Money</h3>
    <form action="/transfer" method="post">
        <input type="text" name="to_user" placeholder="Recipient" required><br>
        <input type="number" name="amount" placeholder="Amount" required><br>
        <button type="submit">Transfer</button>
    </form>
    <p>{{ message }}</p>
    
    <h3>Checkout Process</h3>
    <a href="/checkout">Start Checkout</a>
    
    <br><br>
    <a href="/logout">Logout</a>
</body>
</html>
'''

CHECKOUT_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Checkout</title>
</head>
<body>
    <h2>Checkout Process</h2>
    {% if step == 1 %}
    <form method="post">
        <input type="text" name="item" placeholder="Item" required><br>
        <input type="number" name="price" placeholder="Price" required><br>
        <button type="submit">Continue</button>
    </form>
    {% elif step == 2 %}
    <p>Item: {{ item }}, Price: ${{ price }}</p>
    <form method="post">
        <input type="text" name="shipping" placeholder="Shipping Address" required><br>
        <button type="submit">Confirm Purchase</button>
    </form>
    {% elif step == 3 %}
    <h3>Purchase Confirmed!</h3>
    <p>Item: {{ item }}</p>
    <p>Price: ${{ price }}</p>
    <p>Shipping: {{ shipping }}</p>
    {% endif %}
</body>
</html>
'''

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return 'Please login first', 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return f'''
            <script>
                window.location.href = '/dashboard';
            </script>
            '''
        else:
            return render_template_string(LOGIN_HTML, message='Invalid credentials')
    
    return render_template_string(LOGIN_HTML, message='')

@app.route('/dashboard')
@login_required
def dashboard():
    username = session['username']
    balance = users[username]['balance']
    return render_template_string(DASHBOARD_HTML, username=username, balance=balance, message='')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return '''
    <script>
        window.location.href = '/';
    </script>
    '''

# VULNERABLE: Race condition in transfer endpoint
@app.route('/transfer', methods=['POST'])
@login_required
def transfer_money():
    from_user = session['username']
    to_user = request.form.get('to_user')
    amount = float(request.form.get('amount'))
    
    # VULNERABILITY: No proper locking mechanism
    # This creates a race condition vulnerability
    if from_user in users and to_user in users:
        if users[from_user]['balance'] >= amount:
            # Simulate processing delay (makes race condition easier to exploit)
            time.sleep(0.1)
            
            users[from_user]['balance'] -= amount
            users[to_user]['balance'] += amount
            
            return f'''
            <script>
                alert('Transfer successful! Transferred ${amount} to {to_user}');
                window.location.href = '/dashboard';
            </script>
            '''
        else:
            return 'Insufficient funds', 400
    else:
        return 'User not found', 400

# VULNERABLE: Basic rate limiting that can be bypassed
@app.route('/api/data', methods=['GET'])
def api_data():
    client_ip = request.remote_addr
    
    # VULNERABILITY: Insecure rate limiting implementation
    current_time = time.time()
    window_start = current_time - 60  # 1 minute window
    
    # Clean old entries (inefficient but simple)
    global rate_limit_attempts
    rate_limit_attempts = {ip: ts for ip, ts in rate_limit_attempts.items() 
                          if ts > window_start}
    
    # Count requests in current window
    recent_requests = [ts for ts in rate_limit_attempts.values() 
                      if ts > window_start]
    
    if len(recent_requests) >= 10:  # 10 requests per minute
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    rate_limit_attempts[client_ip] = current_time
    
    # Return sensitive data (vulnerable to information disclosure)
    return jsonify({
        'users': list(users.keys()),
        'system_status': 'operational',
        'internal_data': 'sensitive_information_here'
    })

# VULNERABLE: Multi-step process with state management issues
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    step = int(request.args.get('step', 1))
    
    if request.method == 'POST':
        if step == 1:
            session['checkout_item'] = request.form.get('item')
            session['checkout_price'] = float(request.form.get('price'))
            step = 2
        elif step == 2:
            session['checkout_shipping'] = request.form.get('shipping')
            
            # VULNERABILITY: No validation of previous steps
            # User can skip directly to confirmation
            username = session['username']
            item = session.get('checkout_item', 'unknown')
            price = session.get('checkout_price', 0)
            
            # Process payment without proper validation
            if users[username]['balance'] >= price:
                users[username]['balance'] -= price
                step = 3
            else:
                return 'Insufficient funds', 400
    
    # VULNERABILITY: Direct step manipulation possible
    if step == 1:
        return render_template_string(CHECKOUT_HTML, step=1)
    elif step == 2:
        return render_template_string(CHECKOUT_HTML, step=2, 
                                    item=session.get('checkout_item'),
                                    price=session.get('checkout_price'))
    elif step == 3:
        return render_template_string(CHECKOUT_HTML, step=3,
                                    item=session.get('checkout_item'),
                                    price=session.get('checkout_price'),
                                    shipping=session.get('checkout_shipping'))

# Helper endpoint to view current balances (for testing)
@app.route('/debug/balances')
def debug_balances():
    return jsonify(users)

if __name__ == '__main__':
    print("Vulnerable Banking App Started!")
    print("Available users: user1/pass1, user2/pass2")
    print("Visit http://localhost:5000")
    app.run(debug=True, port=5000)