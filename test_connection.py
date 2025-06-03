#!/usr/bin/env python3
"""
Test script to validate the PostgreSQL Analytics Dashboard setup.
Run this before starting the main application to ensure everything is configured correctly.
"""

import os
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✅ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False
    
    try:
        import psycopg2
        print("✅ Psycopg2 imported successfully")
    except ImportError as e:
        print(f"❌ Psycopg2 import failed: {e}")
        return False
    
    try:
        from langchain.llms.base import LLM
        print("✅ LangChain imported successfully")
    except ImportError as e:
        print(f"❌ LangChain import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ Python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ Python-dotenv import failed: {e}")
        return False
    
    return True


def test_env_file():
    """Test that .env file exists and contains required variables."""
    print("\n🧪 Testing environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("💡 Please create a .env file with your database credentials")
        print("📝 Use env_example.txt as a template")
        return False
    
    print("✅ .env file found")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    print("✅ All required environment variables found")
    return True


def test_modules():
    """Test that our custom modules can be imported."""
    print("\n🧪 Testing custom modules...")
    
    try:
        from database import DatabaseManager, db_manager
        print("✅ Database module imported successfully")
    except ImportError as e:
        print(f"❌ Database module import failed: {e}")
        return False
    
    try:
        from langchain_agent import SQLAgent, get_sql_agent
        print("✅ LangChain agent module imported successfully")
    except ImportError as e:
        print(f"❌ LangChain agent module import failed: {e}")
        return False
    
    try:
        from streamlit_ui import DashboardUI, dashboard
        print("✅ Streamlit UI module imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit UI module import failed: {e}")
        return False
    
    return True


def test_database_connection():
    """Test database connection."""
    print("\n🧪 Testing database connection...")
    
    try:
        from database import db_manager
        
        if db_manager.test_connection():
            print("✅ Database connection successful")
            
            # Test schema retrieval
            schema_info = db_manager.get_schema_info()
            if schema_info:
                print(f"✅ Schema retrieved successfully ({len(schema_info)} tables found)")
                print("📊 Available tables:")
                for table_name in schema_info.keys():
                    print(f"   - {table_name}")
            else:
                print("⚠️ No tables found in schema")
            
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False


def test_sql_agent():
    """Test SQL agent initialization."""
    print("\n🧪 Testing SQL agent...")
    
    try:
        from langchain_agent import get_sql_agent
        
        agent = get_sql_agent()
        print("✅ SQL agent initialized successfully")
        
        # Test default query
        try:
            df = agent.get_default_query_results()
            print(f"✅ Default query executed successfully ({len(df)} rows returned)")
        except Exception as e:
            print(f"⚠️ Default query failed (this might be expected if tables don't exist): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ SQL agent initialization failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 PostgreSQL Analytics Dashboard - Setup Validation")
    print("=" * 60)
    
    tests = [
        ("Dependencies", test_imports),
        ("Environment", test_env_file),
        ("Custom Modules", test_modules),
        ("Database Connection", test_database_connection),
        ("SQL Agent", test_sql_agent),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("🚀 You can now run: streamlit run app.py")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please fix the issues before running the dashboard.")
        
        if not results[0][1]:  # Dependencies failed
            print("\n💡 To install dependencies: pip install -r requirements.txt")
        
        if not results[1][1]:  # Environment failed
            print("\n💡 To setup environment: copy env_example.txt to .env and fill in your database credentials")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)