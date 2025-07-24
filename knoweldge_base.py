from flask import Flask, redirect, url_for, session, render_template, request
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)

# User model
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nickname = db.Column(db.String(50))
    address = db.Column(db.String(200))

# OAuth setup with Okta
oauth = OAuth(app)
okta = oauth.register(
    name='okta',
    client_id=os.getenv('OKTA_CLIENT_ID'),
    client_secret=os.getenv('OKTA_CLIENT_SECRET'),
    server_metadata_url=f"https://{os.getenv('OKTA_DOMAIN')}/.well-known/openid-configuration",
    client_kwargs={'scope': 'openid profile email'}
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return okta.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = okta.authorize_access_token()
    userinfo = token['userinfo']
    session['user'] = {
        'email': userinfo['email'],
        'name': userinfo['name']
    }

    # Check if user profile exists; if not, create one
    profile = UserProfile.query.filter_by(email=userinfo['email']).first()
    if not profile:
        profile = UserProfile(email=userinfo['email'])
        db.session.add(profile)
        db.session.commit()

    return redirect(url_for('profile'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('index'))

    profile = UserProfile.query.filter_by(email=session['user']['email']).first()

    if request.method == 'POST':
        profile.nickname = request.form['nickname']
        profile.address = request.form['address']
        db.session.commit()

    return render_template('profile.html', profile=profile)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
