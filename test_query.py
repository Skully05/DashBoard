#!/usr/bin/env python3
"""
Test script to debug the analytics query
"""

from database import db_manager

def test_analytics_query():
    """Test the specific analytics query step by step."""
    print("🔍 Testing Analytics Query Step by Step")
    print("=" * 50)
    
    # Test 1: Basic table access
    print("1. Testing basic table access...")
    try:
        result = db_manager.execute_query("SELECT COUNT(*) FROM prompt_history")
        print(f"   ✅ prompt_history: {result.iloc[0,0]} records")
    except Exception as e:
        print(f"   ❌ prompt_history failed: {e}")
        return False
    
    try:
        result = db_manager.execute_query("SELECT COUNT(*) FROM usertable")
        print(f"   ✅ usertable: {result.iloc[0,0]} records")
    except Exception as e:
        print(f"   ❌ usertable failed: {e}")
        return False
    
    # Test 2: DATE_TRUNC function
    print("\n2. Testing DATE_TRUNC function...")
    try:
        result = db_manager.execute_query("""
            SELECT DATE_TRUNC('day', created_at) AS prompt_date, COUNT(*)
            FROM prompt_history 
            GROUP BY DATE_TRUNC('day', created_at)
            LIMIT 5
        """)
        print(f"   ✅ DATE_TRUNC works: {len(result)} rows")
    except Exception as e:
        print(f"   ❌ DATE_TRUNC failed: {e}")
        return False
    
    # Test 3: Simple CTE
    print("\n3. Testing simple CTE...")
    try:
        result = db_manager.execute_query("""
            WITH test_cte AS (
                SELECT user_id, COUNT(*) as count
                FROM prompt_history
                GROUP BY user_id
                LIMIT 10
            )
            SELECT * FROM test_cte
        """)
        print(f"   ✅ Simple CTE works: {len(result)} rows")
    except Exception as e:
        print(f"   ❌ Simple CTE failed: {e}")
        return False
    
    # Test 4: Full analytics query
    print("\n4. Testing full analytics query...")
    try:
        query = """
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
        ORDER BY uap.total_prompts DESC
        LIMIT 10
        """
        
        result = db_manager.execute_query(query)
        print(f"   ✅ Full analytics query works: {len(result)} rows")
        
        if len(result) > 0:
            print("\n📊 Sample Results:")
            print(result[['user_id', 'name', 'total_prompts', 'avg_prompts_per_day']].head(3).to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"   ❌ Full analytics query failed: {e}")
        return False

if __name__ == "__main__":
    success = test_analytics_query()
    if success:
        print("\n🎉 All tests passed! Analytics query is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the errors above.") 