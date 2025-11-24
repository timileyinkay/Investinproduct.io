import http.server
import socketserver
import webbrowser
import threading
import json
from datetime import datetime, timedelta
import random

class PowerBankDashboard:
    def __init__(self):
        self.html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Power Bank Investment Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }

                body {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }

                .container {
                    max-width: 1400px;
                    margin: 0 auto;
                }

                .header {
                    text-align: center;
                    margin-bottom: 30px;
                    color: white;
                }

                .header h1 {
                    font-size: 2.5rem;
                    margin-bottom: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 15px;
                }

                .header p {
                    font-size: 1.1rem;
                    opacity: 0.9;
                }

                .dashboard {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }

                .card {
                    background: white;
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                    transition: transform 0.3s ease;
                }

                .card:hover {
                    transform: translateY(-5px);
                }

                .card h3 {
                    color: #333;
                    margin-bottom: 15px;
                    font-size: 1.2rem;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }

                .metric {
                    font-size: 2rem;
                    font-weight: bold;
                    color: #4a5568;
                }

                .metric-small {
                    font-size: 1.5rem;
                }

                .profit-positive {
                    color: #10b981;
                }

                .profit-negative {
                    color: #ef4444;
                }

                .charts-container {
                    display: grid;
                    grid-template-columns: 2fr 1fr;
                    gap: 20px;
                    margin-bottom: 30px;
                }

                .chart-card {
                    background: white;
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                }

                .chart-card h3 {
                    color: #333;
                    margin-bottom: 20px;
                    font-size: 1.3rem;
                }

                .chart-container {
                    height: 300px;
                    position: relative;
                }

                .filters {
                    background: white;
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                }

                .filter-row {
                    display: flex;
                    gap: 20px;
                    flex-wrap: wrap;
                }

                .filter-group {
                    flex: 1;
                    min-width: 200px;
                }

                .filter-group label {
                    display: block;
                    margin-bottom: 8px;
                    font-weight: 600;
                    color: #4a5568;
                }

                .filter-group select, .filter-group input {
                    width: 100%;
                    padding: 10px;
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    font-size: 1rem;
                }

                .table-container {
                    background: white;
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                    overflow-x: auto;
                }

                table {
                    width: 100%;
                    border-collapse: collapse;
                }

                th, td {
                    padding: 12px 15px;
                    text-align: left;
                    border-bottom: 1px solid #e2e8f0;
                }

                th {
                    background-color: #f7fafc;
                    font-weight: 600;
                    color: #4a5568;
                }

                tr:hover {
                    background-color: #f7fafc;
                }

                .status-active {
                    color: #10b981;
                    font-weight: 600;
                }

                .status-inactive {
                    color: #ef4444;
                    font-weight: 600;
                }

                .icon {
                    font-size: 1.5rem;
                    color: #667eea;
                }

                @media (max-width: 768px) {
                    .charts-container {
                        grid-template-columns: 1fr;
                    }
                    
                    .header h1 {
                        font-size: 2rem;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1><i class="fas fa-charging-station"></i> Power Bank Investment Dashboard</h1>
                    <p>Track and analyze your power bank rental investments</p>
                </div>

                <div class="filters">
                    <div class="filter-row">
                        <div class="filter-group">
                            <label for="timeRange">Time Range</label>
                            <select id="timeRange">
                                <option value="7">Last 7 Days</option>
                                <option value="30" selected>Last 30 Days</option>
                                <option value="90">Last 90 Days</option>
                                <option value="365">Last Year</option>
                            </select>
                        </div>
                        <div class="filter-group">
                            <label for="location">Location</label>
                            <select id="location">
                                <option value="all">All Locations</option>
                                <option value="mall">Shopping Mall</option>
                                <option value="airport">Airport</option>
                                <option value="university">University</option>
                                <option value="cafe">Coffee Shop</option>
                            </select>
                        </div>
                        <div class="filter-group">
                            <label for="brand">Brand</label>
                            <select id="brand">
                                <option value="all">All Brands</option>
                                <option value="anker">Anker</option>
                                <option value="xiaomi">Xiaomi</option>
                                <option value="samsung">Samsung</option>
                                <option value="ravpower">RAVPower</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div class="dashboard">
                    <div class="card">
                        <h3><i class="fas fa-dollar-sign"></i> Total Investment</h3>
                        <div class="metric" id="totalInvestment">$24,580</div>
                        <p>Across all locations</p>
                    </div>
                    <div class="card">
                        <h3><i class="fas fa-chart-line"></i> Total Revenue</h3>
                        <div class="metric" id="totalRevenue">$38,420</div>
                        <p>Last 30 days</p>
                    </div>
                    <div class="card">
                        <h3><i class="fas fa-money-bill-wave"></i> Net Profit</h3>
                        <div class="metric profit-positive" id="netProfit">$13,840</div>
                        <p>ROI: 56.3%</p>
                    </div>
                    <div class="card">
                        <h3><i class="fas fa-battery-full"></i> Active Units</h3>
                        <div class="metric" id="activeUnits">142</div>
                        <p>86% utilization rate</p>
                    </div>
                </div>

                <div class="charts-container">
                    <div class="chart-card">
                        <h3><i class="fas fa-chart-bar"></i> Revenue & Profit Trend</h3>
                        <div class="chart-container">
                            <canvas id="revenueChart"></canvas>
                        </div>
                    </div>
                    <div class="chart-card">
                        <h3><i class="fas fa-chart-pie"></i> Revenue by Location</h3>
                        <div class="chart-container">
                            <canvas id="locationChart"></canvas>
                        </div>
                    </div>
                </div>

                <div class="charts-container">
                    <div class="chart-card">
                        <h3><i class="fas fa-chart-line"></i> ROI by Brand</h3>
                        <div class="chart-container">
                            <canvas id="roiChart"></canvas>
                        </div>
                    </div>
                    <div class="chart-card">
                        <h3><i class="fas fa-battery-half"></i> Utilization Rate</h3>
                        <div class="chart-container">
                            <canvas id="utilizationChart"></canvas>
                        </div>
                    </div>
                </div>

                <div class="table-container">
                    <h3><i class="fas fa-table"></i> Investment Details</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Location</th>
                                <th>Brand</th>
                                <th>Units</th>
                                <th>Investment</th>
                                <th>Revenue</th>
                                <th>Profit</th>
                                <th>ROI</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="investmentTable">
                            <!-- Table data will be populated by JavaScript -->
                        </tbody>
                    </table>
                </div>
            </div>

            <script>
                // Sample data for charts
                const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'];
                const revenueData = [3200, 4100, 3800, 5200, 6100, 5800, 7200, 6900];
                const profitData = [1200, 1800, 1500, 2200, 2800, 2400, 3200, 2900];
                const locationData = [35, 25, 20, 15, 5];
                const locationLabels = ['Mall', 'Airport', 'University', 'Coffee Shop', 'Others'];
                const roiData = [65, 52, 48, 60, 45, 55];
                const roiLabels = ['Anker', 'Xiaomi', 'Samsung', 'RAVPower', 'Baseus', 'AUKEY'];
                const utilizationData = [85, 92, 78, 88, 82, 90];

                // Initialize charts
                window.onload = function() {
                    // Revenue & Profit Trend Chart
                    const revenueCtx = document.getElementById('revenueChart').getContext('2d');
                    new Chart(revenueCtx, {
                        type: 'line',
                        data: {
                            labels: months,
                            datasets: [
                                {
                                    label: 'Revenue',
                                    data: revenueData,
                                    borderColor: '#4f46e5',
                                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                                    tension: 0.3,
                                    fill: true
                                },
                                {
                                    label: 'Profit',
                                    data: profitData,
                                    borderColor: '#10b981',
                                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                                    tension: 0.3,
                                    fill: true
                                }
                            ]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    position: 'top',
                                }
                            }
                        }
                    });

                    // Location Revenue Chart
                    const locationCtx = document.getElementById('locationChart').getContext('2d');
                    new Chart(locationCtx, {
                        type: 'doughnut',
                        data: {
                            labels: locationLabels,
                            datasets: [{
                                data: locationData,
                                backgroundColor: [
                                    '#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'
                                ]
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    position: 'right',
                                }
                            }
                        }
                    });

                    // ROI by Brand Chart
                    const roiCtx = document.getElementById('roiChart').getContext('2d');
                    new Chart(roiCtx, {
                        type: 'bar',
                        data: {
                            labels: roiLabels,
                            datasets: [{
                                label: 'ROI %',
                                data: roiData,
                                backgroundColor: '#8b5cf6'
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: false
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    title: {
                                        display: true,
                                        text: 'ROI (%)'
                                    }
                                }
                            }
                        }
                    });

                    // Utilization Rate Chart
                    const utilizationCtx = document.getElementById('utilizationChart').getContext('2d');
                    new Chart(utilizationCtx, {
                        type: 'bar',
                        data: {
                            labels: roiLabels,
                            datasets: [{
                                label: 'Utilization Rate %',
                                data: utilizationData,
                                backgroundColor: '#f59e0b'
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: false
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    max: 100,
                                    title: {
                                        display: true,
                                        text: 'Utilization (%)'
                                    }
                                }
                            }
                        }
                    });

                    // Populate investment table
                    const tableData = [
                        { location: 'Central Mall', brand: 'Anker', units: 25, investment: 4250, revenue: 7012, profit: 2762, roi: 65, status: 'Active' },
                        { location: 'International Airport', brand: 'Xiaomi', units: 30, investment: 3600, revenue: 5472, profit: 1872, roi: 52, status: 'Active' },
                        { location: 'City University', brand: 'Samsung', units: 20, investment: 3400, revenue: 5032, profit: 1632, roi: 48, status: 'Active' },
                        { location: 'StarBucks Coffee', brand: 'RAVPower', units: 15, investment: 2400, revenue: 3840, profit: 1440, roi: 60, status: 'Active' },
                        { location: 'Tech Hub', brand: 'Baseus', units: 18, investment: 2700, revenue: 3915, profit: 1215, roi: 45, status: 'Active' },
                        { location: 'Metro Station', brand: 'AUKEY', units: 22, investment: 3300, revenue: 5115, profit: 1815, roi: 55, status: 'Maintenance' },
                        { location: 'City Library', brand: 'Anker', units: 12, investment: 2040, revenue: 3366, profit: 1326, roi: 65, status: 'Active' }
                    ];

                    const tableBody = document.getElementById('investmentTable');
                    tableData.forEach(item => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${item.location}</td>
                            <td>${item.brand}</td>
                            <td>${item.units}</td>
                            <td>$${item.investment.toLocaleString()}</td>
                            <td>$${item.revenue.toLocaleString()}</td>
                            <td>$${item.profit.toLocaleString()}</td>
                            <td>${item.roi}%</td>
                            <td class="${item.status === 'Active' ? 'status-active' : 'status-inactive'}">${item.status}</td>
                        `;
                        tableBody.appendChild(row);
                    });
                };

                // Filter functionality
                document.getElementById('timeRange').addEventListener('change', updateDashboard);
                document.getElementById('location').addEventListener('change', updateDashboard);
                document.getElementById('brand').addEventListener('change', updateDashboard);

                function updateDashboard() {
                    // In a real application, this would fetch new data from the server
                    // For this demo, we'll just show a loading message
                    const timeRange = document.getElementById('timeRange').value;
                    const location = document.getElementById('location').value;
                    const brand = document.getElementById('brand').value;
                    
                    console.log(`Filters updated: TimeRange=${timeRange}, Location=${location}, Brand=${brand}`);
                    // Here you would typically make an AJAX request to update the dashboard data
                }
            </script>
        </body>
        </html>
        """

    def generate_sample_data(self):
        """Generate sample data for the dashboard"""
        data = {
            "total_investment": 24580,
            "total_revenue": 38420,
            "net_profit": 13840,
            "active_units": 142,
            "roi": 56.3,
            "utilization_rate": 86
        }
        return data

    def start_server(self, port=8000):
        """Start a simple HTTP server to serve the dashboard"""
        handler = http.server.SimpleHTTPRequestHandler
        
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"Power Bank Investment Dashboard running at http://localhost:{port}")
            # Write the HTML content to a file
            with open("index.html", "w") as f:
                f.write(self.html_content)
            
            # Open the dashboard in the default browser
            webbrowser.open(f"http://localhost:{port}")
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nShutting down server...")

if __name__ == "__main__":
    dashboard = PowerBankDashboard()
    dashboard.start_server()