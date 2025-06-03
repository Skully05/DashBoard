"""
Prompt Review Dashboard - Simple Dashboard showing prompt reviews with user information
Run this file with: streamlit run simple_dashboard.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration - MUST be first
st.set_page_config(
    page_title="PostgreSQL Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Try to import database manager
try:
    from database import db_manager
    DATABASE_AVAILABLE = db_manager is not None and (hasattr(db_manager, 'is_configured') and db_manager.is_configured)
except Exception as e:
    logger.error(f"Database import failed: {e}")
    db_manager = None
    DATABASE_AVAILABLE = False

def show_configuration_help():
    """Show database configuration help."""
    st.markdown('<div class="main-header">🔧 Database Configuration Required</div>', unsafe_allow_html=True)
    
    st.warning("⚠️ Database configuration is missing or incomplete!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Configuration Status")
        if db_manager:
            config_status = db_manager.get_configuration_status()
            if config_status['missing_fields']:
                st.error(f"❌ Missing: {', '.join(config_status['missing_fields'])}")
            
            st.markdown("### ✅ Available Configuration")
            for key, available in config_status['available_config'].items():
                status = "✅" if available else "❌"
                st.write(f"{status} {key.upper()}: {'Configured' if available else 'Missing'}")
            
            password_status = "✅" if config_status['password_configured'] else "❌"
            st.write(f"{password_status} PASSWORD: {'Configured' if config_status['password_configured'] else 'Missing'}")
        else:
            st.error("❌ Database manager could not be initialized")
    
    with col2:
        st.markdown("### 🔧 How to Configure")
        
        tab1, tab2 = st.tabs(["Streamlit Cloud", "Local Development"])
        
        with tab1:
            st.markdown("""
            **For Streamlit Cloud deployment:**
            
            1. Go to your app dashboard
            2. Click **"⚙️ Settings"** (or "Manage app")
            3. Click **"Secrets"** in the sidebar
            4. Add your database configuration:
            
            ```toml
            DB_HOST = "your_database_host"
            DB_PORT = "5432"
            DB_NAME = "your_database_name"
            DB_USER = "your_username"
            DB_PASSWORD = "your_password"
            DB_SSL_MODE = "prefer"
            ```
            
            5. Click **"Save"**
            6. **Reboot** the app
            """)
            
            st.info("💡 **Tip**: Make sure your database allows connections from Streamlit Cloud's IP ranges.")
        
        with tab2:
            st.markdown("""
            **For local development:**
            
            1. Create a `.env` file in your project directory
            2. Add your database configuration:
            
            ```env
            DB_HOST=your_database_host
            DB_PORT=5432
            DB_NAME=your_database_name
            DB_USER=your_username
            DB_PASSWORD=your_password
            DB_SSL_MODE=prefer
            ```
            
            3. Restart the application
            """)
            
            st.info("💡 **Tip**: Use the `start_dashboard.bat` or `start_dashboard.sh` scripts for easier setup.")
    
    st.markdown("### 🔍 Testing Connection")
    if st.button("🔄 Test Database Connection"):
        if db_manager and db_manager.is_configured:
            if db_manager.test_connection():
                st.success("✅ Database connection successful!")
                st.rerun()
            else:
                st.error("❌ Database connection failed. Check your configuration and network connectivity.")
        else:
            st.error("❌ Database not configured. Please add your database secrets first.")
    
    st.markdown("---")
    st.markdown("### 📚 Need Help?")
    st.markdown("""
    - **Documentation**: Check the `DEPLOYMENT.md` file
    - **Troubleshooting**: See `DEPENDENCY_TROUBLESHOOTING.md`
    - **Local Setup**: Use the provided startup scripts
    """)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.section-header {
    font-size: 1.5rem;
    color: #2c3e50;
    margin: 1rem 0;
    font-weight: bold;
}
.metric-container {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}
.circular-metric {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    margin: 1rem auto;
    width: 100%;
}
.circle {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    margin-bottom: 0.5rem;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    margin: 0 auto 0.5rem auto;
}
.circle-1 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.circle-2 { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.circle-3 { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.circle-4 { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
.circle-5 { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
.circle-number {
    font-size: 1.5rem;
    font-weight: bold;
    line-height: 1;
}
.circle-label {
    font-size: 0.7rem;
    margin-top: 0.2rem;
    line-height: 1;
}
.metric-title {
    font-size: 0.8rem;
    color: #2c3e50;
    font-weight: bold;
    margin-top: 0.5rem;
    text-align: center;
}
.metrics-container {
    display: flex;
    justify-content: space-around;
    align-items: center;
    flex-wrap: wrap;
    margin: 2rem 0;
    padding: 1rem;
    background-color: #f8f9fa;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

def get_prompt_reviews():
    """Get prompt reviews with user information."""
    if not DATABASE_AVAILABLE:
        return pd.DataFrame()
    
    query = """
    SELECT 
        u.name AS user_name,
        u.email,
        pr.prompt,
        pr.enhanced_prompt,
        pr.domain,
        pr.created_at,
        pr.processing_time_ms
    FROM 
        public.prompt_review pr
    JOIN 
        public.usertable u ON pr.user_id = u.user_id
    ORDER BY 
        pr.created_at DESC
    """
    try:
        df = db_manager.execute_query(query)
        logger.info(f"Prompt reviews query executed successfully, returned {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Prompt reviews query failed: {e}")
        return pd.DataFrame()

def get_total_enhanced_prompts():
    """Get total count of enhanced prompts."""
    if not DATABASE_AVAILABLE:
        return 0
        
    query = """
    SELECT COUNT(id) AS total_prompts FROM prompt_review
    """
    try:
        df = db_manager.execute_query(query)
        return df.iloc[0]['total_prompts'] if not df.empty else 0
    except Exception as e:
        logger.error(f"Total enhanced prompts query failed: {e}")
        return 0

def get_avg_daily_users():
    """Get average daily users."""
    if not DATABASE_AVAILABLE:
        return 0
        
    query = """
    WITH daily_users AS (
        SELECT DATE_TRUNC('day', created_at) AS day, 
               COUNT(DISTINCT user_id) AS daily_count 
        FROM usertable 
        GROUP BY DATE_TRUNC('day', created_at)
    )
    SELECT AVG(daily_count) AS average_daily_users 
    FROM daily_users
    """
    try:
        df = db_manager.execute_query(query)
        return round(df.iloc[0]['average_daily_users'], 1) if not df.empty else 0
    except Exception as e:
        logger.error(f"Average daily users query failed: {e}")
        return 0

def get_avg_weekly_users():
    """Get average weekly users."""
    if not DATABASE_AVAILABLE:
        return 0
        
    query = """
    WITH daily_users AS (
        SELECT DATE_TRUNC('day', created_at) AS day, 
               COUNT(DISTINCT user_id) as daily_count 
        FROM usertable 
        GROUP BY DATE_TRUNC('day', created_at)
    ),
    weekly_users AS (
        SELECT DATE_TRUNC('week', day) AS week, 
               AVG(daily_count) as weekly_avg 
        FROM daily_users 
        GROUP BY DATE_TRUNC('week', day)
    )
    SELECT AVG(weekly_avg) AS average_weekly_users 
    FROM weekly_users
    """
    try:
        df = db_manager.execute_query(query)
        return round(df.iloc[0]['average_weekly_users'], 1) if not df.empty else 0
    except Exception as e:
        logger.error(f"Average weekly users query failed: {e}")
        return 0

def get_most_used_ai():
    """Get most used AI type."""
    if not DATABASE_AVAILABLE:
        return "N/A"
        
    query = """
    SELECT llm_used, COUNT(*) as count 
    FROM prompt_review 
    GROUP BY llm_used 
    ORDER BY count DESC 
    LIMIT 1
    """
    try:
        df = db_manager.execute_query(query)
        if not df.empty:
            return f"{df.iloc[0]['llm_used']} ({df.iloc[0]['count']})"
        return "N/A"
    except Exception as e:
        logger.error(f"Most used AI query failed: {e}")
        return "N/A"

def get_total_users():
    """Get total count of users."""
    if not DATABASE_AVAILABLE:
        return 0
        
    query = """
    SELECT COUNT(DISTINCT user_id) AS total_users 
    FROM usertable 
    LIMIT 100
    """
    try:
        df = db_manager.execute_query(query)
        return df.iloc[0]['total_users'] if not df.empty else 0
    except Exception as e:
        logger.error(f"Total users query failed: {e}")
        return 0

def show_prompt_reviews_table():
    """Display prompt reviews table."""
    st.markdown('<div class="section-header">📝 Prompt Reviews (Latest First)</div>', unsafe_allow_html=True)
    
    if not DATABASE_AVAILABLE:
        st.warning("⚠️ Database not configured. Please configure your database connection to view data.")
        return
    
    reviews_data = get_prompt_reviews()
    if reviews_data.empty:
        st.warning("No prompt review data available")
        return
    
    # Format the data for display
    display_df = reviews_data.copy()
    
    # Handle datetime conversion properly
    try:
        display_df['created_at'] = pd.to_datetime(display_df['created_at'], utc=True).dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        logger.error(f"Date conversion failed: {e}")
        display_df['created_at'] = display_df['created_at'].astype(str)
    
    # Truncate long prompts for better display
    display_df['prompt_preview'] = display_df['prompt'].astype(str).apply(
        lambda x: x[:100] + "..." if len(str(x)) > 100 else str(x)
    )
    display_df['enhanced_preview'] = display_df['enhanced_prompt'].astype(str).apply(
        lambda x: x[:100] + "..." if len(str(x)) > 100 else str(x)
    )
    
    # Create final display dataframe
    display_df_final = display_df[['user_name', 'email', 'prompt_preview', 'enhanced_preview', 'domain', 'created_at', 'processing_time_ms']].copy()
    display_df_final.columns = ['User Name', 'Email', 'Original Prompt', 'Enhanced Prompt', 'Domain', 'Created At', 'Processing Time (ms)']
    
    # Show summary stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_reviews = len(reviews_data)
        st.metric("Total Reviews", f"{total_reviews:,}")
    
    with col2:
        unique_users = reviews_data['user_name'].nunique()
        st.metric("Unique Users", f"{unique_users}")
    
    with col3:
        avg_processing_time = reviews_data['processing_time_ms'].mean() if 'processing_time_ms' in reviews_data.columns else 0
        st.metric("Avg Processing Time", f"{avg_processing_time:.1f}ms")
    
    with col4:
        if len(reviews_data) > 0:
            latest_date = reviews_data['created_at'].max()
            st.metric("Latest Review", f"{pd.to_datetime(latest_date).strftime('%Y-%m-%d')}")
        else:
            st.metric("Latest Review", "N/A")
    
    st.markdown("---")
    
    # Show the main table
    st.dataframe(
        display_df_final,
        use_container_width=True,
        hide_index=True,
        column_config={
            'User Name': st.column_config.TextColumn(
                'User Name',
                help='Name of the user who submitted the prompt',
                width='medium'
            ),
            'Email': st.column_config.TextColumn(
                'Email',
                help='User email address',
                width='medium'
            ),
            'Original Prompt': st.column_config.TextColumn(
                'Original Prompt',
                help='Original prompt submitted by user (truncated)',
                width='large'
            ),
            'Enhanced Prompt': st.column_config.TextColumn(
                'Enhanced Prompt',
                help='AI-enhanced version of the prompt (truncated)',
                width='large'
            ),
            'Domain': st.column_config.TextColumn(
                'Domain',
                help='Domain of the prompt',
                width='medium'
            ),
            'Created At': st.column_config.TextColumn(
                'Created At',
                help='When the prompt was reviewed',
                width='medium'
            ),
            'Processing Time (ms)': st.column_config.NumberColumn(
                'Processing Time (ms)',
                help='Time taken to process the prompt',
                format='%.1f'
            )
        }
    )
    
    # Show expandable section with full prompt details for recent reviews
    with st.expander("🔍 View Full Details of Recent Reviews (Latest 10)"):
        recent_reviews = reviews_data.head(10)
        for idx, row in recent_reviews.iterrows():
            st.markdown(f"### Review #{idx+1}")
            st.markdown(f"**User:** {row['user_name']} ({row['email']})")
            st.markdown(f"**Domain:** {row['domain']}")
            st.markdown(f"**Created:** {row['created_at']}")
            st.markdown(f"**Processing Time:** {row['processing_time_ms']}ms")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Original Prompt:**")
                st.text_area(f"Original {idx+1}", value=str(row['prompt']), height=150, disabled=True, key=f"original_{idx}")
            
            with col2:
                st.markdown("**Enhanced Prompt:**")
                st.text_area(f"Enhanced {idx+1}", value=str(row['enhanced_prompt']), height=150, disabled=True, key=f"enhanced_{idx}")
            
            st.markdown("---")

def show_top_metrics():
    """Display top 5 metrics in circular format."""
    st.markdown('<div class="section-header">📊 Key Metrics Overview</div>', unsafe_allow_html=True)
    
    if not DATABASE_AVAILABLE:
        st.warning("⚠️ Database not configured. Showing demo data.")
        # Show demo metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown("""
            <div class="circular-metric">
                <div class="circle circle-1">
                    <div class="circle-number">0</div>
                    <div class="circle-label">Enhanced</div>
                </div>
                <div class="metric-title">Total Enhanced Prompts</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="circular-metric">
                <div class="circle circle-2">
                    <div class="circle-number">0</div>
                    <div class="circle-label">Daily Avg</div>
                </div>
                <div class="metric-title">Average Daily Users</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="circular-metric">
                <div class="circle circle-3">
                    <div class="circle-number">0</div>
                    <div class="circle-label">Weekly Avg</div>
                </div>
                <div class="metric-title">Average Weekly Users</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="circular-metric">
                <div class="circle circle-4">
                    <div class="circle-number" style="font-size: 1.0rem;">N/A</div>
                </div>
                <div class="metric-title">Most Used AI</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown("""
            <div class="circular-metric">
                <div class="circle circle-5">
                    <div class="circle-number">0</div>
                    <div class="circle-label">Total</div>
                </div>
                <div class="metric-title">Total Users</div>
            </div>
            """, unsafe_allow_html=True)
        return
    
    # Get all metrics
    total_prompts = get_total_enhanced_prompts()
    avg_daily = get_avg_daily_users()
    avg_weekly = get_avg_weekly_users()
    most_used_ai = get_most_used_ai()
    total_users = get_total_users()
    
    # Create 5 columns for the metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="circular-metric">
            <div class="circle circle-1">
                <div class="circle-number">{total_prompts}</div>
                <div class="circle-label">Enhanced</div>
            </div>
            <div class="metric-title">Total Enhanced Prompts</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="circular-metric">
            <div class="circle circle-2">
                <div class="circle-number">{avg_daily}</div>
                <div class="circle-label">Daily Avg</div>
            </div>
            <div class="metric-title">Average Daily Users</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="circular-metric">
            <div class="circle circle-3">
                <div class="circle-number">{avg_weekly}</div>
                <div class="circle-label">Weekly Avg</div>
            </div>
            <div class="metric-title">Average Weekly Users</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Handle AI type display - truncate if too long
        ai_display = str(most_used_ai)
        if len(ai_display) > 15:
            ai_parts = ai_display.split('(')
            if len(ai_parts) > 1:
                ai_name = ai_parts[0].strip()[:8] + "..."
                ai_count = f"({ai_parts[1]}"
                ai_display = f"{ai_name} {ai_count}"
            else:
                ai_display = ai_display[:12] + "..."
        
        st.markdown(f"""
        <div class="circular-metric">
            <div class="circle circle-4">
                <div class="circle-number" style="font-size: 1.0rem;">{ai_display}</div>
            </div>
            <div class="metric-title">Most Used AI</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="circular-metric">
            <div class="circle circle-5">
                <div class="circle-number">{total_users}</div>
                <div class="circle-label">Total</div>
            </div>
            <div class="metric-title">Total Users</div>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main dashboard function."""
    # Check if database is configured
    if not DATABASE_AVAILABLE:
        show_configuration_help()
        return
    
    # Header
    st.markdown('<h1 class="main-header">📊 PostgreSQL Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Connection status
    try:
        if db_manager.test_connection():
            st.success("✅ Database connected successfully")
        else:
            st.error("❌ Database connection failed")
            show_configuration_help()
            return
    except Exception as e:
        st.error(f"❌ Database connection error: {e}")
        show_configuration_help()
        return
    
    # Auto-refresh controls
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    with col2:
        last_update = datetime.now().strftime("%H:%M:%S")
        st.info(f"🕒 Last updated: {last_update}")
    
    # Show top metrics first
    with st.spinner("Loading key metrics..."):
        show_top_metrics()
    
    st.markdown("---")
    
    # Load and display prompt reviews table
    with st.spinner("Loading prompt review data..."):
        show_prompt_reviews_table()
    
    # Auto-refresh option in sidebar
    st.sidebar.markdown("## ⚙️ Settings")
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh every 30 seconds")
    
    if auto_refresh:
        import time
        time.sleep(30)
        st.rerun()
    
    # Dashboard info
    st.sidebar.markdown("## 📊 Dashboard Info")
    st.sidebar.info(f"""
    **Dashboard:** PostgreSQL Analytics
    **Data Source:** prompt_review + usertable
    **Features:**
    - Key metrics overview (5 circular displays)
    - Latest prompt reviews first
    - User information display
    - Processing time tracking
    - Full prompt details view
    
    **Query Type:** Read-Only Analytics
    **Last Update:** {last_update}
    """)

if __name__ == "__main__":
    main() 