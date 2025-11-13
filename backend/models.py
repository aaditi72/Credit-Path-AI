from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False) # Specify length
    email = Column(String(100), unique=True, index=True, nullable=False) # Specify length, add nullable=False
    password = Column(String(255), nullable=False) # Store hashed password
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False) # Store creation timestamp

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"