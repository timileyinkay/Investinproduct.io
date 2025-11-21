from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
import re
import secrets
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gold-investment-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gold_investment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    balance = db.Column(db.Float, default=0.0)
    gold_balance = db.Column(db.Float, default=0.0)
    phone_number = db.Column(db.String(20))
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    payments = db.relationship('PaymentReceipt', backref='user', lazy=True)

class PaymentReceipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    sender_name = db.Column(db.String(100), nullable=False)
    recipient_name = db.Column(db.String(100), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True)
    session_id = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, nullable=False)
    reference_text = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # pending, verified, rejected
    verified_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # deposit, gold_purchase, gold_sale
    amount = db.Column(db.Float, nullable=False)
    gold_amount = db.Column(db.Float)
    gold_price = db.Column(db.Float)
    status = db.Column(db.String(20), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GoldPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Configuration
REFERENCE_PATTERNS = [
    r'invest\d+',
    r'gold\d+',
    r'xau\d+',
    r'tmzbrand\d+',
    r'investment\d+'
]

RECIPIENT_NAMES = [
    "OLUWATOBILOBA SHERIFDEEN KEHINDE",
    "GOLD INVESTMENT",
    "XAU TRADING",
    "GOLD XAU"
]

# Gold API Service
class GoldAPIService:
    @staticmethod
    def get_gold_price():
        """Get current gold price from API"""
        try:
            # Using a free gold API (example)
            response = requests.get('https://api.metalpriceapi.com/v1/latest?api_key=DEMO&base=XAU&currencies=USD', timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('rates', {}).get('USD', 1950.0)
        except:
            pass
        
        # Fallback price
        return 1950.0

# HTML Templates
HTML_TEMPLATES = {
    'base': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}GoldXAU Investment{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gold-gradient { background: linear-gradient(135deg, #FFD700, #D4AF37); }
        .loading { display: none; }
        .receipt-box { 
            border: 2px dashed #e5e7eb;
            background: #f8fafc;
            transition: all 0.3s ease;
        }
        .receipt-box.dragover {
            border-color: #3b82f6;
            background: #dbeafe;
        }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="gold-gradient shadow-lg">
        <div class="container mx-auto px-4">
            <div class="flex justify-between items-center py-4">
                <div class="flex items-center space-x-3">
                    <i class="fas fa-coins text-2xl text-white"></i>
                    <span class="text-xl font-bold text-white">GoldXAU Investment</span>
                </div>
                <div class="flex space-x-6 text-white">
                    {% if session.user_id %}
                        <a href="{{ url_for('dashboard') }}" class="hover:text-yellow-200 transition">Dashboard</a>
                        <a href="{{ url_for('verify_payment') }}" class="hover:text-yellow-200 transition">Verify Payment</a>
                        <a href="{{ url_for('gold_trading') }}" class="hover:text-yellow-200 transition">Gold Trading</a>
                        <a href="{{ url_for('transaction_history') }}" class="hover:text-yellow-200 transition">History</a>
                        <a href="{{ url_for('logout') }}" class="hover:text-yellow-200 transition">Logout</a>
                    {% else %}
                        <a href="{{ url_for('index') }}" class="hover:text-yellow-200 transition">Home</a>
                        <a href="{{ url_for('login') }}" class="hover:text-yellow-200 transition">Login</a>
                    {% endif %}
                </div>
            </div>
        </div>
    </nav>

    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="container mx-auto px-4 mt-4">
                {% for category, message in messages %}
                    <div class="alert p-4 rounded-lg mb-4 
                                {% if category == 'success' %}bg-green-100 text-green-800 border border-green-300
                                {% else %}bg-red-100 text-red-800 border border-red-300{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <main class="container mx-auto px-4 py-8">
        {% block content %}{% endblock %}
    </main>

    <footer class="bg-gray-800 text-white mt-12">
        <div class="container mx-auto px-4 py-8">
            <div class="text-center">
                <p>&copy; 2024 GoldXAU Investment. All rights reserved.</p>
                <p class="text-gray-400 mt-2">Invest in Gold - Secure Your Future</p>
            </div>
        </div>
    </footer>

    <script>
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
        }
        
        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
        }
        
        function setupDragAndDrop() {
            const dropArea = document.getElementById('dropArea');
            if (!dropArea) return;
            
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropArea.addEventListener(eventName, preventDefaults, false);
            });
            
            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            ['dragenter', 'dragover'].forEach(eventName => {
                dropArea.addEventListener(eventName, highlight, false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                dropArea.addEventListener(eventName, unhighlight, false);
            });
            
            function highlight() {
                dropArea.classList.add('dragover');
            }
            
            function unhighlight() {
                dropArea.classList.remove('dragover');
            }
            
            dropArea.addEventListener('drop', handleDrop, false);
            
            function handleDrop(e) {
                const dt = e.dataTransfer;
                const files = dt.files;
                document.getElementById('receiptImage').files = files;
            }
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            setupDragAndDrop();
        });
    </script>
    
    <div id="loading" class="loading fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white p-8 rounded-lg text-center">
            <i class="fas fa-spinner fa-spin text-3xl text-yellow-600 mb-4"></i>
            <p class="text-lg font-semibold">Processing...</p>
        </div>
    </div>
</body>
</html>
    ''',

    'index': '''
{% extends "base.html" %}
{% block title %}Home - GoldXAU Investment{% endblock %}
{% block content %}
<div class="text-center py-12">
    <h1 class="text-5xl font-bold text-gray-800 mb-6">Invest in Gold with Confidence</h1>
    <p class="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
        Secure your financial future with our gold investment platform. 
        Easy payment verification and real-time gold trading.
    </p>
    <div class="space-x-4">
        <a href="{{ url_for('login') }}" class="bg-yellow-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-yellow-700 transition">
            Start Investing
        </a>
        <a href="{{ url_for('gold_trading') }}" class="border-2 border-yellow-600 text-yellow-600 px-8 py-3 rounded-lg font-semibold hover:bg-yellow-50 transition">
            View Gold Prices
        </a>
    </div>
</div>

<div class="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
    <div class="text-center p-6 bg-white rounded-lg shadow-lg">
        <i class="fas fa-receipt text-4xl text-yellow-600 mb-4"></i>
        <h3 class="text-xl font-semibold mb-2">Receipt Verification</h3>
        <p class="text-gray-600">Upload payment receipts for automatic verification and instant funding</p>
    </div>
    <div class="text-center p-6 bg-white rounded-lg shadow-lg">
        <i class="fas fa-chart-line text-4xl text-yellow-600 mb-4"></i>
        <h3 class="text-xl font-semibold mb-2">Real-time Gold Prices</h3>
        <p class="text-gray-600">Live XAU/USD prices with advanced trading tools</p>
    </div>
    <div class="text-center p-6 bg-white rounded-lg shadow-lg">
        <i class="fas fa-shield-alt text-4xl text-yellow-600 mb-4"></i>
        <h3 class="text-xl font-semibold mb-2">Secure Platform</h3>
        <p class="text-gray-600">Bank-level security for all your transactions and investments</p>
    </div>
</div>
{% endblock %}
    ''',

    'login': '''
{% extends "base.html" %}
{% block title %}Login - GoldXAU Investment{% endblock %}
{% block content %}
<div class="max-w-md mx-auto bg-white rounded-lg shadow-lg p-8">
    <h2 class="text-2xl font-bold text-center mb-6">Welcome Back</h2>
    <form method="POST" action="{{ url_for('login') }}">
        <div class="mb-4">
            <label class="block text-gray-700 mb-2">Email Address</label>
            <input type="email" name="email" required 
                   class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                   placeholder="your@email.com">
        </div>
        <div class="mb-4">
            <label class="block text-gray-700 mb-2">Full Name</label>
            <input type="text" name="full_name" required 
                   class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                   placeholder="Your Full Name">
        </div>
        <button type="submit" class="w-full bg-yellow-600 text-white py-3 rounded-lg font-semibold hover:bg-yellow-700 transition">
            Continue to Dashboard
        </button>
    </form>
    <p class="text-gray-600 text-center mt-4 text-sm">
        By continuing, you agree to our Terms of Service and Privacy Policy
    </p>
</div>
{% endblock %}
    ''',

    'dashboard': '''
{% extends "base.html" %}
{% block title %}Dashboard - GoldXAU Investment{% endblock %}
{% block content %}
<div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
    <div class="lg:col-span-2">
        <h1 class="text-3xl font-bold mb-8">Welcome, {{ user.full_name }}!</h1>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div class="bg-white p-6 rounded-lg shadow-lg border-l-4 border-green-500">
                <h3 class="text-gray-600">Cash Balance</h3>
                <p class="text-2xl font-bold">${{ "%.2f"|format(user.balance) }}</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow-lg border-l-4 border-yellow-500">
                <h3 class="text-gray-600">Gold Balance</h3>
                <p class="text-2xl font-bold">{{ "%.3f"|format(user.gold_balance) }} oz</p>
            </div>
        </div>

        <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">Quick Actions</h2>
            <div class="flex flex-wrap gap-4">
                <a href="{{ url_for('verify_payment') }}" class="bg-yellow-600 text-white px-6 py-2 rounded-lg hover:bg-yellow-700 transition">
                    Verify Payment
                </a>
                <a href="{{ url_for('gold_trading') }}" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition">
                    Trade Gold
                </a>
                <a href="{{ url_for('transaction_history') }}" class="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition">
                    View History
                </a>
            </div>
        </div>
    </div>

    <div class="bg-white rounded-lg shadow-lg p-6">
        <h2 class="text-xl font-semibold mb-4">Gold Price</h2>
        <div id="goldPrice" class="text-3xl font-bold text-yellow-600 mb-4">
            Loading...
        </div>
        <div class="text-sm text-gray-600">
            <p>XAU/USD Live Price</p>
            <p class="mt-2">Last updated: <span id="priceTime">-</span></p>
        </div>
        
        <div class="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 class="font-semibold mb-2">Payment Instructions</h3>
            <ul class="text-sm space-y-1">
                <li>• Use reference: invest12345</li>
                <li>• Recipient: OLUWATOBILOBA SHERIFDEEN KEHINDE</li>
                <li>• Upload receipt after payment</li>
            </ul>
        </div>
    </div>
</div>

<script>
function updateGoldPrice() {
    fetch('/api/gold_price')
        .then(response => response.json())
        .then(data => {
            document.getElementById('goldPrice').textContent = '$' + data.price.toFixed(2);
            document.getElementById('priceTime').textContent = new Date().toLocaleTimeString();
        })
        .catch(error => {
            console.error('Error fetching gold price:', error);
        });
}

// Update price immediately and every 30 seconds
updateGoldPrice();
setInterval(updateGoldPrice, 30000);
</script>
{% endblock %}
    ''',

    'verify_payment': '''
{% extends "base.html" %}
{% block title %}Verify Payment - GoldXAU Investment{% endblock %}
{% block content %}
<div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold mb-8">Verify Payment Receipt</h1>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div class="bg-white rounded-lg shadow-lg p-6">
            <h2 class="text-xl font-semibold mb-4">Upload Receipt</h2>
            
            <form method="POST" enctype="multipart/form-data" onsubmit="showLoading()">
                <div id="dropArea" class="receipt-box border-2 border-dashed rounded-lg p-8 text-center mb-4 cursor-pointer">
                    <i class="fas fa-cloud-upload-alt text-4xl text-gray-400 mb-4"></i>
                    <p class="text-gray-600 mb-2">Drag & drop your receipt image here</p>
                    <p class="text-sm text-gray-500">or click to select file</p>
                    <input type="file" id="receiptImage" name="receipt_image" accept="image/*" class="hidden" required>
                </div>
                
                <div class="mb-4">
                    <label class="block text-gray-700 mb-2">Or paste receipt text:</label>
                    <textarea name="receipt_text" rows="8" 
                              class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                              placeholder="Paste the entire receipt text here..."></textarea>
                </div>
                
                <button type="submit" class="w-full bg-yellow-600 text-white py-3 rounded-lg font-semibold hover:bg-yellow-700 transition">
                    Verify Payment
                </button>
            </form>
        </div>

        <div class="bg-white rounded-lg shadow-lg p-6">
            <h2 class="text-xl font-semibold mb-4">Verification Guidelines</h2>
            
            <div class="space-y-4">
                <div class="p-4 bg-green-50 rounded-lg">
                    <h3 class="font-semibold text-green-800">✅ Required Information</h3>
                    <ul class="text-sm text-green-700 mt-2 space-y-1">
                        <li>• Amount transferred</li>
                        <li>• Sender name matching your account</li>
                        <li>• Recipient: OLUWATOBILOBA SHERIFDEEN KEHINDE</li>
                        <li>• Transaction timestamp</li>
                        <li>• Reference containing "invest"</li>
                    </ul>
                </div>
                
                <div class="p-4 bg-yellow-50 rounded-lg">
                    <h3 class="font-semibold text-yellow-800">📝 Reference Examples</h3>
                    <ul class="text-sm text-yellow-700 mt-2 space-y-1">
                        <li>• invest12345</li>
                        <li>• gold67890</li>
                        <li>• xau54321</li>
                        <li>• investment999</li>
                    </ul>
                </div>
                
                <div class="p-4 bg-blue-50 rounded-lg">
                    <h3 class="font-semibold text-blue-800">⚡ Processing Time</h3>
                    <p class="text-sm text-blue-700 mt-2">
                        Payments are verified within 5-15 minutes during business hours. 
                        You will receive email confirmation once processed.
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.getElementById('dropArea').addEventListener('click', function() {
    document.getElementById('receiptImage').click();
});

document.getElementById('receiptImage').addEventListener('change', function(e) {
    if (e.target.files.length > 0) {
        document.getElementById('dropArea').innerHTML = 
            '<i class="fas fa-file-image text-4xl text-green-500 mb-4"></i>' +
            '<p class="text-green-600">File selected: ' + e.target.files[0].name + '</p>';
    }
});
</script>
{% endblock %}
    ''',

    'gold_trading': '''
{% extends "base.html" %}
{% block title %}Gold Trading - GoldXAU Investment{% endblock %}
{% block content %}
<div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-8">Gold Trading (XAU/USD)</h1>
    
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div class="lg:col-span-2">
            <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-2xl font-bold">Current Gold Price</h2>
                    <div id="goldPriceDisplay" class="text-3xl font-bold text-yellow-600">
                        Loading...
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <h3 class="font-semibold mb-2">Buy Gold</h3>
                        <form method="POST" action="{{ url_for('buy_gold') }}" onsubmit="showLoading()">
                            <div class="mb-4">
                                <label class="block text-gray-700 mb-2">Amount (USD)</label>
                                <input type="number" name="amount" step="0.01" min="10" required
                                       class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent">
                            </div>
                            <button type="submit" class="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition">
                                Buy Gold
                            </button>
                        </form>
                    </div>
                    
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <h3 class="font-semibold mb-2">Sell Gold</h3>
                        <form method="POST" action="{{ url_for('sell_gold') }}" onsubmit="showLoading()">
                            <div class="mb-4">
                                <label class="block text-gray-700 mb-2">Gold Amount (oz)</label>
                                <input type="number" name="gold_amount" step="0.001" min="0.001" required
                                       class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent">
                            </div>
                            <button type="submit" class="w-full bg-red-600 text-white py-3 rounded-lg font-semibold hover:bg-red-700 transition">
                                Sell Gold
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow-lg p-6">
            <h2 class="text-xl font-semibold mb-4">Account Summary</h2>
            <div class="space-y-4">
                <div>
                    <p class="text-gray-600">Cash Balance</p>
                    <p class="text-2xl font-bold">${{ "%.2f"|format(user.balance) }}</p>
                </div>
                <div>
                    <p class="text-gray-600">Gold Balance</p>
                    <p class="text-2xl font-bold text-yellow-600">{{ "%.3f"|format(user.gold_balance) }} oz</p>
                </div>
                <div>
                    <p class="text-gray-600">Portfolio Value</p>
                    <p class="text-2xl font-bold" id="portfolioValue">Calculating...</p>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function updateTradingInfo() {
    fetch('/api/gold_price')
        .then(response => response.json())
        .then(data => {
            const goldPrice = data.price;
            document.getElementById('goldPriceDisplay').textContent = '$' + goldPrice.toFixed(2);
            
            // Calculate portfolio value
            const goldBalance = {{ user.gold_balance }};
            const portfolioValue = (goldBalance * goldPrice) + {{ user.balance }};
            document.getElementById('portfolioValue').textContent = '$' + portfolioValue.toFixed(2);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Update trading info immediately and every 10 seconds
updateTradingInfo();
setInterval(updateTradingInfo, 10000);
</script>
{% endblock %}
    ''',

    'transaction_history': '''
{% extends "base.html" %}
{% block title %}Transaction History - GoldXAU Investment{% endblock %}
{% block content %}
<div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-8">Transaction History</h1>
    
    <div class="bg-white rounded-lg shadow-lg overflow-hidden">
        <div class="overflow-x-auto">
            <table class="w-full">
                <thead class="bg-gray-100">
                    <tr>
                        <th class="p-4 text-left">Date</th>
                        <th class="p-4 text-left">Type</th>
                        <th class="p-4 text-left">Amount</th>
                        <th class="p-4 text-left">Gold</th>
                        <th class="p-4 text-left">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for transaction in transactions %}
                    <tr class="border-b hover:bg-gray-50">
                        <td class="p-4">{{ transaction.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                        <td class="p-4">
                            <span class="px-2 py-1 rounded-full text-xs 
                                {% if transaction.type == 'deposit' %}bg-green-100 text-green-800
                                {% elif transaction.type == 'gold_purchase' %}bg-yellow-100 text-yellow-800
                                {% else %}bg-red-100 text-red-800{% endif %}">
                                {{ transaction.type|replace('_', ' ')|title }}
                            </span>
                        </td>
                        <td class="p-4">
                            {% if transaction.amount %}
                                ${{ "%.2f"|format(transaction.amount) }}
                            {% else %}
                                -
                            {% endif %}
                        </td>
                        <td class="p-4">
                            {% if transaction.gold_amount %}
                                {{ "%.3f"|format(transaction.gold_amount) }} oz
                            {% else %}
                                -
                            {% endif %}
                        </td>
                        <td class="p-4">
                            <span class="px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                                {{ transaction.status }}
                            </span>
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="5" class="p-8 text-center text-gray-500">
                            No transactions found.
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
    '''
}

# Payment Receipt Parser
class ReceiptParser:
    @staticmethod
    def parse_receipt_text(text):
        """Parse receipt text and extract transaction details"""
        try:
            lines = text.split('\n')
            parsed_data = {
                'amount': None,
                'sender_name': None,
                'recipient_name': None,
                'timestamp': None,
                'transaction_id': None,
                'session_id': None,
                'reference_text': None,
                'status': 'successful'
            }
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Extract amount
                if not parsed_data['amount']:
                    amount_match = re.search(r'[\d,]+\.\d{2}', line)
                    if amount_match:
                        parsed_data['amount'] = float(amount_match.group().replace(',', ''))
                
                # Extract timestamp
                if not parsed_data['timestamp']:
                    timestamp_match = re.search(r'[A-Za-z]{3} \d{1,2},? \d{4}.*\d{1,2}:\d{2}', line)
                    if timestamp_match:
                        try:
                            parsed_data['timestamp'] = datetime.strptime(
                                timestamp_match.group(), '%b %d, %Y %I:%M:%S %p'
                            )
                        except:
                            try:
                                parsed_data['timestamp'] = datetime.strptime(
                                    timestamp_match.group(), '%b %d, %Y %I:%M %p'
                                )
                            except:
                                pass
                
                # Extract sender name
                if 'sender' in line.lower() and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not any(x in next_line.lower() for x in ['transaction', 'recipient', '---']):
                        parsed_data['sender_name'] = next_line
                
                # Extract recipient name
                if 'recipient' in line.lower() and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not any(x in next_line.lower() for x in ['transaction', 'sender', '---']):
                        parsed_data['recipient_name'] = next_line
                
                # Extract transaction ID
                if 'transaction id' in line.lower():
                    parts = line.split(':')
                    if len(parts) > 1:
                        parsed_data['transaction_id'] = parts[1].strip()
                
                # Extract session ID
                if 'session id' in line.lower():
                    parts = line.split(':')
                    if len(parts) > 1:
                        parsed_data['session_id'] = parts[1].strip()
                
                # Extract reference text
                if any(keyword in line.lower() for keyword in ['reference', 'what\'s it for', 'purpose']):
                    parts = line.split(':')
                    if len(parts) > 1:
                        parsed_data['reference_text'] = parts[1].strip()
            
            return parsed_data
        except Exception as e:
            print(f"Error parsing receipt: {e}")
            return None

    @staticmethod
    def validate_receipt(parsed_data, user_full_name):
        """Validate parsed receipt data"""
        if not parsed_data:
            return False, "Unable to parse receipt data"
        
        # Check required fields
        if not parsed_data['amount']:
            return False, "Could not extract amount from receipt"
        
        if not parsed_data['sender_name']:
            return False, "Could not extract sender name from receipt"
        
        if not parsed_data['recipient_name']:
            return False, "Could not extract recipient name from receipt"
        
        # Validate sender name matches user
        if user_full_name.upper() not in parsed_data['sender_name'].upper():
            return False, f"Sender name '{parsed_data['sender_name']}' doesn't match your account name '{user_full_name}'"
        
        # Validate recipient name
        valid_recipient = any(recipient in parsed_data['recipient_name'].upper() for recipient in RECIPIENT_NAMES)
        if not valid_recipient:
            return False, f"Invalid recipient: {parsed_data['recipient_name']}"
        
        # Validate reference text
        if parsed_data['reference_text']:
            valid_reference = any(re.search(pattern, parsed_data['reference_text'].lower()) for pattern in REFERENCE_PATTERNS)
            if not valid_reference:
                return False, f"Invalid reference text: {parsed_data['reference_text']}"
        
        # Validate timestamp (should be within last 24 hours)
        if parsed_data['timestamp']:
            time_diff = datetime.utcnow() - parsed_data['timestamp']
            if time_diff > timedelta(hours=24):
                return False, "Receipt is too old (more than 24 hours)"
        
        return True, "Receipt validated successfully"

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template_string(HTML_TEMPLATES['index'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        full_name = request.form['full_name'].strip()
        
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, full_name=full_name)
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully!', 'success')
        else:
            # Update name if different
            if user.full_name != full_name:
                user.full_name = full_name
                db.session.commit()
        
        session['user_id'] = user.id
        session['user_email'] = user.email
        return redirect(url_for('dashboard'))
    
    return render_template_string(HTML_TEMPLATES['login'])

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template_string(HTML_TEMPLATES['dashboard'], user=user)

@app.route('/verify_payment', methods=['GET', 'POST'])
def verify_payment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        receipt_text = request.form.get('receipt_text', '').strip()
        
        if not receipt_text:
            flash('Please provide receipt text', 'error')
            return redirect(url_for('verify_payment'))
        
        # Parse receipt
        parser = ReceiptParser()
        parsed_data = parser.parse_receipt_text(receipt_text)
        
        if not parsed_data:
            flash('Could not parse receipt. Please check the format and try again.', 'error')
            return redirect(url_for('verify_payment'))
        
        # Validate receipt
        is_valid, message = parser.validate_receipt(parsed_data, user.full_name)
        
        if not is_valid:
            flash(f'Validation failed: {message}', 'error')
            return redirect(url_for('verify_payment'))
        
        # Check for duplicate transaction
        existing_payment = PaymentReceipt.query.filter_by(
            transaction_id=parsed_data['transaction_id']
        ).first()
        
        if existing_payment:
            flash('This payment has already been verified.', 'error')
            return redirect(url_for('verify_payment'))
        
        # Create payment record
        payment = PaymentReceipt(
            user_id=user.id,
            amount=parsed_data['amount'],
            sender_name=parsed_data['sender_name'],
            recipient_name=parsed_data['recipient_name'],
            transaction_id=parsed_data['transaction_id'],
            session_id=parsed_data['session_id'],
            timestamp=parsed_data['timestamp'] or datetime.utcnow(),
            reference_text=parsed_data['reference_text'],
            status='verified',
            verified_at=datetime.utcnow()
        )
        
        # Fund user account
        user.balance += parsed_data['amount']
        
        # Create transaction record
        transaction = Transaction(
            user_id=user.id,
            type='deposit',
            amount=parsed_data['amount'],
            status='completed'
        )
        
        db.session.add(payment)
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Payment verified successfully! ${parsed_data["amount"]:.2f} has been added to your account.', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template_string(HTML_TEMPLATES['verify_payment'], user=user)

@app.route('/gold_trading')
def gold_trading():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template_string(HTML_TEMPLATES['gold_trading'], user=user)

@app.route('/buy_gold', methods=['POST'])
def buy_gold():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    amount = float(request.form['amount'])
    
    if amount > user.balance:
        flash('Insufficient balance', 'error')
        return redirect(url_for('gold_trading'))
    
    # Get current gold price
    gold_service = GoldAPIService()
    gold_price = gold_service.get_gold_price()
    
    # Calculate gold amount
    gold_amount = amount / gold_price
    
    # Update user balances
    user.balance -= amount
    user.gold_balance += gold_amount
    
    # Create transaction record
    transaction = Transaction(
        user_id=user.id,
        type='gold_purchase',
        amount=amount,
        gold_amount=gold_amount,
        gold_price=gold_price,
        status='completed'
    )
    
    # Save gold price
    gold_price_record = GoldPrice(price=gold_price)
    
    db.session.add(transaction)
    db.session.add(gold_price_record)
    db.session.commit()
    
    flash(f'Successfully purchased {gold_amount:.3f} oz of gold!', 'success')
    return redirect(url_for('gold_trading'))

@app.route('/sell_gold', methods=['POST'])
def sell_gold():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    gold_amount = float(request.form['gold_amount'])
    
    if gold_amount > user.gold_balance:
        flash('Insufficient gold balance', 'error')
        return redirect(url_for('gold_trading'))
    
    # Get current gold price
    gold_service = GoldAPIService()
    gold_price = gold_service.get_gold_price()
    
    # Calculate USD amount
    usd_amount = gold_amount * gold_price
    
    # Update user balances
    user.balance += usd_amount
    user.gold_balance -= gold_amount
    
    # Create transaction record
    transaction = Transaction(
        user_id=user.id,
        type='gold_sale',
        amount=usd_amount,
        gold_amount=gold_amount,
        gold_price=gold_price,
        status='completed'
    )
    
    # Save gold price
    gold_price_record = GoldPrice(price=gold_price)
    
    db.session.add(transaction)
    db.session.add(gold_price_record)
    db.session.commit()
    
    flash(f'Successfully sold {gold_amount:.3f} oz of gold for ${usd_amount:.2f}!', 'success')
    return redirect(url_for('gold_trading'))

@app.route('/transaction_history')
def transaction_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    transactions = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.created_at.desc()).all()
    
    return render_template_string(HTML_TEMPLATES['transaction_history'], 
                                user=user, 
                                transactions=transactions)

@app.route('/api/gold_price')
def api_gold_price():
    gold_service = GoldAPIService()
    price = gold_service.get_gold_price()
    return jsonify({'price': price, 'timestamp': datetime.utcnow().isoformat()})

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)