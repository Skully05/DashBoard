#!/usr/bin/env python3
"""
Deployment Package Creator for PostgreSQL Analytics Dashboard

This script creates a deployment package containing all necessary files
for deploying the dashboard on another PC.
"""

import os
import shutil
import zipfile
import datetime
from pathlib import Path

def create_deployment_package():
    """Create a deployment package with all necessary files."""
    
    # Get current directory
    source_dir = Path.cwd()
    
    # Create timestamp for unique package name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"dashboard_deployment_{timestamp}"
    package_dir = source_dir / package_name
    
    print(f"🚀 Creating deployment package: {package_name}")
    print(f"📁 Source directory: {source_dir}")
    
    # Create package directory
    package_dir.mkdir(exist_ok=True)
    
    # Files to include in deployment
    files_to_copy = [
        "simple_dashboard.py",
        "database.py", 
        "langchain_agent.py",
        "requirements.txt",
        "requirements_minimal.txt",
        "env_example.txt",
        "README.md",
        "DEPLOYMENT.md",
        "DEPENDENCY_TROUBLESHOOTING.md",
        "start_dashboard.bat",
        "start_dashboard.sh",
        "test_connection.py",
        "app.py",
        "streamlit_ui.py",
        "test_query.py"
    ]
    
    # Optional files (copy if they exist)
    optional_files = [
        "security_test.py",
        ".gitignore"
    ]
    
    copied_files = []
    missing_files = []
    
    # Copy required files
    for file_name in files_to_copy:
        source_file = source_dir / file_name
        if source_file.exists():
            shutil.copy2(source_file, package_dir / file_name)
            copied_files.append(file_name)
            print(f"✅ Copied: {file_name}")
        else:
            missing_files.append(file_name)
            print(f"⚠️  Missing: {file_name}")
    
    # Copy optional files
    for file_name in optional_files:
        source_file = source_dir / file_name
        if source_file.exists():
            shutil.copy2(source_file, package_dir / file_name)
            copied_files.append(file_name)
            print(f"✅ Copied (optional): {file_name}")
    
    # Create deployment instructions file
    instructions_file = package_dir / "QUICK_START.txt"
    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write("""🚀 QUICK START DEPLOYMENT GUIDE
=====================================

1. REQUIREMENTS:
   - Python 3.8-3.11 (avoid Python 3.12+)
   - Access to your PostgreSQL database

2. QUICK SETUP (Windows):
   - Double-click: start_dashboard.bat
   - Follow the prompts to configure database

3. QUICK SETUP (Linux/Mac):
   - Run: chmod +x start_dashboard.sh
   - Run: ./start_dashboard.sh
   - Follow the prompts to configure database

4. MANUAL SETUP:
   a) Create virtual environment:
      python -m venv dashboard_env
   
   b) Activate environment:
      Windows: dashboard_env\\Scripts\\activate
      Linux/Mac: source dashboard_env/bin/activate
   
   c) Install dependencies:
      pip install -r requirements.txt
      
      ⚠️ If dependencies fail:
      - Try: pip install -r requirements_minimal.txt
      - See DEPENDENCY_TROUBLESHOOTING.md for solutions
   
   d) Configure database:
      copy env_example.txt .env
      Edit .env with your database credentials
   
   e) Test connection:
      python test_connection.py
   
   f) Start dashboard:
      streamlit run simple_dashboard.py

5. ACCESS:
   - Local: http://localhost:8501
   - Network: http://[YOUR_IP]:8501

6. TROUBLESHOOTING:
   - Dependency issues: See DEPENDENCY_TROUBLESHOOTING.md
   - General issues: See DEPLOYMENT.md
   - Check dashboard.log for application logs
   - Ensure database server allows remote connections

📞 For detailed instructions, see DEPLOYMENT.md
🔧 For dependency problems, see DEPENDENCY_TROUBLESHOOTING.md

📄 FILES INCLUDED:
   - simple_dashboard.py: Main Streamlit dashboard
   - app.py: Alternative entry point
   - database.py: Database connection manager
   - langchain_agent.py: LangChain SQL agent
   - streamlit_ui.py: UI components
   - test_connection.py: Database connection tester
   - requirements.txt: Python dependencies (latest)
   - requirements_minimal.txt: Minimal dependencies (fallback)
   - env_example.txt: Environment variables template
   - start_dashboard.bat: Windows startup script
   - start_dashboard.sh: Linux/Mac startup script
   - DEPENDENCY_TROUBLESHOOTING.md: Dependency conflict solutions
""")
    
    print(f"✅ Created: QUICK_START.txt")
    
    # Create zip file
    zip_file_name = f"{package_name}.zip"
    zip_path = source_dir / zip_file_name
    
    print(f"📦 Creating zip file: {zip_file_name}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(package_dir)
                zipf.write(file_path, arc_name)
    
    # Clean up temporary directory
    shutil.rmtree(package_dir)
    
    # Create summary
    print("\n" + "="*50)
    print("📦 DEPLOYMENT PACKAGE CREATED SUCCESSFULLY!")
    print("="*50)
    print(f"📁 Package file: {zip_file_name}")
    print(f"📏 Package size: {zip_path.stat().st_size / 1024:.1f} KB")
    print(f"📄 Files included: {len(copied_files)}")
    
    if missing_files:
        print(f"⚠️  Missing files: {len(missing_files)}")
        for file in missing_files:
            print(f"   - {file}")
    
    print("\n🚀 DEPLOYMENT INSTRUCTIONS:")
    print("1. Copy the zip file to the target PC")
    print("2. Extract all files to a folder")
    print("3. Run start_dashboard.bat (Windows) or start_dashboard.sh (Linux/Mac)")
    print("4. If dependency errors occur, see DEPENDENCY_TROUBLESHOOTING.md")
    print("5. Follow the prompts to configure database connection")
    print("6. Access dashboard at http://localhost:8501")
    
    print(f"\n📚 For detailed instructions, see DEPLOYMENT.md in the package")
    print(f"🔧 For dependency issues, see DEPENDENCY_TROUBLESHOOTING.md in the package")
    
    return zip_path

if __name__ == "__main__":
    try:
        package_path = create_deployment_package()
        print(f"\n✅ Deployment package ready: {package_path.name}")
    except Exception as e:
        print(f"\n❌ Error creating deployment package: {str(e)}")
        exit(1) 