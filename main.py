from flask import Flask, render_template, request, jsonify
import cv2
import pytesseract
import numpy as np
import re
import json
import os
from werkzeug.utils import secure_filename
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class ReceiptExtractor:
    def __init__(self):
        pass
    
    def preprocess_image(self, image_path):
        """Preprocess the image for better OCR results"""
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        denoised = cv2.medianBlur(gray, 5)
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
    
    def extract_text(self, image_path):
        """Extract all text from receipt image"""
        processed_img = self.preprocess_image(image_path)
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,$€£/-: '
        text = pytesseract.image_to_string(processed_img, config=custom_config)
        return text
    
    def parse_receipt_data(self, text):
        """Parse extracted text to structured data"""
        lines = text.split('\n')
        receipt_data = {
            'store_name': '',
            'date': '',
            'time': '',
            'items': [],
            'subtotal': '',
            'tax': '',
            'total': '',
            'payment_method': ''
        }
        
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
        time_pattern = r'\d{1,2}:\d{2}\s*(?:AM|PM)?'
        currency_pattern = r'[$€£]?\s*\d+\.\d{2}'
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            if not receipt_data['store_name'] and len(line) > 3:
                receipt_data['store_name'] = line
            
            date_match = re.search(date_pattern, line)
            if date_match and not receipt_data['date']:
                receipt_data['date'] = date_match.group()
            
            time_match = re.search(time_pattern, line, re.IGNORECASE)
            if time_match and not receipt_data['time']:
                receipt_data['time'] = time_match.group()
            
            if re.search(r'TOTAL|AMOUNT DUE|GRAND TOTAL', line, re.IGNORECASE):
                currency_match = re.search(currency_pattern, line)
                if currency_match:
                    receipt_data['total'] = currency_match.group()
            
            if re.search(r'SUBTOTAL|SUB-TOTAL', line, re.IGNORECASE):
                currency_match = re.search(currency_pattern, line)
                if currency_match:
                    receipt_data['subtotal'] = currency_match.group()
            
            if re.search(r'TAX|VAT|GST', line, re.IGNORECASE):
                currency_match = re.search(currency_pattern, line)
                if currency_match:
                    receipt_data['tax'] = currency_match.group()
            
            if re.search(r'CASH|CARD|CREDIT|DEBIT|VISA|MASTERCARD', line, re.IGNORECASE):
                receipt_data['payment_method'] = line
            
            if re.search(currency_pattern, line) and len(line) > 5:
                item_parts = re.split(r'\s{2,}', line)
                if len(item_parts) >= 2:
                    item_name = item_parts[0].strip()
                    price_match = re.search(currency_pattern, line)
                    if price_match and len(item_name) > 1:
                        receipt_data['items'].append({
                            'name': item_name,
                            'price': price_match.group()
                        })
        
        return receipt_data
    
    def process_receipt(self, image_path):
        """Main method to process receipt and return structured data"""
        try:
            text = self.extract_text(image_path)
            structured_data = self.parse_receipt_data(text)
            
            return {
                'success': True,
                'raw_text': text,
                'structured_data': structured_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'raw_text': '',
                'structured_data': {}
            }

extractor = ReceiptExtractor()

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Receipt Text Extractor</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }

            .header {
                background: linear-gradient(135deg, #2c3e50, #34495e);
                color: white;
                padding: 30px;
                text-align: center;
            }

            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }

            .header p {
                font-size: 1.2em;
                opacity: 0.9;
            }

            .content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                padding: 40px;
            }

            @media (max-width: 768px) {
                .content {
                    grid-template-columns: 1fr;
                }
            }

            .upload-section {
                background: #f8f9fa;
                padding: 30px;
                border-radius: 10px;
                border: 2px dashed #dee2e6;
            }

            .upload-area {
                text-align: center;
                padding: 40px 20px;
                border: 2px dashed #667eea;
                border-radius: 10px;
                background: #f8f9ff;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .upload-area:hover {
                background: #eef2ff;
                border-color: #5a67d8;
            }

            .upload-icon {
                font-size: 3em;
                color: #667eea;
                margin-bottom: 15px;
            }

            .file-input {
                display: none;
            }

            .upload-btn {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 25px;
                font-size: 1.1em;
                cursor: pointer;
                transition: transform 0.2s ease;
                margin-top: 15px;
            }

            .upload-btn:hover {
                transform: translateY(-2px);
            }

            .upload-btn:disabled {
                background: #6c757d;
                cursor: not-allowed;
                transform: none;
            }

            .results-section {
                background: white;
                padding: 30px;
                border-radius: 10px;
                border: 1px solid #e9ecef;
            }

            .results-container {
                max-height: 500px;
                overflow-y: auto;
            }

            .result-item {
                margin-bottom: 20px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }

            .result-item h3 {
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 1.1em;
            }

            .items-list {
                list-style: none;
            }

            .items-list li {
                padding: 8px;
                border-bottom: 1px solid #dee2e6;
                display: flex;
                justify-content: space-between;
            }

            .items-list li:last-child {
                border-bottom: none;
            }

            .loading {
                display: none;
                text-align: center;
                padding: 20px;
            }

            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 15px;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .error {
                background: #fee;
                color: #c53030;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #c53030;
                margin-top: 15px;
            }

            .success {
                background: #f0fff4;
                color: #2f855a;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #2f855a;
                margin-top: 15px;
            }

            .raw-text {
                background: #2d3748;
                color: #e2e8f0;
                padding: 15px;
                border-radius: 8px;
                font-family: 'Courier New', monospace;
                white-space: pre-wrap;
                font-size: 0.9em;
                max-height: 200px;
                overflow-y: auto;
            }

            .file-info {
                margin-top: 10px;
                font-size: 0.9em;
                color: #6c757d;
            }

            .preview-image {
                max-width: 100%;
                max-height: 200px;
                border-radius: 8px;
                margin-top: 15px;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧾 Receipt Text Extractor</h1>
                <p>Upload a receipt image to extract and verify text information</p>
            </div>
            
            <div class="content">
                <div class="upload-section">
                    <h2>Upload Receipt</h2>
                    <p>Supported formats: JPG, PNG, JPEG</p>
                    
                    <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                        <div class="upload-icon">📁</div>
                        <h3>Click to upload receipt</h3>
                        <p>or drag and drop your file here</p>
                        <input type="file" id="fileInput" class="file-input" accept=".jpg,.jpeg,.png" onchange="handleFileSelect(event)">
                    </div>
                    
                    <div id="fileInfo" class="file-info"></div>
                    <img id="previewImage" class="preview-image" alt="Preview">
                    
                    <button id="uploadBtn" class="upload-btn" onclick="uploadFile()" disabled>
                        Process Receipt
                    </button>
                    
                    <div class="loading" id="loading">
                        <div class="spinner"></div>
                        <p>Processing receipt... This may take a few seconds.</p>
                    </div>
                </div>
                
                <div class="results-section">
                    <h2>Extracted Information</h2>
                    <div id="resultsContainer" class="results-container">
                        <div id="initialMessage">
                            <p>Upload a receipt to see extracted information here.</p>
                        </div>
                        <div id="resultsContent" style="display: none;"></div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let selectedFile = null;
            let filePreviewUrl = null;

            function handleFileSelect(event) {
                const file = event.target.files[0];
                if (file) {
                    selectedFile = file;
                    
                    // Display file info
                    document.getElementById('fileInfo').textContent = 
                        `Selected: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
                    
                    // Enable upload button
                    document.getElementById('uploadBtn').disabled = false;
                    
                    // Show preview
                    const previewImage = document.getElementById('previewImage');
                    if (file.type.startsWith('image/')) {
                        if (filePreviewUrl) {
                            URL.revokeObjectURL(filePreviewUrl);
                        }
                        filePreviewUrl = URL.createObjectURL(file);
                        previewImage.src = filePreviewUrl;
                        previewImage.style.display = 'block';
                    }
                }
            }

            function uploadFile() {
                if (!selectedFile) return;
                
                const loadingElement = document.getElementById('loading');
                const uploadBtn = document.getElementById('uploadBtn');
                const resultsContent = document.getElementById('resultsContent');
                const initialMessage = document.getElementById('initialMessage');
                
                loadingElement.style.display = 'block';
                uploadBtn.disabled = true;
                
                const formData = new FormData();
                formData.append('file', selectedFile);
                
                fetch('/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    loadingElement.style.display = 'none';
                    uploadBtn.disabled = false;
                    
                    if (data.success) {
                        displayResults(data);
                        initialMessage.style.display = 'none';
                        resultsContent.style.display = 'block';
                    } else {
                        showError(data.error);
                    }
                })
                .catch(error => {
                    loadingElement.style.display = 'none';
                    uploadBtn.disabled = false;
                    showError('Network error: ' + error.message);
                });
            }

            function displayResults(data) {
                const resultsContent = document.getElementById('resultsContent');
                const structured = data.structured_data;
                
                let html = `
                    <div class="success">
                        ✅ Successfully extracted receipt information
                    </div>
                    
                    <div class="result-item">
                        <h3>🏪 Store Information</h3>
                        <p><strong>Store Name:</strong> ${structured.store_name || 'Not found'}</p>
                        <p><strong>Date:</strong> ${structured.date || 'Not found'}</p>
                        <p><strong>Time:</strong> ${structured.time || 'Not found'}</p>
                    </div>`;
                
                if (structured.items && structured.items.length > 0) {
                    html += `
                    <div class="result-item">
                        <h3>🛒 Purchased Items</h3>
                        <ul class="items-list">`;
                    
                    structured.items.forEach(item => {
                        html += `<li><span>${item.name}</span><span>${item.price}</span></li>`;
                    });
                    
                    html += `</ul></div>`;
                }
                
                html += `
                    <div class="result-item">
                        <h3>💰 Payment Details</h3>
                        <p><strong>Subtotal:</strong> ${structured.subtotal || 'Not found'}</p>
                        <p><strong>Tax:</strong> ${structured.tax || 'Not found'}</p>
                        <p><strong>Total:</strong> ${structured.total || 'Not found'}</p>
                        <p><strong>Payment Method:</strong> ${structured.payment_method || 'Not found'}</p>
                    </div>
                    
                    <div class="result-item">
                        <h3>📝 Raw Extracted Text</h3>
                        <div class="raw-text">${data.raw_text || 'No text extracted'}</div>
                    </div>`;
                
                resultsContent.innerHTML = html;
            }

            function showError(message) {
                const resultsContent = document.getElementById('resultsContent');
                const initialMessage = document.getElementById('initialMessage');
                
                initialMessage.style.display = 'none';
                resultsContent.style.display = 'block';
                resultsContent.innerHTML = `
                    <div class="error">
                        ❌ Error: ${message}
                    </div>
                `;
            }

            // Drag and drop functionality
            document.addEventListener('DOMContentLoaded', function() {
                const uploadArea = document.querySelector('.upload-area');
                
                uploadArea.addEventListener('dragover', function(e) {
                    e.preventDefault();
                    uploadArea.style.background = '#eef2ff';
                    uploadArea.style.borderColor = '#5a67d8';
                });
                
                uploadArea.addEventListener('dragleave', function(e) {
                    e.preventDefault();
                    uploadArea.style.background = '#f8f9ff';
                    uploadArea.style.borderColor = '#667eea';
                });
                
                uploadArea.addEventListener('drop', function(e) {
                    e.preventDefault();
                    uploadArea.style.background = '#f8f9ff';
                    uploadArea.style.borderColor = '#667eea';
                    
                    const files = e.dataTransfer.files;
                    if (files.length > 0) {
                        const fileInput = document.getElementById('fileInput');
                        fileInput.files = files;
                        handleFileSelect({target: {files: files}});
                    }
                });
            });
        </script>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if file:
        # Validate file type
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload JPG, JPEG, or PNG images.'})
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the receipt
        result = extractor.process_receipt(filepath)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)