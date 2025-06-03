#!/bin/bash

echo "🚀 Starting PostgreSQL Analytics Dashboard..."
echo

# Check if virtual environment exists
if [ ! -d "dashboard_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv dashboard_env
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment. Make sure Python 3 is installed."
        exit 1
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source dashboard_env/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment."
    exit 1
fi

# Upgrade pip first
echo "🔄 Upgrading pip..."
python -m pip install --upgrade pip --quiet

# Install requirements with fallback
echo "📚 Installing/updating dependencies..."
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "⚠️  Standard requirements failed. Trying minimal requirements..."
    pip install -r requirements_minimal.txt --quiet
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies."
        echo
        echo "🔧 TROUBLESHOOTING:"
        echo "1. Check your Python version: python --version"
        echo "2. Ensure Python 3.8-3.11 (avoid 3.12+)"
        echo "3. See DEPENDENCY_TROUBLESHOOTING.md for detailed solutions"
        echo "4. Try manual installation: pip install streamlit langchain psycopg2-binary"
        echo
        exit 1
    else
        echo "✅ Minimal requirements installed successfully!"
    fi
else
    echo "✅ Standard requirements installed successfully!"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please copy env_example.txt to .env and configure your database settings."
    echo
    read -p "Would you like to copy the template now? (y/n): " choice
    if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
        cp env_example.txt .env
        echo "✅ Template copied to .env - Please edit it with your database credentials."
        echo "Opening .env file for editing..."
        ${EDITOR:-nano} .env
        echo
        echo "Press Enter after you've configured the database settings..."
        read
    fi
    echo
fi

# Test database connection
if [ -f ".env" ]; then
    echo "🔍 Testing database connection..."
    python test_connection.py
    if [ $? -ne 0 ]; then
        echo "⚠️  Database connection test failed."
        echo "Please check your .env configuration and database server."
        echo
    else
        echo "✅ Database connection successful!"
        echo
    fi
fi

# Start the dashboard
echo "🌟 Starting Streamlit dashboard..."
echo
echo "The dashboard will be available at:"
echo "🔗 Local:   http://localhost:8501"
echo "🌐 Network: http://$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'YOUR_IP'):8501"
echo
echo "Press Ctrl+C to stop the dashboard"
echo

streamlit run simple_dashboard.py

echo
echo "👋 Dashboard stopped." 