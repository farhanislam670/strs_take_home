# 🚀 Setup Instructions

## Prerequisites

- **Python** 3.10 or higher  
- **PostgreSQL** database (or **Supabase** account)  
- **Git**

---

## 1. Clone the Repository

```bash
git clone https://github.com/farhanislam670/strs_take_home
cd strs_take_home
```

---

## 2. Create Virtual Environment

### 🪟 Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### 🐧 Linux / 🍎 Mac
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Copy the example environment file and update it with your credentials:

```bash
cp .env.example .env
```

Then edit `.env`:

```properties
# Database Connection (Port 5432 for direct connection)
DATABASE_URL=postgresql://postgres:your-password@db.your-project.supabase.co:5432/postgres

# Environment
ENVIRONMENT=development
```

### 🔑 Getting Supabase Credentials
1. Go to your **Supabase project dashboard**  
2. Navigate to **Settings → Database** for connection details  
3. Navigate to **Settings → API** for API keys  

---

## 5. Test Database Connection

```bash
python scripts/test_supabase_conn.py
```

**Expected Output:**
```
✅ Connected successfully!
PostgreSQL version: PostgreSQL 15.x ...
```

---

# 💾 Database Setup

## Step 1: Apply Migrations

Create all database tables:

```bash
alembic upgrade head
```

**This creates:**
- `properties` — Main property data  
- `property_amenities` — Amenity details (JSONB)  
- `property_reviews` — Review statistics  
- `investment_scores` — Calculated scores  

---

## Step 2: Seed Data

Load CSV data into the database:

```bash
python scripts/seed_data.py
```

**This will:**
- Read CSV files from `data/raw/`  
- Clean and validate data  
- Insert properties, amenities, and reviews  
- Show progress and summary  

**Expected Output:**
```
📊 Loading data from data/raw...
✓ Loaded Blue Ridge GA: 150 properties
✓ Loaded Bradenton FL: 200 properties
✓ Loaded Indianapolis IN: 180 properties
✅ Data seeding complete!
• Total properties: 530
• Total amenities: 530
• Total reviews: 530
```

---

## Step 3: Calculate Investment Scores

Run the scoring algorithm:

```bash
python scripts/calculate_scores.py
```

**This will:**
- Calculate market benchmarks  
- Score each property (0–100 scale)  
- Store results in `investment_scores` table  
- Flag top opportunities  

**Expected Output:**
```
📊 Calculating market benchmarks...
✓ Benchmarks calculated for 5 bedroom configurations

🏠 Processing 530 properties...
Processed 530/530

✅ Complete!
• Processed: 530
• Created: 530
• Updated: 0
• Errors: 0

🌟 Top Investment Opportunities:
abnb_123... - Score: 92.5 (A+) - Blue Ridge GA
abnb_456... - Score: 89.3 (A) - Bradenton FL
...
```

---

# 🎯 Running the Application

Start the API server:

```bash
uvicorn src.api.main:app --reload
```

**The API will be available at:**
- API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Alternative Docs: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
