from flask import Flask, redirect, url_for, session, render_template, request
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import os

load_dotenv()

# Create the main web app object
app = Flask(__name__)
# Set the secret key for the app (used to keep sessions and cookies safe)
app.secret_key = os.getenv('SECRET_KEY')

# Database setup
# Set up the database connection using a URL from the .env file
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
# Create a database object to use in the app
db = SQLAlchemy(app)

# User model
# This class defines what information we store about each user in the database
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each user
    email = db.Column(db.String(120), unique=True, nullable=False)  # User's email address (must be unique)
    nickname = db.Column(db.String(50))  # User's nickname (optional)
    address = db.Column(db.String(200))  # User's address (optional)

# OAuth setup with Okta
# Set up OAuth (login with Okta) for the app
oauth = OAuth(app)
okta = oauth.register(
    name='okta',  # Name for this login provider
    client_id=os.getenv('OKTA_CLIENT_ID'),  # Okta client ID from .env
    client_secret=os.getenv('OKTA_CLIENT_SECRET'),  # Okta client secret from .env
    server_metadata_url=f"https://{os.getenv('OKTA_DOMAIN')}/.well-known/openid-configuration",  # Okta server info
    client_kwargs={'scope': 'openid profile email'}  # Ask Okta for user's profile and email
)

# Home page route
@app.route('/')
def index():
    # Show the home page (index.html)
    return render_template('index.html')

# Login route
@app.route('/login')
def login():
    # Start the login process with Okta
    redirect_uri = url_for('authorize', _external=True)  # Where Okta should send us back after login
    return okta.authorize_redirect(redirect_uri)

# Authorization callback route
@app.route('/authorize')
def authorize():
    # Handle the response from Okta after login
    token = okta.authorize_access_token()  # Get the login token from Okta
    userinfo = token['userinfo']  # Get user info (like email and name)
    session['user'] = {
        'email': userinfo['email'],  # Save user's email in session
        'name': userinfo['name']     # Save user's name in session
    }

    # Check if user profile exists in the database; if not, create one
    profile = UserProfile.query.filter_by(email=userinfo['email']).first()
    if not profile:
        profile = UserProfile(email=userinfo['email'])  # Create new profile with email
        db.session.add(profile)  # Add to database
        db.session.commit()  # Save changes

    # After login, go to the profile page
    return redirect(url_for('profile'))

# Profile page route (view and update profile)
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # If user is not logged in, send them to the home page
    if 'user' not in session:
        return redirect(url_for('index'))

    # Get the user's profile from the database
    profile = UserProfile.query.filter_by(email=session['user']['email']).first()

    # If the user submits the form to update their profile
    if request.method == 'POST':
        profile.nickname = request.form['nickname']  # Update nickname
        profile.address = request.form['address']    # Update address
        db.session.commit()  # Save changes to database

    # Show the profile page with the user's info
    return render_template('profile.html', profile=profile)

# Logout route
@app.route('/logout')
def logout():
    # Clear the user's session (log them out)
    session.clear()
    return redirect(url_for('index'))  # Go back to home page

# Run the app if this file is executed directly
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True, port=5000)  # Start the web server on port 5000
