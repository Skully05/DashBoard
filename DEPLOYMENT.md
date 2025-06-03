# 🚀 Deployment Guide

This guide will help you deploy the PostgreSQL Analytics Dashboard on another PC.

## 📋 Prerequisites

Before deploying on the target PC, ensure you have:

- Python 3.8 or higher
- Access to your PostgreSQL database
- Network connectivity between the target PC and database server

## 📦 Deployment Steps

### Step 1: Prepare the Project Files

1. **Copy all project files** to the target PC:
   ```
   ├── simple_dashboard.py    # Main dashboard file
   ├── database.py           # Database connection management
   ├── langchain_agent.py    # LangChain SQL agent
   ├── requirements.txt      # Python dependencies
   ├── env_example.txt       # Environment variables template
   ├── README.md            # Documentation
   ├── DEPLOYMENT.md        # This deployment guide
   └── .env                 # Your database configuration (create this)
   ```

### Step 2: Set Up Python Environment

```bash
# Option 1: Using virtual environment (Recommended)
python -m venv dashboard_env
dashboard_env\Scripts\activate  # Windows
# source dashboard_env/bin/activate  # Linux/Mac

# Option 2: Using conda
conda create -n dashboard python=3.9
conda activate dashboard

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Database Connection

1. **Copy the environment template:**

   ```bash
   copy env_example.txt .env  # Windows
   # cp env_example.txt .env    # Linux/Mac
   ```

2. **Edit the `.env` file** with your database credentials:

   ```env
   # PostgreSQL Database Configuration
   DB_HOST=your_database_host    # IP address or hostname
   DB_PORT=5432                  # Database port
   DB_NAME=your_database_name    # Database name
   DB_USER=your_username         # Database username
   DB_PASSWORD=your_password     # Database password

   # Optional: SSL Mode
   DB_SSL_MODE=prefer
   ```

### Step 4: Test Database Connection

Run the connection test script:

```bash
python test_connection.py
```

If successful, you should see:

```
INFO:database:Database engine created successfully
INFO:database:Database connection test successful
✅ Database connection successful!
```

### Step 5: Launch the Dashboard

```bash
streamlit run simple_dashboard.py
```

The dashboard will be available at:

- **Local access:** http://localhost:8501
- **Network access:** http://[PC_IP]:8501

## 🌐 Network Access Configuration

### For Local Network Access

If you want other devices on your network to access the dashboard:

1. **Find your PC's IP address:**

   ```bash
   # Windows
   ipconfig

   # Linux/Mac
   ifconfig
   ```

2. **Run Streamlit with network access:**

   ```bash
   streamlit run simple_dashboard.py --server.address 0.0.0.0
   ```

3. **Configure firewall** (if needed):
   - Windows: Allow port 8501 through Windows Firewall
   - Linux: `sudo ufw allow 8501`

### For Custom Port

To use a different port:

```bash
streamlit run simple_dashboard.py --server.port 8080
```

## 🐳 Docker Deployment (Optional)

If you prefer containerized deployment, create these files:

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "simple_dashboard.py", "--server.address", "0.0.0.0"]
```

### docker-compose.yml

```yaml
version: "3.8"
services:
  dashboard:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DB_HOST=${DB_HOST}
      - DB_PORT=${DB_PORT}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
    restart: unless-stopped
```

### Deploy with Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🔧 Troubleshooting

### Common Issues

1. **Module not found errors:**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Database connection issues:**

   - Check firewall settings on database server
   - Verify network connectivity: `telnet DB_HOST DB_PORT`
   - Ensure PostgreSQL allows remote connections
   - Check `pg_hba.conf` and `postgresql.conf`

3. **Port already in use:**

   ```bash
   streamlit run simple_dashboard.py --server.port 8080
   ```

4. **Permission errors:**
   - Run as administrator (Windows) or with sudo (Linux)
   - Check file permissions

### Database Server Configuration

If connecting to a remote PostgreSQL server, ensure:

1. **postgresql.conf** allows connections:

   ```
   listen_addresses = '*'  # or specific IP
   port = 5432
   ```

2. **pg_hba.conf** allows your client IP:

   ```
   host    all    all    CLIENT_IP/32    md5
   ```

3. **Restart PostgreSQL** after configuration changes

## 📊 Monitoring and Logs

### Application Logs

Check `dashboard.log` for application logs:

```bash
tail -f dashboard.log
```

### System Monitoring

Monitor resource usage:

```bash
# Windows
tasklist | findstr python

# Linux/Mac
htop
ps aux | grep streamlit
```

## 🔄 Auto-Start Configuration

### Windows Service (Advanced)

Create a batch file `start_dashboard.bat`:

```batch
@echo off
cd /d "C:\path\to\your\dashboard"
call dashboard_env\Scripts\activate
streamlit run simple_dashboard.py
pause
```

### Linux Systemd Service

Create `/etc/systemd/system/dashboard.service`:

```ini
[Unit]
Description=PostgreSQL Analytics Dashboard
After=network.target

[Service]
Type=simple
User=dashboard_user
WorkingDirectory=/path/to/dashboard
Environment=PATH=/path/to/dashboard/dashboard_env/bin
ExecStart=/path/to/dashboard/dashboard_env/bin/streamlit run simple_dashboard.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable dashboard.service
sudo systemctl start dashboard.service
```

## ✅ Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] .env file configured with database credentials
- [ ] Database connection tested successfully
- [ ] Streamlit dashboard launches without errors
- [ ] Network access configured (if needed)
- [ ] Firewall rules configured (if needed)
- [ ] Auto-start configured (if needed)

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review application logs in `dashboard.log`
3. Test database connectivity separately
4. Verify all environment variables are set correctly

## 🎯 Next Steps

After successful deployment:

1. Bookmark the dashboard URL
2. Set up regular backups if needed
3. Monitor performance and logs
4. Consider setting up SSL/HTTPS for production use
