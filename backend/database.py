from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# ⚙️ Update credentials as needed, ideally from environment variables
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "NCT127@dream")
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = os.getenv("MYSQL_PORT", 3306)
MYSQL_DB = os.getenv("MYSQL_DB", "creditpath_ai")

# Construct DATABASE_URL using f-strings for clarity and security (if escaping needed)
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:pOkpywahgINwwPTDtBgmexKHMMkQuYxl@metro.proxy.rlwy.net:17009/railway")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


