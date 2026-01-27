from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

print("=== Environment Variables ===")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_KEY: {os.getenv('SUPABASE_KEY')[:20]}..." if os.getenv('SUPABASE_KEY') else "SUPABASE_KEY: None")
print()

# Test Supabase connection
try:
    from supabase import create_client
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env file")
        exit(1)
    
    print(f"Connecting to: {supabase_url}")
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Test connection by checking if we can access the API
    print("✅ Supabase client created successfully!")
    
    # Try a simple operation (list tables or query)
    # This will fail if tables don't exist yet, but confirms connection works
    try:
        response = supabase.table('properties').select("*").limit(1).execute()
        print(f"✅ Successfully connected to database!")
        print(f"Found {len(response.data)} properties (table exists)")
    except Exception as e:
        if "relation" in str(e) or "does not exist" in str(e):
            print("✅ Connection works! (Tables not created yet - that's OK)")
        else:
            print(f"⚠️  Connection works, but query failed: {e}")
    
except ImportError:
    print("❌ supabase-py not installed. Run: pip install supabase")
except Exception as e:
    print(f"❌ Connection failed: {e}")