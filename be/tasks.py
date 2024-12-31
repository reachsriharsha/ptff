from celery_config import celery_app
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from synapse import Synapse

@celery_app.task
def analyze_stock(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Calculate metrics
        analysis = {
            'current_price': 123.4,
        
        }
        
        return {
            'status': 'completed',
            'data': analysis
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

@celery_app.task
def calculate_technical_indicators(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        
        return {
            'status': 'completed',
            'data': {
                'rsi': 123.4,
                #'macd': macd.iloc[-1],
                #'macd_signal': signal.iloc[-1],
                #'trend': 'bullish' if macd.iloc[-1] > signal.iloc[-1] else 'bearish'
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


@celery_app.task
def kb_addition(title: str, 
                description: str, 
                collection_name: str, 
                tag_or_version:str, 
                file_name: str,
                user_id: int):
    try:
        #create new synapse layer to do all jobs
        synapse = Synapse()
        synapse.ingest_data_to_vector_db(source=file_name, 
                                         title=title, 
                                         description=description, 
                                         collection_name=collection_name, 
                                         metadata=tag_or_version,
                                         user_id=user_id)   

        
        return {
            'status': 'completed',
            'message': 'Knowledge base record added successfully'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }