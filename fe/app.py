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
import traceback
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
    logger.debug(f"got the login request {request.form.to_dict()}")
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
            session['username'] = request.form['username']
            session['email'] = data['email']
            
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


@app.route('/kb/create', methods=['POST'])
@login_required
def create_kb():
    if request.method == 'POST':
        description = request.form.get('description', 'NA')
        email = session.get('email', 'NA')

        try:
            logger.debug(f"Knowledge base addition details: {request.form.to_dict()}")
            response = requests.post(
                f"{os.getenv('BACKEND_URL')}/kb/add",
                json={
                    "title": request.form['title'],
                    "tag_or_version": request.form['tag_or_version'],
                    "description": description,
                    "email": email
                    #"description": request.form['description'],
                    #"file_name": request.form['file_name'],
                    #"email": request.form['email']
                }
            )
            
            if response.status_code == 200:
                #return redirect(url_for('kb'))
                logger.info(f"Knowledge base entry added successfully: {response.json()}")
                return jsonify({'message': 'Knowledge base entry added successfully'}), 200
            else:
                return jsonify({'error': 'Knowledge base addition failed'}), 400
            
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Knowledge base addition failed: {str(e)}")
            return jsonify({'error': 'Knowledge base addition failed'}), 400
    
    return render_template('kb.html', error="Knowledge base addition failed")


    

@app.route('/kb')
@login_required
def kb():

    email = session.get('email', 'NA')
    data = {
        "email": email
    }
    response = requests.get(f'{os.getenv('BACKEND_URL')}/kb/list', json=data)
    if response.status_code == 200:
        data = response.json()
        title_tags = data.get('title_tags', {})
        corp_actions = data.get('corp_actions', {})
        logger.debug(f"Knowledge base entries: {title_tags} and corp_actions: {corp_actions}")
        return render_template('kb.html', title_tags=title_tags, company_data=corp_actions)

    return render_template('kb.html',title_tags=None, company_data=None)

@app.route('/ca/upload', methods=['POST'])
@login_required
def upload_ca():
    #logger.info(f"Adding knowledge base entry  {request.form}")
    #print(f"======>Adding knowledge base entry {request.form}\n\n\n")

    if 'cafile' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['cafile']
    caName = request.form.get('caName')
    cAction = request.form.get('cAction')
    email = session.get('email', 'NA')

    data = {"caName":caName, "cAction":cAction, "email": email}
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    logger.debug(f"Company Action addition details: {data}")
    
    #FIX ME: Check how to use allowed files only.
    if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            safe_file_path = os.path.join(os.getenv('UPLOAD_FOLDER'), filename)
            file.save(safe_file_path)
            #return jsonify({'message': 'File uploaded successfully'}), 200
            with open(safe_file_path, 'rb') as f:
                #files = {'file': (filename, f, file.content_type)}
                files = {'file':f}

                response = requests.post(f'{os.getenv('BACKEND_URL')}/ca/upload', 
                                         data=data,
                                         files=files
                                         )
                f.close()
                if response.status_code == 200:
                    logger.info(f"Company Action added successfully: {response.json()}")
                    return {
                        "status": "success",
                        "message": f"File '{filename}' uploaded successfully"
                    }
                #response.json()
                else:
                    logger.error(f"Company Action addition failed: {response.json()}")
                    return { "status": "error", "message": "Company Action addition failed" }
                
    return render_template('kb.html', error="Company Action addition failed")


@app.route('/kb/add', methods=['POST'])
@login_required
def add_kb():
    #logger.info(f"Adding knowledge base entry  {request.form}")
    #print(f"======>Adding knowledge base entry {request.form}\n\n\n")

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    title = request.form.get('title')
    tag = request.form.get('tag')
    email = session.get('email', 'NA')

    data = {"title":title, "tag":tag, "email": email}
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    logger.debug(f"Knowledge base addition details: {data}")
    
    #FIX ME: Check how to use allowed files only.
    if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            safe_file_path = os.path.join(os.getenv('UPLOAD_FOLDER'), filename)
            file.save(safe_file_path)
            #return jsonify({'message': 'File uploaded successfully'}), 200
            with open(safe_file_path, 'rb') as f:
                #files = {'file': (filename, f, file.content_type)}
                files = {'file':f}
                '''response = requests.post(f'{os.getenv('BACKEND_URL')}/kb/upload', 
                                         files=files, 
                                         json={"title":title, 
                                               "tag":tag, 
                                               "email": email
                                               }
                                         )
                '''
                response = requests.post(f'{os.getenv('BACKEND_URL')}/kb/upload', 
                                         data=data,
                                         files=files
                                         )
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
                    logger.error(f"Knowledge base addition failed: {response.json()}")
                    return { "status": "error", "message": "Knowledge base addition failed" }
                
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
