from fastapi import (
    FastAPI, 
    HTTPException,
    Depends,
    status
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import yfinance as yf
from tasks import analyze_stock, calculate_technical_indicators
from celery.result import AsyncResult

import logging
from database import get_db, engine
import models, schemas, auth
from datetime import datetime, timedelta


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Create a console handler and set the formatter
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
# Get the root logger and set its level
logger = logging.getLogger()
logger.setLevel(logging.DEBUG) 
# Add the console handler to the logger
logger.addHandler(console_handler)

'''
# Log messages
logger.debug('This is a debug message')
logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
logger.critical('This is a critical message')
'''

# Create tables
models.Base.metadata.create_all(bind=engine)



app = FastAPI()

#@app.get("/api/stock/{symbol}", response_model=StockData)
@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str):
    # Start both tasks asynchronously
    analysis_task = analyze_stock.delay(symbol)
    technical_task = calculate_technical_indicators.delay(symbol)
    
    return {
        "task_ids": {
            "analysis": analysis_task.id,
            "technical": technical_task.id
        }
    }

@app.get("/api/tasks/{task_id}")
async def get_task_result(task_id: str):
    task_result = AsyncResult(task_id)
    
    if task_result.ready():
        if task_result.successful():
            return {"status": "completed", "result": task_result.get()}
        else:
            return {"status": "failed", "error": str(task_result.result)}
    
    return {"status": "pending"}

@app.post("/api/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating user {user}")
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/watchlists/", response_model=schemas.Watchlist)
async def create_watchlist(
    watchlist: schemas.WatchlistCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_watchlist = models.Watchlist(**watchlist.dict(), user_id=current_user.id)
    db.add(db_watchlist)
    db.commit()
    db.refresh(db_watchlist)
    return db_watchlist

@app.get("/api/watchlists/", response_model=List[schemas.Watchlist])
async def get_watchlists(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Watchlist).filter(models.Watchlist.user_id == current_user.id).all()

