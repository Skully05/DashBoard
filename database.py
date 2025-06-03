"""
Database connection and management module for PostgreSQL.
"""

import os
import logging
from typing import Optional, Dict, Any, List
import sqlalchemy as sa
from sqlalchemy import create_engine, text, MetaData, inspect
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_config():
    """Get database configuration from environment variables or Streamlit secrets."""
    try:
        # Try to import streamlit to check if running in Streamlit Cloud
        import streamlit as st
        
        # If running in Streamlit Cloud, use secrets
        if hasattr(st, 'secrets'):
            return {
                'host': st.secrets.get('DB_HOST', 'localhost'),
                'port': int(st.secrets.get('DB_PORT', 5432)),
                'database': st.secrets.get('DB_NAME'),
                'user': st.secrets.get('DB_USER'),
                'password': st.secrets.get('DB_PASSWORD'),
                'sslmode': st.secrets.get('DB_SSL_MODE', 'prefer')
            }
    except ImportError:
        pass
    
    # Fallback to environment variables
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 5432)),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('DB_SSL_MODE', 'prefer')
    }


class DatabaseManager:
    """Manages PostgreSQL database connections and operations."""
    
    def __init__(self):
        """Initialize database manager with connection parameters from environment or Streamlit secrets."""
        self.db_config = get_db_config()
        
        # Validate required configuration
        required_fields = ['database', 'user', 'password']
        missing_fields = [field for field in required_fields if not self.db_config[field]]
        
        if missing_fields:
            raise ValueError(f"Missing required database configuration: {missing_fields}")
        
        self.engine = None
        self.connection_string = self._build_connection_string()
    
    def _build_connection_string(self) -> str:
        """Build PostgreSQL connection string."""
        return (
            f"postgresql://{self.db_config['user']}:{self.db_config['password']}@"
            f"{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
            f"?sslmode={self.db_config['sslmode']}"
        )
    
    def get_engine(self):
        """Get or create SQLAlchemy engine."""
        if self.engine is None:
            try:
                self.engine = create_engine(
                    self.connection_string,
                    pool_size=5,
                    max_overflow=10,
                    pool_pre_ping=True,
                    echo=False
                )
                logger.info("Database engine created successfully")
            except Exception as e:
                logger.error(f"Failed to create database engine: {e}")
                raise
        return self.engine
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            engine = self.get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute a read-only query and return results as DataFrame.
        
        Args:
            query: SQL query string (must be read-only)
            params: Optional query parameters
            
        Returns:
            pandas.DataFrame with query results
        """
        # Security check: ensure query is read-only
        query_upper = query.strip().upper()
        
        # Use word boundaries to match complete keywords only
        forbidden_patterns = [
            r'\bINSERT\b', r'\bUPDATE\b', r'\bDELETE\b', r'\bDROP\b', 
            r'\bCREATE\b', r'\bALTER\b', r'\bTRUNCATE\b', r'\bGRANT\b', 
            r'\bREVOKE\b', r'\bEXEC\b', r'\bEXECUTE\b'
        ]
        
        for pattern in forbidden_patterns:
            if re.search(pattern, query_upper):
                keyword = pattern.replace(r'\b', '').replace('\\', '')
                raise ValueError(f"Query contains forbidden keyword: {keyword}. Only read-only operations allowed.")
        
        try:
            engine = self.get_engine()
            with engine.connect() as conn:
                if params:
                    result = pd.read_sql_query(text(query), conn, params=params)
                else:
                    result = pd.read_sql_query(query, conn)
            logger.info(f"Query executed successfully, returned {len(result)} rows")
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def get_schema_info(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get database schema information for LangChain agent.
        
        Returns:
            Dictionary with table names and their column info
        """
        try:
            engine = self.get_engine()
            inspector = inspect(engine)
            schema_info = {}
            
            # Get all table names
            table_names = inspector.get_table_names()
            
            for table_name in table_names:
                columns = inspector.get_columns(table_name)
                schema_info[table_name] = [
                    {
                        'name': col['name'],
                        'type': str(col['type']),
                        'nullable': col['nullable'],
                        'default': col.get('default')
                    }
                    for col in columns
                ]
            
            logger.info(f"Retrieved schema for {len(schema_info)} tables")
            return schema_info
        except Exception as e:
            logger.error(f"Failed to retrieve schema info: {e}")
            return {}
    
    def get_schema_string(self) -> str:
        """
        Get formatted schema string for LangChain prompts.
        
        Returns:
            Formatted string describing database schema
        """
        schema_info = self.get_schema_info()
        schema_parts = []
        
        for table_name, columns in schema_info.items():
            table_part = f"\nTable: {table_name}\n" + "="*40
            column_parts = []
            
            for col in columns:
                nullable_str = "NULL" if col['nullable'] else "NOT NULL"
                default_str = f" DEFAULT {col['default']}" if col['default'] else ""
                column_parts.append(f"  {col['name']}: {col['type']} {nullable_str}{default_str}")
            
            table_part += "\n" + "\n".join(column_parts)
            schema_parts.append(table_part)
        
        return "\n".join(schema_parts)
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """
        Get sample data from a table for schema understanding.
        
        Args:
            table_name: Name of the table
            limit: Number of sample rows to retrieve
            
        Returns:
            DataFrame with sample data
        """
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.execute_query(query)


# Global database manager instance
db_manager = DatabaseManager() 