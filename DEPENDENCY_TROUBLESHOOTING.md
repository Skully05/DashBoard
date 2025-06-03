# 🔧 Dependency Troubleshooting Guide

If you're encountering dependency conflicts during installation, follow these solutions:

## 🚨 Common Error: Dependency Conflicts

### Error Message:
```
ERROR: Cannot install -r requirements.txt (line X) and packagename==X.X.X because these package versions have conflicting dependencies.
ERROR: ResolutionImpossible: for help visit https://pip.pypa.io/en/latest/topics/dependency-resolution/
```

## 🔨 Solutions (Try in Order)

### Solution 1: Use Updated Requirements (Recommended)
The latest deployment package includes updated requirements.txt with compatible versions.

```bash
# Use the latest deployment package: dashboard_deployment_20250603_220003.zip
pip install -r requirements.txt
```

### Solution 2: Use Minimal Requirements
If conflicts persist, try the minimal requirements file:

```bash
pip install -r requirements_minimal.txt
```

### Solution 3: Install Core Packages Only
Install packages individually without version constraints:

```bash
pip install streamlit
pip install langchain
pip install langchain-community
pip install psycopg2-binary
pip install sqlalchemy
pip install python-dotenv
pip install pandas
pip install plotly
pip install numpy
```

### Solution 4: Use Fresh Virtual Environment
Create a completely new virtual environment:

```bash
# Remove old environment
rmdir /s dashboard_env  # Windows
# rm -rf dashboard_env    # Linux/Mac

# Create fresh environment
python -m venv dashboard_env
dashboard_env\Scripts\activate  # Windows
# source dashboard_env/bin/activate  # Linux/Mac

# Upgrade pip first
python -m pip install --upgrade pip

# Install minimal requirements
pip install -r requirements_minimal.txt
```

### Solution 5: Install with No Dependencies Check (Last Resort)
```bash
pip install -r requirements.txt --no-deps
# Then install missing dependencies manually
```

## 🔄 Alternative Package Versions

If specific packages cause issues, try these alternatives:

### LangChain Alternatives:
```bash
# Latest stable versions
pip install langchain>=0.1.0
pip install langchain-community>=0.0.20

# Or use latest available
pip install langchain --upgrade
pip install langchain-community --upgrade
```

### Database Connection Alternatives:
```bash
# If psycopg2-binary fails
pip install psycopg2  # Requires compilation
# OR
pip install pg8000  # Pure Python alternative
```

## 🐍 Python Version Compatibility

Ensure you're using a compatible Python version:

- **Recommended**: Python 3.8 - 3.11
- **Minimum**: Python 3.8
- **Not recommended**: Python 3.12+ (may have compatibility issues)

Check your Python version:
```bash
python --version
```

## 🔧 System-Specific Solutions

### Windows:
```bash
# If Visual C++ build tools are missing
# Download and install Microsoft C++ Build Tools
# Or use pre-compiled packages
pip install --only-binary=all -r requirements.txt
```

### Linux/Mac:
```bash
# Install system dependencies first
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install python3-dev libpq-dev

# macOS:
brew install postgresql
```

## 🚀 Quick Test After Installation

After resolving dependencies, test the installation:

```bash
python test_connection.py
```

If successful, you should see:
```
✅ Database connection successful!
```

## 📝 Manual Requirements Installation

If all else fails, install each package manually:

```bash
# Core packages (install in this order)
pip install python-dotenv
pip install numpy
pip install pandas
pip install sqlalchemy
pip install psycopg2-binary
pip install streamlit
pip install plotly

# LangChain packages (install last)
pip install langchain-core
pip install langchain-community
pip install langchain
```

## 🆘 Still Having Issues?

1. **Check Python version**: Ensure Python 3.8-3.11
2. **Update pip**: `python -m pip install --upgrade pip`
3. **Clear pip cache**: `pip cache purge`
4. **Use virtual environment**: Always use a clean virtual environment
5. **Check system dependencies**: Install PostgreSQL development libraries

## 📋 Working Combinations

These combinations are known to work together:

### Combination A (Latest):
```
streamlit>=1.28.0
langchain>=0.1.0
langchain-community>=0.0.20
psycopg2-binary>=2.9.7
sqlalchemy>=2.0.23
```

### Combination B (Stable):
```
streamlit==1.28.0
langchain==0.1.5
langchain-community==0.0.25
psycopg2-binary==2.9.7
sqlalchemy==2.0.23
```

### Combination C (Minimal):
```
streamlit
langchain
langchain-community
psycopg2-binary
sqlalchemy
python-dotenv
pandas
plotly
```

Choose the combination that works best for your system! 