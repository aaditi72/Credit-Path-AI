from database import Base, engine
from models import User # Ensure all models you want to create are imported

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully!")