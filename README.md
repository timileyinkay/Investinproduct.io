# Investinproduct.io<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Investment Hub</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #0d47a1, #1976d2);
            color: #fff;
            text-align: center;
            padding-top: 10%;
            position: relative;
            overflow: hidden;
        }

        .box {
            background: rgba(0, 0, 0, 0.8);
            border-radius: 10px;
            padding: 20px;
            width: 300px;
            margin: 0 auto;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            display: none;
            position: relative;
            z-index: 10;
        }

        input[type="text"],
        input[type="password"] {
            width: 90%;
            padding: 10px;
            margin: 10px 0;
            border: none;
            border-radius: 5px;
        }

        button {
            background: #4caf50;
            color: #fff;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
        }

        button:hover {
            background: #45a049;
        }

        .error {
            color: #f44336;
            font-size: 0.9em;
        }

        .link {
            color: #4caf50;
            cursor: pointer;
            text-decoration: underline;
        }

        .pay-button {
            background: #ff9800;
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }

        /* New Section: Benefits */
        .benefits {
            background: rgba(255, 255, 255, 0.9);
            color: #000;
            border-radius: 10px;
            padding: 20px;
            width: 300px;
            margin: 20px auto;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        .benefits h3 {
            color: #1976d2;
        }

        .benefits ul {
            text-align: left;
            padding-left: 20px;
        }

        .benefits ul li {
            margin-bottom: 10px;
        }

        /* Hamburger Menu */
        .hamburger-menu {
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 100;
            cursor: pointer;
        }

        .hamburger-menu div {
            width: 30px;
            height: 4px;
            background-color: #fff;
            margin: 6px 0;
            transition: 0.4s;
        }

        .menu-options {
            display: none;
            position: absolute;
            top: 40px;
            left: 20px;
            background-color: rgba(0, 0, 0, 0.7);
            padding: 10px;
            border-radius: 5px;
        }

        .menu-options a {
            color: #fff;
            text-decoration: none;
            display: block;
            padding: 8px 15px;
        }

        .menu-options a:hover {
            background-color: #555;
        }

        .background-shapes {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
        }

        .shape {
            position: absolute;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            animation: moveShape 8s infinite ease-in-out;
        }

        .shape:nth-child(1) {
            width: 250px;
            height: 250px;
            top: 10%;
            left: 15%;
            animation-duration: 10s;
        }

        .shape:nth-child(2) {
            width: 300px;
            height: 300px;
            top: 25%;
            left: 60%;
            animation-duration: 12s;
        }

        .shape:nth-child(3) {
            width: 200px;
            height: 200px;
            top: 40%;
            left: 40%;
            animation-duration: 14s;
        }

        .shape:nth-child(4) {
            width: 150px;
            height: 150px;
            top: 60%;
            left: 80%;
            animation-duration: 16s;
        }

        @keyframes moveShape {
            0% {
                transform: translateY(0) scale(1);
            }
            50% {
                transform: translateY(-50px) scale(1.1);
            }
            100% {
                transform: translateY(0) scale(1);
            }
        }
    </style>
</head>
<body>
    <!-- Hamburger Menu -->
    <div class="hamburger-menu" onclick="toggleMenu()">
        <div></div>
        <div></div>
        <div></div>
    </div>

    <div class="menu-options" id="menu-options">
        <a href="#" onclick="showHome()">Home</a>
        <a href="#">About</a>
        <a href="#">Commission</a>
    </div>

    <!-- 3D Background Shapes -->
    <div class="background-shapes">
        <div class="shape"></div>
        <div class="shape"></div>
        <div class="shape"></div>
        <div class="shape"></div>
    </div>

    <!-- Investment Platform Benefits -->
    <div class="benefits">
        <h3>Why Choose Our Platform?</h3>
        <ul>
            <li>🌟 High Returns on Investment</li>
            <li>🔒 Secure and Reliable Transactions</li>
            <li>🚀 Fast Growth Opportunities</li>
            <li>📈 Flexible Investment Plans</li>
            <li>🤝 Transparent and Trustworthy</li>
        </ul>
    </div>

    <!-- Sign In Box -->
    <div class="box" id="signin-box">
        <h2>Sign In</h2>
        <input type="text" id="signin-username" placeholder="Username" required>
        <input type="password" id="signin-password" placeholder="Password" required>
        <button onclick="validateLogin()">Sign In</button>
        <p class="error" id="signin-error"></p>
        <p>Don't have an account? <span class="link" onclick="showSignup()">Sign Up</span></p>
    </div>

    <!-- Sign Up Box -->
    <div class="box" id="signup-box">
        <h2>Sign Up</h2>
        <input type="text" id="signup-username" placeholder="Create Username" required>
        <input type="password" id="signup-password" placeholder="Create Password" required>
        <button onclick="register()">Sign Up</button>
        <p>Already have an account? <span class="link" onclick="showSignin()">Sign In</span></p>
    </div>

    <!-- Home Page -->
    <div class="box" id="home-box">
        <h1>Investment Opportunities</h1>
        <p id="status"></p>
        <button class="pay-button" onclick="showPaymentDetails()">Pay &#8358;1000 to Invest</button>
        <button onclick="logout()">Logout</button>
    </div>

    <!-- Payment Details Box -->
    <div class="box" id="payment-box">
        <h2>Make Payment</h2>
        <p>To proceed with your investment, pay &#8358;1000 to:</p>
        <p><strong>Opay Account:</strong> 8079304530</p>
        <p><strong>Account Name:</strong> Sherifden Kehinde</p>
        <p>After payment, click the button below to confirm.</p>
        <button onclick="confirmPayment()">I Have Paid</button>
        <button onclick="showHome()">Go Back</button>
    </div>

    <script>
        // Show Sign In by default
        window.onload = function() {
            showSignin();
        }

        // Navigation Functions
        function toggleMenu() {
            const menu = document.getElementById("menu-options");
            menu.style.display = menu.style.display === "block" ? "none" : "block";
        }

        function showSignin() {
            document.getElementById("signin-box").style.display = "block";
            document.getElementById("signup-box").style.display = "none";
            document.getElementById("home-box").style.display = "none";
            document.getElementById("payment-box").style.display = "none";
        }

        function showSignup() {
            document.getElementById("signin-box").style.display = "none";
            document.getElementById("signup-box").style.display = "block";
            document.getElementById("home-box").style.display = "none";
            document.getElementById("payment-box").style.display = "none";
        }

        function showHome() {
            document.getElementById("signin-box").style.display = "none";
            document.getElementById("signup-box").style.display = "none";
            document.getElementById("home-box").style.display = "block";
            document.getElementById("payment-box").style.display = "none";

            const hasPaid = localStorage.getItem("hasPaid");
            if (hasPaid === "true") {
                document.getElementById("status").textContent = "You have access to invest!";
            } else {
                document.getElementById("status").textContent = "You need to pay before investing.";
            }
        }

        function showPaymentDetails() {
            document.getElementById("signin-box").style.display = "none";
            document.getElementById("signup-box").style.display = "none";
            document.getElementById("home-box").style.display = "none";
            document.getElementById("payment-box").style.display = "block";
        }

        function validateLogin() {
            const username = document.getElementById("signin-username").value;
            const password = document.getElementById("signin-password").value;
            const errorMessage = document.getElementById("signin-error");

            const storedUsername = localStorage.getItem("username");
            const storedPassword = localStorage.getItem("password");

            if (username === storedUsername && password === storedPassword) {
                errorMessage.textContent = "";
                alert("Login Successful!");
                showHome();
            } else {
                errorMessage.textContent = "Invalid Username or Password!";
            }
        }

        function register() {
            const newUsername = document.getElementById("signup-username").value;
            const newPassword = document.getElementById("signup-password").value;

            localStorage.setItem("username", newUsername);
            localStorage.setItem("password", newPassword);

            alert("Registration Successful! You can now sign in.");
            showSignin();
        }

        function confirmPayment() {
            alert("Your payment will be verified shortly.");
            localStorage.setItem("hasPaid", "true");
            showHome();
        }

        function logout() {
            alert("Logged out successfully!");
            showSignin();
        }
    </script>
</body>
</html>
