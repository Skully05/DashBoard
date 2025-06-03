"""
Main Streamlit application for PostgreSQL Analytics Dashboard.
Run this file with: streamlit run app.py
"""

import streamlit as st
import sys
import os
import logging
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def check_environment():
    """Check if the environment is properly configured."""
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        st.error("""
        ⚠️ **Environment Configuration Missing**
        
        Please create a `.env` file in the project root with your database credentials:
        
        ```
        DB_HOST=localhost
        DB_PORT=5432
        DB_NAME=your_database_name
        DB_USER=your_username
        DB_PASSWORD=your_password
        DB_SSL_MODE=prefer
        ```
        
        You can use `env_example.txt` as a template.
        """)
        return False
    
    # Import our modules after page config is set
    try:
        from database import db_manager
    except ImportError as e:
        st.error(f"Import error: {e}")
        st.error("Please ensure all required modules are available and dependencies are installed.")
        return False
    
    # Check database connection
    try:
        if not db_manager.test_connection():
            st.error("""
            ❌ **Database Connection Failed**
            
            Please check your database credentials in the `.env` file and ensure:
            - PostgreSQL server is running
            - Database exists and is accessible
            - Credentials are correct
            - Network connectivity is available
            """)
            return False
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return False
    
    return True


def show_welcome_message():
    """Show welcome message and instructions."""
    st.markdown("""
    ## 🎉 Welcome to PostgreSQL Analytics Dashboard!
    
    This dashboard provides powerful analytics capabilities for your PostgreSQL database with:
    
    ### ✨ Key Features:
    - **🔍 Interactive Data Exploration**: Browse and filter your data with ease
    - **💬 Natural Language Queries**: Ask questions in plain English and get SQL results
    - **📊 Beautiful Visualizations**: Charts and graphs to understand your data
    - **🔄 Real-time Updates**: Auto-refresh capabilities for live data monitoring
    - **🛡️ Read-Only Safety**: All operations are read-only for data protection
    - **🧠 Conversation Memory**: Context-aware query generation
    
    ### 🚀 Getting Started:
    1. **Main Dashboard**: View your prompt usage statistics and user analytics
    2. **Interactive Chat**: Ask questions like "Show me the top 10 most active users"
    3. **Filters & Charts**: Explore data with built-in filtering and visualization tools
    4. **Auto-Refresh**: Enable automatic data updates in the sidebar
    
    ### 🎯 Example Questions to Try:
    - "Who are the users with the highest prompt usage?"
    - "Show me users created in the last month"
    - "What's the distribution of prompts per day?"
    - "Find users with email addresses containing 'gmail'"
    
    ---
    """)


def main():
    """Main application function."""
    # MUST be the very first Streamlit command
    st.set_page_config(
        page_title="PostgreSQL Analytics Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    logger.info("Starting PostgreSQL Analytics Dashboard")
    
    # Check environment configuration
    if not check_environment():
        st.stop()
    
    # Import our modules after environment check
    try:
        from streamlit_ui import dashboard
    except ImportError as e:
        st.error(f"Import error: {e}")
        st.error("Please ensure all required modules are available and dependencies are installed.")
        st.stop()
    
    # Show welcome message
    show_welcome_message()
    
    try:
        # Run the main dashboard (without calling setup_page_config again)
        dashboard.setup_custom_css()
        dashboard.show_sidebar()
        dashboard.show_header()
        
        # Load and display main data
        main_df = dashboard.load_main_data()
        
        if not main_df.empty:
            # Summary metrics
            dashboard.show_summary_metrics(main_df)
            
            # Main data table
            dashboard.show_main_data_table(main_df)
            
            # Charts
            dashboard.show_charts(main_df)
        
        # Chat interface
        st.markdown("---")
        dashboard.show_chat_interface()
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        st.error(f"""
        ❌ **Dashboard Error**
        
        An error occurred while running the dashboard: {str(e)}
        
        Please check the logs for more details and ensure all dependencies are properly installed.
        """)
        
        # Show error details in expander
        with st.expander("Error Details"):
            st.exception(e)


if __name__ == "__main__":
    main() 