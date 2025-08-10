import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from mysql_handler import MySQLHandler

# Page configuration
st.set_page_config(
    page_title="Log Analyzer Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .stMetric {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        border: none;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .stSelectbox > div > div {
        background-color: #f0f2f6;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database connection
@st.cache_resource
def init_database():
    """Initialize database connection"""
    try:
        db = MySQLHandler()
        if db.connect():
            return db
        else:
            st.error("Failed to connect to database. Please check your configuration.")
            return None
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

# Cache data functions
@st.cache_data(ttl=60)
def get_database_stats():
    """Get cached database statistics"""
    db = init_database()
    if db:
        return db.get_database_stats()
    return {}

@st.cache_data(ttl=60)
def get_top_ips(n=10):
    """Get cached top IPs data"""
    db = init_database()
    if db:
        return db.get_top_n_ips(n)
    return []

@st.cache_data(ttl=60)
def get_status_codes():
    """Get cached status code distribution"""
    db = init_database()
    if db:
        return db.get_status_code_distribution()
    return []

@st.cache_data(ttl=60)
def get_hourly_traffic():
    """Get cached hourly traffic data"""
    db = init_database()
    if db:
        return db.get_hourly_traffic()
    return []

@st.cache_data(ttl=60)
def get_daily_traffic():
    """Get cached daily traffic data"""
    db = init_database()
    if db:
        return db.get_daily_traffic()
    return []

@st.cache_data(ttl=60)
def get_resource_analysis(n=10):
    """Get cached resource analysis"""
    db = init_database()
    if db:
        return db.get_resource_analysis(n)
    return []

@st.cache_data(ttl=60)
def get_error_analysis():
    """Get cached error analysis"""
    db = init_database()
    if db:
        return db.get_error_analysis()
    return []

@st.cache_data(ttl=60)
def get_heatmap_data():
    """Get cached heatmap data"""
    db = init_database()
    if db:
        return db.get_traffic_heatmap_data()
    return []

def create_animated_bar_chart(data, x_col, y_col, title, color_sequence=None):
    """Create animated bar chart"""
    if not data:
        return go.Figure().add_annotation(text="No data available", 
                                        xref="paper", yref="paper",
                                        x=0.5, y=0.5, showarrow=False)
    
    df = pd.DataFrame(data)
    fig = px.bar(df, x=x_col, y=y_col, title=title,
                 color_discrete_sequence=color_sequence or px.colors.qualitative.Set3)
    
    fig.update_layout(
        title_font_size=20,
        title_x=0.5,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        showlegend=False
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>',
        marker_line_width=2,
        marker_line_color='white'
    )
    
    return fig

def create_pie_chart(data, names_col, values_col, title):
    """Create animated pie chart"""
    if not data:
        return go.Figure().add_annotation(text="No data available", 
                                        xref="paper", yref="paper",
                                        x=0.5, y=0.5, showarrow=False)
    
    df = pd.DataFrame(data)
    fig = px.pie(df, names=names_col, values=values_col, title=title,
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    
    fig.update_layout(
        title_font_size=20,
        title_x=0.5,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
        textposition='inside',
        textinfo='percent+label'
    )
    
    return fig

def create_line_chart(data, x_col, y_col, title):
    """Create animated line chart"""
    if not data:
        return go.Figure().add_annotation(text="No data available", 
                                        xref="paper", yref="paper",
                                        x=0.5, y=0.5, showarrow=False)
    
    df = pd.DataFrame(data)
    fig = px.line(df, x=x_col, y=y_col, title=title,
                  line_shape='spline')
    
    fig.update_layout(
        title_font_size=20,
        title_x=0.5,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title=y_col.replace('_', ' ').title()
    )
    
    fig.update_traces(
        line=dict(width=3, color='#667eea'),
        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
    )
    
    return fig

def create_heatmap(data):
    """Create traffic heatmap"""
    if not data:
        return go.Figure().add_annotation(text="No data available", 
                                        xref="paper", yref="paper",
                                        x=0.5, y=0.5, showarrow=False)
    
    # Create pivot table for heatmap
    df = pd.DataFrame(data)
    
    # Map day numbers to day names
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    df['day_name'] = df['day_of_week'].apply(lambda x: day_names[x-1] if 1 <= x <= 7 else 'Unknown')
    
    pivot_table = df.pivot_table(values='request_count', 
                                index='day_name', 
                                columns='hour', 
                                fill_value=0)
    
    fig = px.imshow(pivot_table, 
                    title="Traffic Heatmap (Day vs Hour)",
                    color_continuous_scale='Viridis',
                    aspect='auto')
    
    fig.update_layout(
        title_font_size=20,
        title_x=0.5,
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week"
    )
    
    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Log Analyzer Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🎛️ Dashboard Controls")
    
    # Filters
    st.sidebar.subheader("📊 Display Options")
    top_n = st.sidebar.slider("Top N Results", min_value=5, max_value=50, value=10, step=5)
    
    # Get database stats
    stats = get_database_stats()
    
    if not stats or stats.get('total_records', 0) == 0:
        st.error("⚠️ No data available in the database. Please process some log files first.")
        st.info("Run: `python main.py process_logs your_log_file.log`")
        return
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📈 Total Requests",
            value=f"{stats.get('total_records', 0):,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="🌐 Unique IPs",
            value=f"{stats.get('unique_ips', 0):,}",
            delta=None
        )
    
    with col3:
        if stats.get('earliest_log'):
            earliest = stats['earliest_log']
            if isinstance(earliest, str):
                earliest = datetime.fromisoformat(earliest.replace('Z', '+00:00'))
            days_span = (datetime.now() - earliest).days
            st.metric(
                label="📅 Days Analyzed",
                value=f"{days_span}",
                delta=None
            )
        else:
            st.metric(label="📅 Days Analyzed", value="N/A")
    
    with col4:
        # Calculate average requests per day
        if stats.get('total_records', 0) > 0 and stats.get('earliest_log'):
            earliest = stats['earliest_log']
            if isinstance(earliest, str):
                earliest = datetime.fromisoformat(earliest.replace('Z', '+00:00'))
            days_span = max((datetime.now() - earliest).days, 1)
            avg_per_day = stats['total_records'] / days_span
            st.metric(
                label="📊 Avg Requests/Day",
                value=f"{avg_per_day:.0f}",
                delta=None
            )
        else:
            st.metric(label="📊 Avg Requests/Day", value="N/A")
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Top IPs", "📊 Status Codes", "⏰ Traffic Patterns", "📁 Resources", "🚨 Errors"])
    
    with tab1:
        st.subheader(f"🎯 Top {top_n} IP Addresses")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            top_ips_data = get_top_ips(top_n)
            fig = create_animated_bar_chart(
                top_ips_data, 
                'ip_address', 
                'request_count',
                f"Top {top_n} IP Addresses by Request Count",
                px.colors.qualitative.Set1
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if top_ips_data:
                st.subheader("📋 Top IPs Table")
                df = pd.DataFrame(top_ips_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No IP data available")
    
    with tab2:
        st.subheader("📊 HTTP Status Code Distribution")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            status_data = get_status_codes()
            fig = create_pie_chart(
                status_data,
                'status_code',
                'count',
                "Status Code Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = create_animated_bar_chart(
                status_data,
                'status_code',
                'count',
                "Status Codes by Count",
                px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Status codes table
        if status_data:
            st.subheader("📋 Status Code Details")
            df = pd.DataFrame(status_data)
            df['status_code'] = df['status_code'].astype(str)
            st.dataframe(df, use_container_width=True)
    
    with tab3:
        st.subheader("⏰ Traffic Patterns")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            hourly_data = get_hourly_traffic()
            if hourly_data:
                # Format hour data
                formatted_hourly = []
                for item in hourly_data:
                    formatted_hourly.append({
                        'hour': f"{item['hour']:02d}:00",
                        'request_count': item['request_count']
                    })
                
                fig = create_line_chart(
                    formatted_hourly,
                    'hour',
                    'request_count',
                    "Hourly Traffic Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            daily_data = get_daily_traffic()
            if daily_data:
                fig = create_line_chart(
                    daily_data,
                    'date',
                    'request_count',
                    "Daily Traffic Trend (Last 30 Days)"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Traffic heatmap
        st.subheader("🔥 Traffic Heatmap")
        heatmap_data = get_heatmap_data()
        fig = create_heatmap(heatmap_data)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader(f"📁 Top {top_n} Requested Resources")
        
        resource_data = get_resource_analysis(top_n)
        
        if resource_data:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = create_animated_bar_chart(
                    resource_data,
                    'resource',
                    'request_count',
                    f"Top {top_n} Resources by Request Count",
                    px.colors.qualitative.Dark2
                )
                # Rotate x-axis labels for better readability
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📋 Resource Details")
                df = pd.DataFrame(resource_data)
                # Truncate long resource names for display
                df['resource_short'] = df['resource'].apply(lambda x: x[:30] + '...' if len(x) > 30 else x)
                df['avg_size'] = df['avg_size'].apply(lambda x: f"{x:.2f}" if x else "0")
                display_df = df[['resource_short', 'request_count', 'avg_size']].rename(columns={
                    'resource_short': 'Resource',
                    'request_count': 'Requests',
                    'avg_size': 'Avg Size (bytes)'
                })
                st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No resource data available")
    
    with tab5:
        st.subheader("🚨 Error Analysis")
        
        error_data = get_error_analysis()
        
        if error_data:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                fig = create_animated_bar_chart(
                    error_data,
                    'status_code',
                    'error_count',
                    "Error Distribution (4xx & 5xx)",
                    px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = create_pie_chart(
                    error_data,
                    'status_code',
                    'error_count',
                    "Error Types Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Error details table
            st.subheader("📋 Error Details")
            df = pd.DataFrame(error_data)
            df['sample_resources'] = df['sample_resources'].apply(
                lambda x: x[:100] + '...' if x and len(x) > 100 else x
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.success("🎉 No errors found in the logs!")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>📊 Log Analyzer Dashboard | Built with Streamlit & Plotly</p>
            <p>Last updated: {}</p>
        </div>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

