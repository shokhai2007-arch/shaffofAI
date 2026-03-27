from sqlalchemy import Boolean, Column, Float, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Tender(Base):
    __tablename__ = "tenders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lot_id = Column(String, unique=True, index=True)  # lot_display_no
    name = Column(String, index=True)  # product_name yoki category_name
    org = Column(String)  # customer_name
    region = Column(String)  # customer_region_name yoki customer_region
    sector = Column(String)  # category_name
    date = Column(DateTime)  # deal_date
    amount = Column(Float)  # deal_cost
    
    # Sun'iy ko'rsatkichlar (Mock / Generated fields)
    marketAvg = Column(Float, nullable=True)
    companyAgeMonths = Column(Integer, nullable=True)
    sameAddress = Column(Boolean, default=False)
    
    # Hisoblanuvchi Risk Fields
    score = Column(Integer, default=0)
    riskLevel = Column(String, default="low") # low, medium, high
    riskLabel = Column(String, default="Xavfsiz")
    riskColor = Column(String, default="#4caf50")
    factors = Column(String, nullable=True) # JSON string sifatida saqlaymiz

    # Qatnashchilar (One-to-many relatsiya)
    participants = relationship("Participant", back_populates="tender", cascade="all, delete-orphan")

class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"))
    name = Column(String) # provider_name
    inn = Column(String, index=True) # provider_inn (bazada qoladi)
    role = Column(String) # G'olib yoki Ishtirokchi
    
    # Yangi Frontend Maydonlari
    type = Column(String, default="company")
    director = Column(String, nullable=True)
    address = Column(String, nullable=True)
    ageMonths = Column(Integer, nullable=True)

    tender = relationship("Tender", back_populates="participants")
