# 🔍 PostgreSQL Analytics Dashboard

A powerful Streamlit dashboard that connects to PostgreSQL databases using LangChain SQL agents for natural language querying and data analytics.

## ✨ Features

- **🔒 Read-Only Safety**: All operations are strictly read-only to protect your data
- **💬 Natural Language Queries**: Ask questions in plain English and get SQL results
- **📊 Interactive Visualizations**: Beautiful charts and graphs with Plotly
- **🔄 Real-time Updates**: Auto-refresh capabilities for live data monitoring
- **🧠 Conversation Memory**: Context-aware query generation that builds on previous queries
- **🎛️ Filtering & Controls**: Advanced filtering options for data exploration
- **📈 Analytics Dashboard**: Pre-built dashboard for user prompt usage statistics
- **🛡️ Security First**: Multiple layers of security validation for all queries

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project files
# Navigate to the project directory

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Configuration

Create a `.env` file in the project root:

```env
# PostgreSQL Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password

# Optional: SSL Mode
DB_SSL_MODE=prefer
```

**Note**: Use `env_example.txt` as a template for your `.env` file.

### 3. Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## 📊 Dashboard Components

### Main Analytics Dashboard

- **User Prompt Statistics**: Daily and average prompt usage per user
- **Summary Metrics**: Total users, prompts, and activity statistics
- **Interactive Tables**: Sortable and filterable data views
- **Visual Charts**: Bar charts, distributions, and top user rankings

### Natural Language Chat Interface

Ask questions like:

- "Show me users with more than 100 prompts"
- "What's the average number of prompts per user?"
- "Who are the top 10 most active users?"
- "Find users with email addresses containing 'gmail'"
- "Show me users created in the last month"

### Interactive Features

- **Auto-refresh**: Configurable automatic data updates (30s, 60s, 2min, 5min)
- **Filtering**: Filter data by user, date ranges, and activity levels
- **Export**: Download filtered data as CSV
- **Conversation History**: View previous queries and results

## 🏗️ Architecture

### Modular Design

The application is built with a modular architecture:

```
├── app.py                 # Main Streamlit application
├── database.py           # Database connection and management
├── langchain_agent.py    # LangChain SQL agent with safety features
├── streamlit_ui.py       # Streamlit UI components and dashboard
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### Key Components

1. **DatabaseManager** (`database.py`)

   - Secure PostgreSQL connections using SQLAlchemy
   - Schema introspection and validation
   - Read-only query execution with safety checks

2. **SQLAgent** (`langchain_agent.py`)

   - LangChain-powered natural language to SQL conversion
   - Conversation memory and context awareness
   - Comprehensive safety rules and validation
   - Custom system prompt with database schema integration

3. **DashboardUI** (`streamlit_ui.py`)
   - Modern Streamlit interface with custom CSS
   - Interactive charts using Plotly
   - Real-time chat interface
   - Auto-refresh and filtering capabilities

## 🛡️ Security Features

### Read-Only Operations

- All queries are validated to ensure they contain only read operations
- Forbidden keywords are blocked (INSERT, UPDATE, DELETE, DROP, etc.)
- Query structure validation before execution

### Safety Rules

The system enforces strict safety rules:

- Only SELECT, WITH, and other read operations allowed
- No data modification operations
- No schema changes
- No user/permission changes
- Proper SQL injection prevention

### Query Validation

- Pattern matching for safe query structures
- Table and column existence validation against schema
- Nested aggregate function prevention
- Proper join syntax enforcement

## 📈 Default Analytics Query

The dashboard includes a pre-built analytics query that calculates:

```sql
WITH daily_prompts AS (
  SELECT ph.user_id, DATE_TRUNC('day', ph.created_at) AS prompt_date,
         COUNT(ph.prompt_id) AS prompts_per_day
  FROM prompt_history ph
  WHERE ph.user_id NOT IN (329, 136)
  GROUP BY ph.user_id, DATE_TRUNC('day', ph.created_at)
),
user_avg_prompts AS (
  SELECT dp.user_id, AVG(dp.prompts_per_day) AS avg_prompts_per_day,
         SUM(dp.prompts_per_day) AS total_prompts,
         COUNT(dp.prompt_date) AS total_days
  FROM daily_prompts dp
  GROUP BY dp.user_id
),
user_details AS (
  SELECT u.user_id, u.name, u.email, u.created_at
  FROM usertable u
  WHERE u.user_id NOT IN (329, 136)
)
SELECT
  ud.user_id,
  ud.name,
  ud.email,
  ud.created_at,
  uap.avg_prompts_per_day,
  uap.total_prompts,
  uap.total_days,
  ROUND(uap.total_prompts / 30.0, 2) AS calculated_avg_prompts_per_day
FROM user_details ud
JOIN user_avg_prompts uap ON ud.user_id = uap.user_id
ORDER BY ud.user_id;
```

## 🔧 Configuration Options

### Auto-Refresh Settings

- Enable/disable automatic data refresh
- Configurable intervals: 30s, 60s, 2min, 5min
- Manual refresh button available

### Database Connection

- Configurable connection pooling
- SSL mode options
- Connection timeout settings
- Automatic reconnection handling

### Logging

- Comprehensive logging to `dashboard.log`
- Configurable log levels
- Error tracking and debugging information

## 🎯 Usage Examples

### Basic Questions

```
"Show me all users"
"How many users do we have?"
"What's the total number of prompts?"
```

### Advanced Analytics

```
"Show me users with more than 50 prompts per day on average"
"Find the most active users in the last week"
"What's the distribution of user activity?"
"Show me users created after January 1st, 2024"
```

### Filtering and Sorting

```
"Show me top 20 users by total prompts"
"Find users with gmail email addresses"
"Show me users sorted by creation date"
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**

   - Check `.env` file configuration
   - Verify PostgreSQL server is running
   - Confirm network connectivity
   - Validate credentials

2. **Import Errors**

   - Run `pip install -r requirements.txt`
   - Check Python version compatibility
   - Verify all files are present

3. **Query Execution Errors**
   - Ensure database schema matches expected structure
   - Check table and column names
   - Verify user permissions for read operations

### Debug Mode

Enable debug logging by setting the environment variable:

```bash
export STREAMLIT_LOGGER_LEVEL=debug
```

## 📦 Dependencies

- **streamlit**: Web application framework
- **langchain**: LLM framework for SQL agent
- **psycopg2-binary**: PostgreSQL database adapter
- **sqlalchemy**: SQL toolkit and ORM
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualizations
- **python-dotenv**: Environment variable management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For questions, issues, or feature requests:

1. Check the troubleshooting section above
2. Review the logs in `dashboard.log`
3. Create an issue with detailed information about your problem

## 🔮 Future Enhancements

- **Export Functionality**: CSV/Excel export of query results
- **Advanced Visualizations**: More chart types and customization
- **User Management**: Role-based access control
- **Query History**: Persistent query history and favorites
- **Scheduled Reports**: Automated report generation
- **API Integration**: REST API for programmatic access
