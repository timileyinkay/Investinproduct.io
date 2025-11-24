import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Power Bank Investment Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .profit-positive {
        color: #00ff00;
        font-weight: bold;
    }
    .profit-negative {
        color: #ff0000;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class PowerBankInvestmentDashboard:
    def __init__(self):
        self.df = self.generate_sample_data()
    
    def generate_sample_data(self):
        """Generate sample power bank investment data"""
        np.random.seed(42)
        
        dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
        brands = ['Anker', 'Xiaomi', 'Samsung', 'RAVPower', 'Baseus', 'AUKEY']
        locations = ['Mall Kiosk', 'Airport', 'University', 'Coffee Shop', 'Co-working Space']
        
        data = []
        for date in dates:
            for brand in brands:
                for location in locations:
                    units = np.random.randint(1, 10)
                    cost_per_unit = np.random.uniform(20, 100)
                    revenue_per_unit = cost_per_unit * np.random.uniform(1.1, 2.0)
                    
                    data.append({
                        'date': date,
                        'brand': brand,
                        'location': location,
                        'units_invested': units,
                        'cost_per_unit': cost_per_unit,
                        'revenue_per_unit': revenue_per_unit,
                        'total_cost': units * cost_per_unit,
                        'total_revenue': units * revenue_per_unit
                    })
        
        df = pd.DataFrame(data)
        df['profit'] = df['total_revenue'] - df['total_cost']
        df['roi'] = (df['profit'] / df['total_cost']) * 100
        return df
    
    def display_header(self):
        """Display dashboard header"""
        st.markdown('<h1 class="main-header">🔋 Power Bank Investment Dashboard</h1>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.write("Track and analyze your power bank rental investments")
    
    def display_kpis(self):
        """Display Key Performance Indicators"""
        st.subheader("📊 Key Performance Indicators")
        
        total_investment = self.df['total_cost'].sum()
        total_revenue = self.df['total_revenue'].sum()
        total_profit = self.df['profit'].sum()
        avg_roi = self.df['roi'].mean()
        total_units = self.df['units_invested'].sum()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="Total Investment",
                value=f"${total_investment:,.0f}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="Total Revenue",
                value=f"${total_revenue:,.0f}",
                delta=f"${total_profit:,.0f}"
            )
        
        with col3:
            profit_class = "profit-positive" if total_profit >= 0 else "profit-negative"
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Profit</h3>
                <h2 class="{profit_class}">${total_profit:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.metric(
                label="Average ROI",
                value=f"{avg_roi:.1f}%",
                delta=None
            )
        
        with col5:
            st.metric(
                label="Total Units",
                value=f"{total_units:,.0f}",
                delta=None
            )
    
    def display_filters(self):
        """Display filters in sidebar"""
        st.sidebar.header("🔍 Filters")
        
        # Date range filter
        min_date = self.df['date'].min().date()
        max_date = self.df['date'].max().date()
        
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Brand filter
        brands = st.sidebar.multiselect(
            "Brands",
            options=self.df['brand'].unique(),
            default=self.df['brand'].unique()
        )
        
        # Location filter
        locations = st.sidebar.multiselect(
            "Locations",
            options=self.df['location'].unique(),
            default=self.df['location'].unique()
        )
        
        # Apply filters
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = self.df[
                (self.df['date'].dt.date >= start_date) & 
                (self.df['date'].dt.date <= end_date) &
                (self.df['brand'].isin(brands)) &
                (self.df['location'].isin(locations))
            ]
        else:
            filtered_df = self.df
        
        return filtered_df
    
    def display_profit_trend(self, filtered_df):
        """Display profit trend over time"""
        st.subheader("📈 Profit Trend Over Time")
        
        # Aggregate data by month
        monthly_data = filtered_df.groupby(pd.Grouper(key='date', freq='M')).agg({
            'total_cost': 'sum',
            'total_revenue': 'sum',
            'profit': 'sum',
            'units_invested': 'sum'
        }).reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=monthly_data['date'],
            y=monthly_data['profit'],
            mode='lines+markers',
            name='Profit',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=monthly_data['date'],
            y=monthly_data['total_revenue'],
            mode='lines',
            name='Revenue',
            line=dict(color='#2ca02c', width=2, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=monthly_data['date'],
            y=monthly_data['total_cost'],
            mode='lines',
            name='Cost',
            line=dict(color='#ff7f0e', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title='Monthly Profit, Revenue, and Cost Trends',
            xaxis_title='Date',
            yaxis_title='Amount ($)',
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_brand_performance(self, filtered_df):
        """Display brand performance comparison"""
        st.subheader("🏷️ Brand Performance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # ROI by brand
            brand_roi = filtered_df.groupby('brand').agg({
                'roi': 'mean',
                'profit': 'sum',
                'units_invested': 'sum'
            }).reset_index()
            
            fig_roi = px.bar(
                brand_roi,
                x='brand',
                y='roi',
                title='Average ROI by Brand',
                color='roi',
                color_continuous_scale='Viridis'
            )
            fig_roi.update_layout(height=400)
            st.plotly_chart(fig_roi, use_container_width=True)
        
        with col2:
            # Profit by brand
            fig_profit = px.pie(
                filtered_df.groupby('brand')['profit'].sum().reset_index(),
                values='profit',
                names='brand',
                title='Profit Distribution by Brand',
                hole=0.4
            )
            fig_profit.update_layout(height=400)
            st.plotly_chart(fig_profit, use_container_width=True)
    
    def display_location_analysis(self, filtered_df):
        """Display location performance analysis"""
        st.subheader("📍 Location Performance")
        
        location_performance = filtered_df.groupby('location').agg({
            'profit': 'sum',
            'roi': 'mean',
            'units_invested': 'sum'
        }).reset_index()
        
        fig = px.scatter(
            location_performance,
            x='units_invested',
            y='profit',
            size='roi',
            color='location',
            title='Location Performance: Units vs Profit (Size = ROI)',
            hover_data=['roi']
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    def display_investment_details(self, filtered_df):
        """Display detailed investment table"""
        st.subheader("📋 Investment Details")
        
        # Show aggregated data
        summary_df = filtered_df.groupby(['brand', 'location']).agg({
            'units_invested': 'sum',
            'total_cost': 'sum',
            'total_revenue': 'sum',
            'profit': 'sum',
            'roi': 'mean'
        }).reset_index()
        
        # Format numbers
        summary_df['total_cost'] = summary_df['total_cost'].round(2)
        summary_df['total_revenue'] = summary_df['total_revenue'].round(2)
        summary_df['profit'] = summary_df['profit'].round(2)
        summary_df['roi'] = summary_df['roi'].round(2)
        
        st.dataframe(
            summary_df,
            use_container_width=True,
            column_config={
                'units_invested': st.column_config.NumberColumn('Units'),
                'total_cost': st.column_config.NumberColumn('Cost', format='$%.2f'),
                'total_revenue': st.column_config.NumberColumn('Revenue', format='$%.2f'),
                'profit': st.column_config.NumberColumn('Profit', format='$%.2f'),
                'roi': st.column_config.NumberColumn('ROI', format='%.2f%%')
            }
        )
    
    def display_forecasting(self, filtered_df):
        """Display simple forecasting"""
        st.subheader("🔮 Revenue Forecasting")
        
        # Simple linear forecast based on last 3 months
        recent_data = filtered_df.groupby(pd.Grouper(key='date', freq='M'))['total_revenue'].sum().tail(3)
        
        if len(recent_data) >= 2:
            # Simple linear projection
            x = np.arange(len(recent_data))
            y = recent_data.values
            slope = (y[-1] - y[0]) / (x[-1] - x[0]) if (x[-1] - x[0]) != 0 else 0
            
            future_months = 6
            forecast_dates = pd.date_range(
                start=recent_data.index[-1] + pd.DateOffset(months=1),
                periods=future_months,
                freq='M'
            )
            
            forecast_values = [recent_data.iloc[-1] + slope * (i + 1) for i in range(future_months)]
            
            fig = go.Figure()
            
            # Historical data
            fig.add_trace(go.Scatter(
                x=recent_data.index,
                y=recent_data.values,
                mode='lines+markers',
                name='Historical Revenue',
                line=dict(color='#1f77b4', width=3)
            ))
            
            # Forecast data
            fig.add_trace(go.Scatter(
                x=forecast_dates,
                y=forecast_values,
                mode='lines+markers',
                name='Forecasted Revenue',
                line=dict(color='#ff7f0e', width=3, dash='dash')
            ))
            
            fig.update_layout(
                title='6-Month Revenue Forecast',
                xaxis_title='Date',
                yaxis_title='Revenue ($)',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Not enough data for forecasting. Need at least 2 months of data.")
    
    def run(self):
        """Run the dashboard"""
        self.display_header()
        
        # Get filtered data
        filtered_df = self.display_filters()
        
        # Display KPIs
        self.display_kpis()
        
        # Display charts in tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Trends", 
            "🏷️ Brands", 
            "📍 Locations", 
            "📋 Details", 
            "🔮 Forecast"
        ])
        
        with tab1:
            self.display_profit_trend(filtered_df)
        
        with tab2:
            self.display_brand_performance(filtered_df)
        
        with tab3:
            self.display_location_analysis(filtered_df)
        
        with tab4:
            self.display_investment_details(filtered_df)
        
        with tab5:
            self.display_forecasting(filtered_df)

# Run the dashboard
if __name__ == "__main__":
    dashboard = PowerBankInvestmentDashboard()
    dashboard.run()