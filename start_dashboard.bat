@echo off
echo 🚀 Starting PostgreSQL Analytics Dashboard...
echo.

REM Check if virtual environment exists
if not exist "dashboard_env" (
    echo 📦 Creating virtual environment...
    python -m venv dashboard_env
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment. Make sure Python is installed.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call dashboard_env\Scripts\activate
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Upgrade pip first
echo 🔄 Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install requirements with fallback
echo 📚 Installing/updating dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ⚠️  Standard requirements failed. Trying minimal requirements...
    pip install -r requirements_minimal.txt --quiet
    if errorlevel 1 (
        echo ❌ Failed to install dependencies.
        echo.
        echo 🔧 TROUBLESHOOTING:
        echo 1. Check your Python version: python --version
        echo 2. Ensure Python 3.8-3.11 (avoid 3.12+)
        echo 3. See DEPENDENCY_TROUBLESHOOTING.md for detailed solutions
        echo 4. Try manual installation: pip install streamlit langchain psycopg2-binary
        echo.
        pause
        exit /b 1
    ) else (
        echo ✅ Minimal requirements installed successfully!
    )
) else (
    echo ✅ Standard requirements installed successfully!
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  Warning: .env file not found!
    echo Please copy env_example.txt to .env and configure your database settings.
    echo.
    echo Would you like to copy the template now? (y/n)
    set /p choice="Enter choice: "
    if /i "%choice%"=="y" (
        copy env_example.txt .env
        echo ✅ Template copied to .env - Please edit it with your database credentials.
        echo Opening .env file for editing...
        notepad .env
        echo.
        echo Press any key after you've configured the database settings...
        pause >nul
    )
    echo.
)

REM Test database connection
if exist ".env" (
    echo 🔍 Testing database connection...
    python test_connection.py
    if errorlevel 1 (
        echo ⚠️  Database connection test failed.
        echo Please check your .env configuration and database server.
        echo.
    ) else (
        echo ✅ Database connection successful!
        echo.
    )
)

REM Start the dashboard
echo 🌟 Starting Streamlit dashboard...
echo.
echo The dashboard will be available at:
echo 🔗 Local:   http://localhost:8501
echo 🌐 Network: http://[YOUR_IP]:8501
echo.
echo Press Ctrl+C to stop the dashboard
echo.

streamlit run simple_dashboard.py

echo.
echo 👋 Dashboard stopped.
pause 