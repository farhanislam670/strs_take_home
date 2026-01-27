from sqlalchemy import create_engine, text
from src.config import get_settings
import os
from dotenv import load_dotenv

load_dotenv()

print("=== Testing PostgreSQL Connection to Supabase ===")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')[:50]}...")
print()

settings = get_settings()

try:
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✅ Connected successfully!")
        print(f"PostgreSQL version: {version[:80]}...")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check your DATABASE_URL in .env")
    print("2. Get it from: Supabase Dashboard → Settings → Database → Connection String")
    print("3. Use the 'Connection Pooling' URI (port 6543)")