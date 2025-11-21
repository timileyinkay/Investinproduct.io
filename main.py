from flask import Flask, request, render_template_string

app = Flask(__name__)

# HTML template with form
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Welcome!</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 500px; margin: 0 auto; }
        input[type="email"] { width: 100%; padding: 10px; margin: 10px 0; }
        input[type="submit"] { background: #007cba; color: white; padding: 10px 20px; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to Our Site!</h1>
        {% if name %}
            <h2>Hello, {{ name }}! 👋</h2>
            <p>Nice to see you here!</p>
            <a href="/">Go Back</a>
        {% else %}
            <form method="POST">
                <p>Enter your email to get a personalized greeting:</p>
                <input type="email" name="email" placeholder="your@email.com" required>
                <input type="submit" value="Get Greeting">
            </form>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def welcome():
    if request.method == 'POST':
        email = request.form['email']
        # Extract name from email (part before @)
        name = email.split('@')[0]
        # Capitalize first letter
        name = name.capitalize()
        return render_template_string(HTML_TEMPLATE, name=name)
    
    return render_template_string(HTML_TEMPLATE, name=None)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)