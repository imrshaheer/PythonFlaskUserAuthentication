from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import json
import secrets
import os

# Application Setup
app = Flask(__name__)

# Load configuration parameters from a JSON file
with open('config.json', 'r') as c:
    params = json.load(c)['params']

# Set database URI based on the server type
LOCAL_SERVER = params['local_server']
app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri'] if LOCAL_SERVER else params['production_uri']

# Set a secret key for session management securely
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(16))

# Initialize the database
db = SQLAlchemy(app)

# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(80), nullable=False)
    lastName = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    # Check if user is logged in
    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        password = request.form['password']
        repeatPassword = request.form['repeatPassword']

        # Check if passwords match
        if password == repeatPassword:
            # Create a new user and save to the database
            userinfo = User(firstName=fname, lastName=lname, email=email, password=password)
            db.session.add(userinfo)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            # Redirect back to registration page if passwords do not match
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        password = request.form['password']

        # Query the user by email
        user = User.query.filter_by(email=email).first()

        # Check if user exists and password matches
        if user and user.password == password:
            session['user'] = user.id
            return redirect(url_for('index'))
        else:
            # Show error if email or password do not match
            flash('Email or Passwords do not match. Please try again.', 'error')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Remove user from session
    session.pop('user', None)
    return redirect(url_for('login'))

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
