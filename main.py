from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors
import re


app = Flask(__name__)


app.secret_key = 'INTERNSHIPP'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sachin@123'
app.config['MYSQL_DB'] = 'pythonlogin'

mysql = MySQL(app)

# http://localhost:5000/pythonlogin/ - this will be the login page
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    
    msg = ''
    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s ', (username,))
        account = cursor.fetchone()

        if account and check_password_hash(account['password'],password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'

    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    
    return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/home - this will be the home page
@app.route('/pythonlogin/home')
def home():  
    if 'loggedin' in session: 
        return render_template('home.html', username=session['username'])
    
    return redirect(url_for('login'))

@app.route('/pythonlogin/add',  methods=['GET', 'POST'])
def add():
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'web' in request.form:
        username = request.form['username']
        password = request.form['password']
        web = request.form['web']
        if 'loggedin' in session:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO sites VALUES (%s, %s, %s, %s)', (session['id'],username, password,web,))
            mysql.connection.commit()
            msg = 'You have successfully added!'

    return render_template('add.html', msg=msg)


# http://localhost:5000/pythinlogin/profile - only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM sites WHERE id = %s', (session['id'],))
        account = cursor.fetchall()
        return render_template('profile.html', account=account,username=session['username'])
   
    return redirect(url_for('login'))