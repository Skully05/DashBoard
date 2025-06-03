"""
LangChain SQL Agent for PostgreSQL with conversation memory and read-only operations.
"""

import logging
from typing import Dict, List, Any, Optional
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.prompts import PromptTemplate
import pandas as pd
from database import db_manager
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockLLM(LLM):
    """Mock LLM for testing purposes when no real LLM is available."""
    
    @property
    def _llm_type(self) -> str:
        return "mock"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        # Simple mock response for testing
        if "SELECT" in prompt.upper():
            return "SELECT * FROM usertable LIMIT 5;"
        return "I can help you query the database. Please ask a specific question about the data."


class SQLAgent:
    """Custom SQL Agent with read-only operations and conversation memory."""
    
    def __init__(self, llm: Optional[LLM] = None):
        """
        Initialize SQL Agent with database connection and LLM.
        
        Args:
            llm: Language model instance (optional, will use mock if not provided)
        """
        self.db_manager = db_manager
        self.llm = llm or MockLLM()
        self.conversation_history: List[Dict[str, str]] = []
        
        # Initialize database connection
        try:
            engine = self.db_manager.get_engine()
            self.sql_database = SQLDatabase(engine=engine)
            logger.info("SQL Database connection established")
        except Exception as e:
            logger.error(f"Failed to initialize SQL database: {e}")
            raise
        
        # Get database schema
        self.schema_string = self.db_manager.get_schema_string()
        
        # Initialize conversation memory
        self.memory = ConversationBufferWindowMemory(
            k=5,  # Keep last 5 exchanges
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Custom system prompt
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Get the custom system prompt with safety rules and schema information."""
        return f"""You are a PostgreSQL expert operating in READ-ONLY mode for data analytics with conversation memory.
            
            CONVERSATION CONTEXT:
            {{context}}
            
            CRITICAL SAFETY RULES - MUST FOLLOW:
            ================================
            - You are in READ-ONLY mode
            - ONLY use read-only operations (SELECT, WITH, etc.)
            - NEVER use: INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, TRUNCATE, GRANT, REVOKE
            - NO data modification operations allowed
            - NO schema changes allowed
            - NO user/permission changes allowed

            PERFORMANCE OPTIMIZATION RULES:
            - Use appropriate indexes
            - Implement proper filtering
            - Use LIMIT for large result sets
            - Optimize subqueries
            
            CONTEXT-AWARE QUERY GENERATION:
            ===============================
            - Consider previous queries and results when generating new queries
            - Build upon previous analysis and findings
            - Reference earlier results when relevant
            - Avoid redundant queries if similar data was recently retrieved
            - Suggest follow-up analysis based on conversation history
            
            ALLOWED OPERATIONS:
            =====================
            - SELECT with WHERE, HAVING, ORDER BY, GROUP BY
            - JOIN operations (INNER, LEFT, RIGHT, FULL OUTER)
            - Aggregate functions (COUNT, SUM, AVG, MIN, MAX)
            - Window functions (RANK, ROW_NUMBER, LAG, LEAD, PARTITION BY)
            - DISTINCT, LIMIT, OFFSET
            - Subqueries and Common Table Expressions (CTEs)
            - Date/Time functions (NOW(), DATE_TRUNC, EXTRACT, etc.)
            - Mathematical calculations and operators
            - CASE statements for conditional logic
            - String functions (CONCAT, SUBSTRING, UPPER, LOWER, etc.)
            - Conditional logic (COALESCE, NULLIF, etc.)
            
            PATTERN MATCHING OPERATORS (LIKE vs ILIKE):
            ==========================================
            - **ILIKE** (default): Case-insensitive matching for user searches (names, descriptions, general text)
              Example: WHERE name ILIKE 'john%' (matches "John", "JOHN", "johnny")
            - **LIKE**: Case-sensitive matching for exact codes, IDs, technical identifiers
              Example: WHERE user_id LIKE 'USER_%' (exact case matching)
            - **Syntax**: Always use single quotes: 'pattern%', '%text%', 'te_t' (% = wildcard, _ = single char)
            - **SQLAlchemy Safe**: Use direct strings only: column ILIKE 'pattern%'
            - **NEVER use**: Parameterized patterns (%s, %(name)s, ?) - causes immutabledict errors
            - **DEFAULT**: Use ILIKE for text searches unless case sensitivity explicitly required
            
            CRITICAL SQL SYNTAX RULES:
            =========================
            - NEVER nest aggregate functions (e.g., AVG(COUNT(...)) is INVALID)
            - Use subqueries or CTEs instead of nested aggregates
            - For calculations involving aggregates, use two-step approach:
              1. First query: Calculate the aggregate per group
              2. Second query or CTE: Calculate the final result
            - Example: Instead of AVG(COUNT(id)), use:
              WITH counts AS (SELECT group_col, COUNT(id) as cnt FROM table GROUP BY group_col)
              SELECT AVG(cnt) FROM counts
            - ALWAYS use table aliases in JOIN operations to avoid ambiguous column errors
            - ALWAYS qualify column names with table aliases when multiple tables are involved
            - Example: SELECT t1.user_id, t2.name FROM table1 t1 JOIN table2 t2 ON t1.id = t2.id
            - When both tables have the same column name, specify which table: table1.column_name
            
            Database Schema:
            {self.schema_string}
            
            QUERY GENERATION RULES:
            ======================
            1. Generate ONLY read-only queries (can start with SELECT, WITH, etc.)
            2. Use proper PostgreSQL syntax
            3. Be precise with column names and table names from the schema 
            4. Include only the SQL query in your response, no explanations
            5. Handle NULL values appropriately
            6. Use proper date formatting for PostgreSQL
            7. Validate that all referenced tables and columns exist in the schema
            8. If unsure about a query, default to a safer, simpler approach
            9. NEVER use nested aggregate functions - use CTEs or subqueries instead
            10. **PATTERN MATCHING**: Use ILIKE for case-insensitive text searches (default), LIKE only for case-sensitive searches
            11. **ALWAYS use single quotes** around LIKE/ILIKE patterns: column ILIKE 'pattern%'
            12. **NO parameterized patterns** - embed patterns directly in SQL string
            13. **USE CONVERSATION CONTEXT** to build upon previous queries and avoid redundancy

            COMPLEX QUERY HANDLING RULES:
            ===========================
            1. For analytical queries:
            - Use Common Table Expressions (CTEs) to break down complex logic
            - Implement proper window functions (RANK, ROW_NUMBER, LAG, LEAD)
            - Use appropriate date/time calculations
            - Handle NULL values with COALESCE or NULLIF
            - Use proper data type casting
            - Implement ROUND() for decimal results
            
            2. For aggregations:
            - Use subqueries and derived tables
            - Implement proper GROUP BY clauses
            - Use appropriate aggregate functions
            - Handle NULL values in aggregations
            - NEVER nest aggregates - use step-by-step approach with CTEs
            
            3. For average calculations on grouped data:
            - Step 1: Create CTE to calculate counts/sums per group
            - Step 2: Calculate average from the CTE results
            - Example pattern:
              WITH group_stats AS (
                SELECT group_col, COUNT(*) as count_per_group 
                FROM table 
                GROUP BY group_col
              )
              SELECT AVG(count_per_group) FROM group_stats
            
            4. For date/time calculations:
            - Use DATE_TRUNC for time-based grouping
            - Implement proper interval calculations
            - Handle timezone considerations
            - Use appropriate date formatting
            
            5. For complex joins:
            - Use appropriate join types
            - Handle NULL values in joins
            - Implement proper join conditions
            - ALWAYS use table aliases for clarity (e.g., t1, t2, ph, od)
            - ALWAYS qualify column names with table aliases to avoid ambiguous references
            - Example: FROM prompt_history ph JOIN onboarding_data od ON ph.user_id = od.user_id
            - SELECT qualified columns: SELECT ph.user_id, ph.created_at, od.occupation
                      
            PATTERN MATCHING EXAMPLES:
            ✅ CORRECT: WHERE name ILIKE 'john%', WHERE email ILIKE '%gmail.com', WHERE user_id LIKE 'USER_%'
            ❌ INCORRECT: WHERE name ILIKE %s, WHERE name ILIKE %(pattern)s (causes SQLAlchemy errors)
                      
            SECURITY VALIDATION:
            ===================
            Before generating any query, verify:
            - Query starts with read-only operations (SELECT, WITH, etc.)
            - No modification keywords present
            - All tables/columns exist in provided schema
            - Query follows PostgreSQL best practices
            - No nested aggregate functions are used
                   
            Question: {{question}}
            
            Generate a safe, read-only PostgreSQL SELECT query considering the conversation context:"""
    
    def _format_conversation_context(self) -> str:
        """Format conversation history for context."""
        if not self.conversation_history:
            return "No previous conversation."
        
        context_parts = []
        for i, exchange in enumerate(self.conversation_history[-3:], 1):  # Last 3 exchanges
            context_parts.append(f"Exchange {i}:")
            context_parts.append(f"  User: {exchange['question']}")
            context_parts.append(f"  Assistant: {exchange['response'][:200]}...")  # Truncate long responses
        
        return "\n".join(context_parts)
    
    def generate_sql_query(self, question: str) -> str:
        """
        Generate SQL query from natural language question.
        
        Args:
            question: Natural language question about the data
            
        Returns:
            Generated SQL query string
        """
        context = self._format_conversation_context()
        
        # Format the prompt with context and question
        formatted_prompt = self.system_prompt.format(
            context=context,
            question=question
        )
        
        try:
            # Use LLM to generate SQL query
            response = self.llm(formatted_prompt)
            
            # Extract SQL query from response (simple extraction)
            query = self._extract_sql_from_response(response)
            
            # Validate query safety
            self._validate_query_safety(query)
            
            logger.info(f"Generated SQL query: {query[:100]}...")
            return query
            
        except Exception as e:
            logger.error(f"Failed to generate SQL query: {e}")
            raise
    
    def _extract_sql_from_response(self, response: str) -> str:
        """Extract SQL query from LLM response."""
        # Simple extraction - look for SQL patterns
        lines = response.strip().split('\n')
        
        # Find lines that look like SQL
        sql_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and (
                stripped.upper().startswith(('SELECT', 'WITH', 'FROM', 'WHERE', 'GROUP', 'ORDER', 'HAVING')) or
                any(keyword in stripped.upper() for keyword in ['SELECT', 'FROM', 'WHERE', 'JOIN'])
            ):
                sql_lines.append(stripped)
        
        if sql_lines:
            return ' '.join(sql_lines)
        
        # Fallback: return the response as-is if no SQL pattern found
        return response.strip()
    
    def _validate_query_safety(self, query: str):
        """Validate that the query is safe (read-only)."""
        query_upper = query.upper().strip()
        
        # Use word boundaries to match complete keywords only
        forbidden_patterns = [
            r'\bINSERT\b', r'\bUPDATE\b', r'\bDELETE\b', r'\bDROP\b', 
            r'\bCREATE\b', r'\bALTER\b', r'\bTRUNCATE\b', r'\bGRANT\b', 
            r'\bREVOKE\b', r'\bEXEC\b', r'\bEXECUTE\b'
        ]
        
        for pattern in forbidden_patterns:
            if re.search(pattern, query_upper):
                keyword = pattern.replace(r'\b', '').replace('\\', '')
                raise ValueError(f"Query contains forbidden keyword: {keyword}")
        
        # Ensure query starts with allowed operations
        allowed_starts = ['SELECT', 'WITH']
        if not any(query_upper.startswith(start) for start in allowed_starts):
            raise ValueError("Query must start with SELECT or WITH")
    
    def execute_query_with_context(self, question: str) -> pd.DataFrame:
        """
        Execute natural language question as SQL query with conversation context.
        
        Args:
            question: Natural language question
            
        Returns:
            DataFrame with query results
        """
        try:
            # Generate SQL query
            sql_query = self.generate_sql_query(question)
            
            # Execute query
            result_df = self.db_manager.execute_query(sql_query)
            
            # Store in conversation history
            self.conversation_history.append({
                'question': question,
                'sql_query': sql_query,
                'response': f"Query executed successfully, returned {len(result_df)} rows",
                'result_count': len(result_df)
            })
            
            # Update memory
            self.memory.chat_memory.add_user_message(question)
            self.memory.chat_memory.add_ai_message(f"Executed query: {sql_query}")
            
            return result_df
            
        except Exception as e:
            error_msg = f"Failed to execute query: {str(e)}"
            logger.error(error_msg)
            
            # Store error in conversation history
            self.conversation_history.append({
                'question': question,
                'sql_query': '',
                'response': error_msg,
                'result_count': 0
            })
            
            raise
    
    def get_default_query_results(self) -> pd.DataFrame:
        """Execute the default prompt usage stats query."""
        default_query = """
        WITH daily_prompts AS (
            SELECT ph.user_id, DATE_TRUNC('day', ph.created_at) AS prompt_date, COUNT(ph.prompt_id) AS prompts_per_day
            FROM prompt_history ph
            WHERE ph.user_id NOT IN (329, 136)
            GROUP BY ph.user_id, DATE_TRUNC('day', ph.created_at)
        ),
        user_avg_prompts AS (
            SELECT dp.user_id, AVG(dp.prompts_per_day) AS avg_prompts_per_day, SUM(dp.prompts_per_day) AS total_prompts, COUNT(dp.prompt_date) AS total_days
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
        """
        
        return self.db_manager.execute_query(default_query)
    
    def clear_conversation_history(self):
        """Clear conversation history and memory."""
        self.conversation_history.clear()
        self.memory.clear()
        logger.info("Conversation history cleared")


# Global SQL agent instance (will be initialized when needed)
sql_agent: Optional[SQLAgent] = None


def get_sql_agent(llm: Optional[LLM] = None) -> SQLAgent:
    """Get or create SQL agent instance."""
    global sql_agent
    if sql_agent is None:
        sql_agent = SQLAgent(llm)
    return sql_agent 