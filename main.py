import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Food Commodities Investment Dashboard",
    page_icon="🌾",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .investment-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2E8B57;
        margin: 0.5rem 0;
    }
    .price-up {
        color: #28a745;
        font-weight: bold;
    }
    .price-down {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🌾 Food Commodities Investment Platform</h1>', unsafe_allow_html=True)

# Sample data for food commodities
def generate_food_data():
    commodities = [
        {
            'name': 'Rice',
            'category': 'Grains',
            'current_price': 15.75,
            'change_24h': 0.25,
            'unit': 'per 50kg',
            'description': 'Premium long-grain rice',
            'market_cap': '2.1B',
            'volume': '145K'
        },
        {
            'name': 'Beans',
            'category': 'Legumes',
            'current_price': 8.45,
            'change_24h': -0.15,
            'unit': 'per 25kg',
            'description': 'Black beans organic',
            'market_cap': '850M',
            'volume': '89K'
        },
        {
            'name': 'Chicken',
            'category': 'Poultry',
            'current_price': 3.25,
            'change_24h': 0.08,
            'unit': 'per kg',
            'description': 'Fresh poultry chicken',
            'market_cap': '1.8B',
            'volume': '210K'
        },
        {
            'name': 'Wheat',
            'category': 'Grains',
            'current_price': 12.30,
            'change_24h': 0.45,
            'unit': 'per 50kg',
            'description': 'Hard red winter wheat',
            'market_cap': '3.2B',
            'volume': '320K'
        },
        {
            'name': 'Corn',
            'category': 'Grains',
            'current_price': 6.80,
            'change_24h': -0.20,
            'unit': 'per 50kg',
            'description': 'Yellow feed corn',
            'market_cap': '2.8B',
            'volume': '280K'
        },
        {
            'name': 'Soybeans',
            'category': 'Legumes',
            'current_price': 14.20,
            'change_24h': 0.35,
            'unit': 'per 50kg',
            'description': 'Non-GMO soybeans',
            'market_cap': '1.5B',
            'volume': '165K'
        }
    ]
    return pd.DataFrame(commodities)

# Generate price history
def generate_price_history(commodity_name, base_price, days=30):
    dates = [datetime.now() - timedelta(days=x) for x in range(days, 0, -1)]
    prices = []
    current_price = base_price
    
    for i in range(days):
        # Random walk for price simulation
        change = random.uniform(-0.1, 0.1)
        current_price = max(0.1, current_price * (1 + change))
        prices.append(round(current_price, 2))
    
    return pd.DataFrame({'date': dates, 'price': prices, 'commodity': commodity_name})

# Initialize session state for portfolio
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'investment_history' not in st.session_state:
    st.session_state.investment_history = []

# Generate data
df = generate_food_data()

# Sidebar for filters
st.sidebar.header("🔍 Filters")
category_filter = st.sidebar.multiselect(
    "Select Categories:",
    options=df['category'].unique(),
    default=df['category'].unique()
)

# Main dashboard layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Market Overview")
    
    # Display commodities in a grid
    for _, commodity in df.iterrows():
        if commodity['category'] in category_filter:
            with st.container():
                col_a, col_b, col_c = st.columns([2, 1, 1])
                
                with col_a:
                    st.write(f"**{commodity['name']}**")
                    st.write(f"{commodity['description']}")
                    st.write(f"Category: {commodity['category']}")
                
                with col_b:
                    change_color = "price-up" if commodity['change_24h'] >= 0 else "price-down"
                    change_symbol = "▲" if commodity['change_24h'] >= 0 else "▼"
                    st.markdown(f"**${commodity['current_price']}**")
                    st.markdown(f'<span class="{change_color}">{change_symbol} ${abs(commodity["change_24h"])}</span>', unsafe_allow_html=True)
                    st.write(f"Unit: {commodity['unit']}")
                
                with col_c:
                    # Investment interface
                    quantity = st.number_input(
                        f"Quantity ({commodity['unit']})",
                        min_value=0.0,
                        step=1.0,
                        key=f"qty_{commodity['name']}"
                    )
                    
                    if st.button(f"Invest in {commodity['name']}", key=f"btn_{commodity['name']}"):
                        if quantity > 0:
                            investment_amount = quantity * commodity['current_price']
                            # Add to portfolio
                            if commodity['name'] in st.session_state.portfolio:
                                st.session_state.portfolio[commodity['name']]['quantity'] += quantity
                                st.session_state.portfolio[commodity['name']]['total_invested'] += investment_amount
                            else:
                                st.session_state.portfolio[commodity['name']] = {
                                    'quantity': quantity,
                                    'avg_price': commodity['current_price'],
                                    'total_invested': investment_amount,
                                    'category': commodity['category']
                                }
                            
                            # Add to history
                            st.session_state.investment_history.append({
                                'timestamp': datetime.now(),
                                'commodity': commodity['name'],
                                'quantity': quantity,
                                'price': commodity['current_price'],
                                'amount': investment_amount
                            })
                            
                            st.success(f"Successfully invested ${investment_amount:,.2f} in {commodity['name']}!")
                        else:
                            st.error("Please enter a valid quantity")
                
                st.markdown("---")

with col2:
    st.subheader("💰 Your Portfolio")
    
    if not st.session_state.portfolio:
        st.info("Your portfolio is empty. Start investing!")
    else:
        total_value = 0
        for commodity, data in st.session_state.portfolio.items():
            current_price = df[df['name'] == commodity]['current_price'].iloc[0]
            current_value = data['quantity'] * current_price
            total_value += current_value
            
            st.write(f"**{commodity}**")
            st.write(f"Quantity: {data['quantity']} {df[df['name'] == commodity]['unit'].iloc[0]}")
            st.write(f"Invested: ${data['total_invested']:,.2f}")
            st.write(f"Current Value: ${current_value:,.2f}")
            
            pnl = current_value - data['total_invested']
            pnl_color = "price-up" if pnl >= 0 else "price-down"
            st.markdown(f'P&L: <span class="{pnl_color}">${pnl:,.2f}</span>', unsafe_allow_html=True)
            st.markdown("---")
        
        st.metric("Total Portfolio Value", f"${total_value:,.2f}")

# Price charts section
st.subheader("📈 Price Trends")
selected_commodity = st.selectbox("Select commodity to view price history:", df['name'].unique())

# Generate and display price chart
price_history = generate_price_history(selected_commodity, df[df['name'] == selected_commodity]['current_price'].iloc[0])

fig = px.line(price_history, x='date', y='price', title=f'{selected_commodity} Price History (30 days)')
fig.update_layout(xaxis_title='Date', yaxis_title='Price ($)')
st.plotly_chart(fig, use_container_width=True)

# Investment history
st.subheader("📋 Investment History")
if st.session_state.investment_history:
    history_df = pd.DataFrame(st.session_state.investment_history)
    history_df = history_df.sort_values('timestamp', ascending=False)
    st.dataframe(history_df.style.format({
        'price': '${:.2f}',
        'amount': '${:.2f}'
    }))
else:
    st.info("No investment history yet.")

# Market statistics
st.subheader("📊 Market Statistics")
col3, col4, col5 = st.columns(3)

with col3:
    total_market_cap = sum([float(x.replace('B', '')) * 1000000000 for x in df['market_cap'] if 'B' in x])
    st.metric("Total Market Cap", f"${total_market_cap/1000000000:.1f}B")

with col4:
    avg_daily_change = df['change_24h'].mean()
    st.metric("Average Daily Change", f"{avg_daily_change:.2f}%")

with col5:
    top_performer = df.loc[df['change_24h'].idxmax()]
    st.metric("Top Performer", top_performer['name'])

# Real-time price updates (simulated)
if st.button("🔄 Refresh Prices"):
    with st.spinner("Updating prices..."):
        # Simulate API call delay
        time.sleep(1)
        # Update prices with small random changes
        for i in range(len(df)):
            change = random.uniform(-0.05, 0.05)
            df.at[i, 'current_price'] = max(0.1, df.at[i, 'current_price'] * (1 + change))
            df.at[i, 'change_24h'] = change
        st.rerun()

# Footer
st.markdown("---")
st.markdown("*Disclaimer: This is a demo application. Prices are simulated and not real market data.*")