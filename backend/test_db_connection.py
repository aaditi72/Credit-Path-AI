from sqlalchemy import create_engine

DATABASE_URL = "mysql+pymysql://root:pOkpywahgINwwPTDtBgmexKHMMkQuYxl@metro.proxy.rlwy.net:17009/railway"
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        print("✅ Connected successfully to Railway MySQL!")
except Exception as e:
    print("❌ Connection failed:", e)
