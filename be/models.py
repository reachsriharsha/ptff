from pydantic import BaseModel
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Float, 
    DateTime, 
    ForeignKey, 
    Boolean,
    Index,
    func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    relationship,
    Session
)
from typing import List, Optional

from datetime import datetime

Base = declarative_base()

class StockData(BaseModel):
    symbol: str
    price: float
    change: float
    volume: int

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    watchlists = relationship("Watchlist", back_populates="user")
    stock_alerts = relationship("StockAlert", back_populates="user")
    knowledge_base = relationship("KnowledgeBaseDB", back_populates="user")


class KnowledgeBaseDB(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    collection_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="knowledge_base")



class Watchlist(Base):
    __tablename__ = "watchlists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    stocks = Column(String)  # Comma-separated stock symbols
    user = relationship("User", back_populates="watchlists")

class StockAlert(Base):
    __tablename__ = "stock_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String)
    price_threshold = Column(Float)
    is_above = Column(Boolean)  # True if alert when price goes above threshold
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="stock_alerts")

###
#SqlAlchemy Model for Equity. This is to create database table for storing equity information
class EquityDB(Base):
    __tablename__ = "equities_info"

    id = Column(Integer, primary_key=True, index=True)
    isin_no = Column(String)
    bse_security_code = Column(String)
    bse_security_id = Column(String)
    nse_symbol = Column(String)
    date_of_listing = Column(String)
    name_of_company = Column(String, index=True)
    industry = Column(String)
    sector = Column(String)
    vector_collection_name = Column(String)
    vector_collection_desc = Column(String)
    from_exchange = Column(String)
    comments = Column(String)

    '''
    # Create a GIN index for full-text search
    __table_args__ = ({
        'postgresql_using': 'gin',
        'postgresql_ops': {
            'name_of_company': 'gin_trgm_ops'
        }
    },)
    
    __table_args__ = (
        Index('my_index', "name_of_company", "bse_security_code", "bse_security_id", "nse_symbol", postgresql_using="gin"), 
    )'''

# Pydantic models for the EquityDB
class EquityBase(BaseModel):
    isin_no: str
    bse_security_code: str
    bse_security_id: str
    nse_symbol: str
    date_of_listing: str
    name_of_company: str
    industry: str
    sector: str
    vector_collection_name: str
    vector_collection_desc: str
    from_exchange: str
    comments: str

class EquityCreate(EquityBase):
    pass

class Equity(EquityBase):
    id: int

    class Config:
        #orm_mode = True
        from_attributes = True

# CRUD operations for Equity
class EquityRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_Equity(self, equity: EquityCreate) -> Equity:
        db_equity = EquityDB(**equity.dict())
        self.db.add(db_equity)
        self.db.commit()
        self.db.refresh(db_equity)
        return Equity.from_orm(db_equity)
    
    def search_equity(self, query: str, limit: int = 10) -> List[Equity]:
        # Create a full-text search query using to_tsquery
        search_query = func.plainto_tsquery('english', query)
        
        # Search in both title and content using to_tsvector
        results = self.db.query(EquityDB).filter(
            func.to_tsvector('english', EquityDB.name_of_company + ' ' + EquityDB.bse_security_code + ' ' + EquityDB.bse_security_id + ' ' + EquityDB.nse_symbol + ' ' + EquityDB.isin_no).match(search_query)
            
        ).limit(limit).all()
        
        return [Equity.from_orm(article) for article in results]