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
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from logs import logger  # Import the logger from the logger.py file

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

#csrf = CSRFProtect(app)
#BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost/api')
BACKEND_URL = os.environ.get('BACKEND_URL')


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


@app.route('/kb')
@login_required
def kb():
    return render_template('kb.html')



@app.route('/kb/add', methods=['POST'])
@login_required
def add_kb():
    #logger.info(f"Adding knowledge base entry  {request.form}")
    #print(f"======>Adding knowledge base entry {request.form}\n\n\n")

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            safe_file_path = os.path.join(os.getenv('UPLOAD_FOLDER'), filename)
            file.save(safe_file_path)
            #return jsonify({'message': 'File uploaded successfully'}), 200
            with open(safe_file_path, 'rb') as f:
                #files = {'file': (filename, f, file.content_type)}
                files = {'file':f}
                response = requests.post(f'{os.getenv('BACKEND_URL')}/kb/upload', files=files)
                f.close()
                if response.status_code == 200:
                    logger.info(f"Knowledge base entry added successfully: {response.json()}")
                    #return redirect(url_for('kb'))
                    #return render_template('kb.html', message="Knowledge base addition successful")
                    return {
                        "status": "success",
                        "message": f"File '{filename}' uploaded successfully"
                    }
                #response.json()
                else:
                    return { "status": "error", "message": "Knowledge base addition failed" }
                
    

    
    
    #with open(os.path.join("tempDir", file.filename), 'wb') as f:
    #    f.write(file.get_buffer())    
    #    f.close()
#
    #with open(os.path.join("tempDir", file.filename), 'rb') as f:
    #    files = {'file': (file.filename, f, file.content_type)}
    #    response = requests.post(f'{os.getenv('BACKEND_URL')}/kb/upload', files=files)
    #    f.close()
    
    #files = {'file': (file.filename, file.stream, file.content_type)}
    #response = requests.post(f'{os.getenv('BACKEND_URL')}/kb/upload', files=files)

    #response = requests.post(
    #    f"{os.getenv('BACKEND_URL')}/kb/upload",
    #    json={
    #        "title": request.form['title'],
    #        "description": request.form['description'],
    #        "collection_name": request.form['collection_name'],
    #        "tag_or_version": request.form['tag_or_version'],
    #        "file_name": request.form['file_name'],
    #        "user_id": 1
    #    }
    #)
    
    #if response.status_code == 200:
    #    return redirect(url_for('kb'))
    
    return render_template('kb.html', error="Knowledge base addition failed")

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
