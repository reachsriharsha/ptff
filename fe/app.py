from flask import (
    Flask, 
    render_template, 
    jsonify, 
    request, 
    session, 
    redirect, 
    url_for
)
#from flask_wtf.csrf import CSRFProtect
#ToDo; Use flask log in manager.
import requests
from functools import wraps

import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
#csrf = CSRFProtect(app)

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost/api')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        response = requests.post(
            f"{os.getenv('BACKEND_URL')}/token",
            data={
                "username": request.form['username'],
                "password": request.form['password']
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            session['access_token'] = data['access_token']
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        response = requests.post(
            f"{os.getenv('BACKEND_URL')}/users/",
            json={
                "email": request.form['email'],
                "username": request.form['username'],
                "password": request.form['password']
            }
        )
        
        if response.status_code == 200:
            return redirect(url_for('login'))
        
        return render_template('register.html', error="Registration failed")
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('access_token', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

#create a new route to access tools section
@app.route('/tools') 
def tools():
    return render_template('tools.html')    

@app.route('/get_stock_data/<symbol>')
@login_required
def get_stock_data(symbol):

    response = requests.get(f'{BACKEND_URL}/stock/{symbol}')
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5000)
