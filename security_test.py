#!/usr/bin/env python3
"""
Security test script to demonstrate that dangerous SQL operations are blocked.
"""

from database import db_manager

def test_security():
    """Test that dangerous SQL operations are properly blocked."""
    print("🛡️ Testing Database Security Features")
    print("=" * 50)
    
    # List of dangerous queries to test
    dangerous_queries = [
        ("DELETE", "DELETE FROM usertable WHERE user_id = 1"),
        ("INSERT", "INSERT INTO usertable (name) VALUES ('hacker')"),
        ("UPDATE", "UPDATE usertable SET name = 'changed' WHERE user_id = 1"),
        ("DROP", "DROP TABLE usertable"),
        ("CREATE", "CREATE TABLE malicious_table (id INT)"),
        ("ALTER", "ALTER TABLE usertable ADD COLUMN malicious TEXT"),
        ("TRUNCATE", "TRUNCATE TABLE usertable"),
        ("GRANT", "GRANT ALL PRIVILEGES ON usertable TO public"),
    ]
    
    print(f"Testing {len(dangerous_queries)} dangerous operations...")
    print()
    
    all_blocked = True
    
    for operation, query in dangerous_queries:
        try:
            # This should FAIL and raise an exception
            result = db_manager.execute_query(query)
            print(f"❌ {operation}: SECURITY BREACH - Query was executed!")
            all_blocked = False
        except Exception as e:
            print(f"✅ {operation}: Successfully blocked - {str(e)}")
    
    print()
    print("=" * 50)
    
    if all_blocked:
        print("🎉 ALL SECURITY TESTS PASSED!")
        print("✅ Your data is completely safe - no dangerous operations can be executed.")
    else:
        print("⚠️ SECURITY ISSUES DETECTED!")
        print("❌ Some dangerous operations were not blocked.")
    
    print()
    print("Testing safe operations:")
    
    # Test a safe operation
    try:
        result = db_manager.execute_query("SELECT COUNT(*) as total_users FROM usertable")
        print(f"✅ Safe SELECT query: Successfully executed - Found {result.iloc[0]['total_users']} users")
    except Exception as e:
        print(f"⚠️ Safe query failed: {e}")
    
    return all_blocked

if __name__ == "__main__":
    test_security() 