from celery_config import celery_app
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

@celery_app.task
def analyze_stock(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        #hist = stock.history(start=start_date, end=end_date)
        
        # Calculate metrics
        analysis = {
            'current_price': 123.4,
            #'price_change': ((hist['Close'][-1] - hist['Close'][0]) / hist['Close'][0] * 100),
            #'volume': hist['Volume'][-1],
            #'avg_volume': hist['Volume'].mean(),
            #'high_30d': hist['High'].max(),
            #'low_30d': hist['Low'].min(),
            #'moving_avg_7d': hist['Close'].tail(7).mean(),
            #'moving_avg_30d': hist['Close'].mean(),
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
        #hist = stock.history(period='1m')
        #
        ## Calculate RSI
        #delta = hist['Close'].diff()
        #gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        #loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        #rs = gain / loss
        #rsi = 100 - (100 / (1 + rs))
        #
        ## Calculate MACD
        #exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
        #exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
        #macd = exp1 - exp2
        #signal = macd.ewm(span=9, adjust=False).mean()
        
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
