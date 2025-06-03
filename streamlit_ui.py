"""
Streamlit UI components for the PostgreSQL Analytics Dashboard.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import logging
from typing import Optional, Dict, Any, List
from langchain_agent import get_sql_agent
from database import db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DashboardUI:
    """Main dashboard UI class with all Streamlit components."""
    
    def __init__(self):
        """Initialize dashboard UI."""
        self.sql_agent = None
        self.last_refresh = None
        self.auto_refresh_interval = 30  # seconds
    
    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="PostgreSQL Analytics Dashboard",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def setup_custom_css(self):
        """Add custom CSS styling."""
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-container {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .chat-container {
            border: 1px solid #ddd;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1rem 0;
            background-color: #fafafa;
        }
        .query-result {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #007bff;
        }
        .error-message {
            background-color: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #dc3545;
        }
        .success-message {
            background-color: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #28a745;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_sql_agent(self):
        """Initialize SQL agent if not already done."""
        if self.sql_agent is None:
            try:
                with st.spinner("Initializing SQL Agent..."):
                    self.sql_agent = get_sql_agent()
                st.success("SQL Agent initialized successfully!")
            except Exception as e:
                st.error(f"Failed to initialize SQL Agent: {e}")
                logger.error(f"SQL Agent initialization error: {e}")
                return False
        return True
    
    def test_database_connection(self):
        """Test database connection and show status."""
        try:
            if db_manager.test_connection():
                st.success("✅ Database connection successful")
                return True
            else:
                st.error("❌ Database connection failed")
                return False
        except Exception as e:
            st.error(f"❌ Database connection error: {e}")
            return False
    
    def show_header(self):
        """Display main dashboard header."""
        st.markdown('<h1 class="main-header">🔍 PostgreSQL Analytics Dashboard</h1>', 
                   unsafe_allow_html=True)
        
        # Connection status and refresh info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if self.test_database_connection():
                st.markdown("**Status:** 🟢 Connected")
            else:
                st.markdown("**Status:** 🔴 Disconnected")
        
        with col2:
            if self.last_refresh:
                st.markdown(f"**Last Refresh:** {self.last_refresh.strftime('%H:%M:%S')}")
            else:
                st.markdown("**Last Refresh:** Never")
        
        with col3:
            if st.button("🔄 Manual Refresh"):
                st.rerun()
    
    def show_summary_metrics(self, df: pd.DataFrame):
        """Display summary metrics from the main query."""
        if df.empty:
            st.warning("No data available for metrics")
            return
        
        st.markdown("### 📊 Summary Metrics")
        
        # Calculate metrics
        total_users = len(df)
        total_prompts = df['total_prompts'].sum() if 'total_prompts' in df.columns else 0
        avg_prompts_per_user = df['avg_prompts_per_day'].mean() if 'avg_prompts_per_day' in df.columns else 0
        most_active_user = df.loc[df['total_prompts'].idxmax(), 'name'] if 'total_prompts' in df.columns and not df.empty else "N/A"
        
        # Display metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Users",
                value=f"{total_users:,}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="Total Prompts",
                value=f"{total_prompts:,}",
                delta=None
            )
        
        with col3:
            st.metric(
                label="Avg Prompts/User/Day",
                value=f"{avg_prompts_per_user:.2f}",
                delta=None
            )
        
        with col4:
            st.metric(
                label="Most Active User",
                value=most_active_user,
                delta=None
            )
    
    def show_main_data_table(self, df: pd.DataFrame):
        """Display the main data table with filtering options."""
        st.markdown("### 📋 User Prompt Usage Statistics")
        
        if df.empty:
            st.warning("No data available")
            return
        
        # Filtering options
        with st.expander("🔍 Filter Options", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                # User filter
                if 'name' in df.columns:
                    user_names = ['All'] + sorted(df['name'].dropna().unique().tolist())
                    selected_user = st.selectbox("Filter by User", user_names)
                else:
                    selected_user = 'All'
            
            with col2:
                # Minimum prompts filter
                if 'total_prompts' in df.columns:
                    min_prompts = st.number_input(
                        "Minimum Total Prompts",
                        min_value=0,
                        max_value=int(df['total_prompts'].max()) if not df['total_prompts'].empty else 100,
                        value=0
                    )
                else:
                    min_prompts = 0
        
        # Apply filters
        filtered_df = df.copy()
        
        if selected_user != 'All' and 'name' in df.columns:
            filtered_df = filtered_df[filtered_df['name'] == selected_user]
        
        if 'total_prompts' in df.columns:
            filtered_df = filtered_df[filtered_df['total_prompts'] >= min_prompts]
        
        # Display filtered results
        st.markdown(f"**Showing {len(filtered_df)} of {len(df)} users**")
        
        # Format numeric columns
        if not filtered_df.empty:
            display_df = filtered_df.copy()
            
            # Format numeric columns for better display
            numeric_columns = ['avg_prompts_per_day', 'calculated_avg_prompts_per_day']
            for col in numeric_columns:
                if col in display_df.columns:
                    display_df[col] = display_df[col].round(2)
            
            # Display table
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No data matches the current filters")
    
    def show_charts(self, df: pd.DataFrame):
        """Display charts and visualizations."""
        if df.empty:
            st.warning("No data available for charts")
            return
        
        st.markdown("### 📈 Visualizations")
        
        # Chart tabs
        tab1, tab2, tab3 = st.tabs(["📊 Bar Chart", "📈 Distribution", "🔢 Top Users"])
        
        with tab1:
            if 'name' in df.columns and 'total_prompts' in df.columns:
                # Bar chart of total prompts by user
                top_users = df.nlargest(20, 'total_prompts')
                
                fig = px.bar(
                    top_users,
                    x='name',
                    y='total_prompts',
                    title='Total Prompts by User (Top 20)',
                    labels={'total_prompts': 'Total Prompts', 'name': 'User Name'}
                )
                fig.update_xaxis(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Required columns not available for bar chart")
        
        with tab2:
            if 'avg_prompts_per_day' in df.columns:
                # Histogram of average prompts per day
                fig = px.histogram(
                    df,
                    x='avg_prompts_per_day',
                    nbins=30,
                    title='Distribution of Average Prompts per Day',
                    labels={'avg_prompts_per_day': 'Average Prompts per Day', 'count': 'Number of Users'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Required columns not available for distribution chart")
        
        with tab3:
            if 'name' in df.columns and 'avg_prompts_per_day' in df.columns:
                # Top users by average prompts per day
                top_avg_users = df.nlargest(15, 'avg_prompts_per_day')
                
                fig = px.bar(
                    top_avg_users,
                    x='avg_prompts_per_day',
                    y='name',
                    orientation='h',
                    title='Top 15 Users by Average Prompts per Day',
                    labels={'avg_prompts_per_day': 'Average Prompts per Day', 'name': 'User Name'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Required columns not available for top users chart")
    
    def show_chat_interface(self):
        """Display chat interface for natural language queries."""
        st.markdown("### 💬 Ask Questions About Your Data")
        
        if not self.initialize_sql_agent():
            return
        
        # Initialize chat history in session state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Chat input
        user_question = st.chat_input("Ask a question about your data...")
        
        if user_question:
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_question,
                "timestamp": datetime.now()
            })
            
            # Process the question
            try:
                with st.spinner("Generating and executing query..."):
                    result_df = self.sql_agent.execute_query_with_context(user_question)
                
                # Add assistant response to history
                response_content = {
                    "text": f"Query executed successfully! Found {len(result_df)} results.",
                    "data": result_df,
                    "sql_query": self.sql_agent.conversation_history[-1].get('sql_query', '')
                }
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response_content,
                    "timestamp": datetime.now()
                })
                
            except Exception as e:
                error_message = f"Error: {str(e)}"
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": {"text": error_message, "error": True},
                    "timestamp": datetime.now()
                })
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("#### Conversation History")
            
            for i, message in enumerate(reversed(st.session_state.chat_history[-10:])):  # Show last 10 messages
                with st.container():
                    if message["role"] == "user":
                        st.markdown(f"**🧑 You:** {message['content']}")
                    else:
                        content = message['content']
                        if isinstance(content, dict):
                            if content.get('error'):
                                st.markdown(f'<div class="error-message">🤖 <strong>Assistant:</strong> {content["text"]}</div>', 
                                          unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="success-message">🤖 <strong>Assistant:</strong> {content["text"]}</div>', 
                                          unsafe_allow_html=True)
                                
                                # Show SQL query if available
                                if content.get('sql_query'):
                                    with st.expander("View Generated SQL Query"):
                                        st.code(content['sql_query'], language='sql')
                                
                                # Show data if available
                                if 'data' in content and not content['data'].empty:
                                    st.dataframe(content['data'], use_container_width=True)
                        else:
                            st.markdown(f"**🤖 Assistant:** {content}")
                    
                    st.markdown("---")
        
        # Clear chat history button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            if self.sql_agent:
                self.sql_agent.clear_conversation_history()
            st.rerun()
    
    def show_sidebar(self):
        """Display sidebar with controls and information."""
        st.sidebar.markdown("## 🎛️ Dashboard Controls")
        
        # Auto-refresh settings
        st.sidebar.markdown("### Auto-Refresh Settings")
        auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=False)
        
        if auto_refresh:
            refresh_interval = st.sidebar.selectbox(
                "Refresh Interval",
                options=[30, 60, 120, 300],
                format_func=lambda x: f"{x} seconds",
                index=0
            )
            self.auto_refresh_interval = refresh_interval
            
            # Auto-refresh logic
            if auto_refresh:
                time.sleep(refresh_interval)
                st.rerun()
        
        # Database info
        st.sidebar.markdown("### 📊 Database Info")
        try:
            schema_info = db_manager.get_schema_info()
            st.sidebar.markdown(f"**Tables:** {len(schema_info)}")
            
            if schema_info:
                with st.sidebar.expander("View Schema"):
                    for table_name, columns in schema_info.items():
                        st.write(f"**{table_name}** ({len(columns)} columns)")
        except Exception as e:
            st.sidebar.error(f"Failed to load schema info: {e}")
        
        # Tips and help
        st.sidebar.markdown("### 💡 Tips")
        st.sidebar.markdown("""
        - Use the chat interface to ask questions in natural language
        - Try questions like:
          - "Show me users with more than 100 prompts"
          - "What's the average number of prompts per user?"
          - "Who are the top 10 most active users?"
        - The system operates in read-only mode for safety
        - Data refreshes automatically if enabled
        """)
    
    def load_main_data(self) -> pd.DataFrame:
        """Load the main dashboard data."""
        if not self.initialize_sql_agent():
            return pd.DataFrame()
        
        try:
            with st.spinner("Loading data..."):
                df = self.sql_agent.get_default_query_results()
                self.last_refresh = datetime.now()
                return df
        except Exception as e:
            st.error(f"Failed to load data: {e}")
            logger.error(f"Data loading error: {e}")
            return pd.DataFrame()
    
    def run_dashboard(self):
        """Main dashboard execution function."""
        self.setup_custom_css()
        
        # Show sidebar
        self.show_sidebar()
        
        # Main content
        self.show_header()
        
        # Load and display main data
        main_df = self.load_main_data()
        
        if not main_df.empty:
            # Summary metrics
            self.show_summary_metrics(main_df)
            
            # Main data table
            self.show_main_data_table(main_df)
            
            # Charts
            self.show_charts(main_df)
        
        # Chat interface
        st.markdown("---")
        self.show_chat_interface()


# Global dashboard instance
dashboard = DashboardUI() 