from fastapi import (
    FastAPI, 
    HTTPException,
    Depends,
    status,
    File, 
    UploadFile
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import yfinance as yf
from tasks import (
    analyze_stock, 
    calculate_technical_indicators,
    kb_addition,
)
from celery.result import AsyncResult

from database import get_db, engine
import models, schemas, auth, utils
from datetime import datetime, timedelta
from logs import logger  # Import the logger from the logger.py file
from dotenv import load_dotenv
import os
from pathlib import Path
import aiofiles
import traceback

load_dotenv()


# Create tables
models.Base.metadata.create_all(bind=engine)


app = FastAPI(title="Sample Framework to demonstrate the FAST API",
                          description="Sample Framework to demonstrate the FAST API",
                          version="0.1",)

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

@app.post("/api/kb/add")
async def create_knowledge_base_entry(
    kb_create: schemas.KnowledgeBaseCreate,
    db: Session = Depends(get_db)
):
    logger.debug(f"Creating knowledge base entry from input {kb_create}")
    
    
    db_user = db.query(models.User).filter(models.User.email == kb_create.email).first()
    if db_user:

        # Check if the entry already exists
        existing_entry = db.query(models.KnowledgeBaseDB).filter(
            models.KnowledgeBaseDB.title == kb_create.title,
            models.KnowledgeBaseDB.user_id == db_user.id,
            models.KnowledgeBaseDB.tag_or_version == kb_create.tag_or_version
        ).first()

        if existing_entry:
            logger.debug(f"Knowledge base entry already exists {existing_entry}")
            return {'status': 'success',
                    'message': 'Knowledge base entry added successfully'
                }
        
        #create collection name
        collection_name = f"{utils.clense_name(kb_create.title)}_kb"
        db_knowledge_base = models.KnowledgeBaseDB(
            title=kb_create.title,
            tag_or_version=kb_create.tag_or_version,
            description=kb_create.description,
            collection_name=collection_name,
            user_id=db_user.id)
        logger.debug(f"Creating knowledge base entry {db_knowledge_base}")
        db.add(db_knowledge_base)
        db.commit()
        db.refresh(db_knowledge_base)

        #FIX ME: Return proper http code etc..
        #return db_knowledge_base
        return {'status': 'success',
                 'message': 'Knowledge base entry added successfully'
                }
    else:
        raise HTTPException(status_code=404, detail="User not found")
    

@app.post("/api/kb/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Create safe filename and path
        file_location = os.path.join(os.environ.get('UPLOADS_DIR'), f"{utils.gen_random_string()}_{file.filename}")

        logger.debug(f"File :{file_location} started uploading... original name:{file.filename}")

        #file_location = os.environ.get('UPLOADS') / file.filename
        # Read the file in chunks and write asynchronously
        async with aiofiles.open(file_location, 'wb') as out_file:
            # Read and write the file in chunks of 1MB
            #chunk_size = 1024 * 1024  # 1MB chunks
            chunk_size = 8192 # take a sip of 8KB
            while content := await file.read(chunk_size):
                await out_file.write(content)
        # Get file size for confirmation
        file_size = os.path.getsize(file_location)

        '''
        kb_addition.delay(
            kb_create.title, 
            kb_create.description, 
            collection_name, 
            db_user.id
        )'''

    
        return {
            "filename": file.filename,
            "size": file_size,
            "status": "success",
            "message": f"File '{file.filename}' uploaded successfully ({file_size} bytes)"
        }
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error uploading file:{file.filename}  {e}")
        return {
            "status": "error",
            "message": "File Upload Error"
        }

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
        data={'sub': user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, 
            "token_type": "bearer", 
            'email': user.email
            }

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

