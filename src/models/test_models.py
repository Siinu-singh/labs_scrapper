from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Numeric, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Test(Base):
    __tablename__ = "tests"
    
    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String(255), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    prices = relationship("TestPrice", back_populates="test", cascade="all, delete-orphan")

class TestPrice(Base):
    __tablename__ = "test_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False, index=True)
    lab_name = Column(String(50), nullable=False, index=True)
    price = Column(Numeric(10, 2))
    matched_test_name = Column(String(255))
    match_score = Column(Float)
    is_available = Column(Boolean, default=True)
    scraped_at = Column(DateTime)
    is_latest = Column(Boolean, default=True, index=True)
    
    test = relationship("Test", back_populates="prices")
