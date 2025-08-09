from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from flask_sqlalchemy import SQLAlchemy
import os
import datetime

app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Database configuration
if os.environ.get('DATABASE_URL'):
    # Production database (Render)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # Local development - fallback to SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(80), primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    school_name = db.Column(db.String(120))
    class_level = db.Column(db.String(20))  # renamed from 'class' as it's a Python keyword
    password = db.Column(db.String(120), nullable=False)
    phone_no = db.Column(db.String(20))
    email = db.Column(db.String(120))
    birthdate = db.Column(db.String(20))
    country = db.Column(db.String(50))
    state = db.Column(db.String(50))
    city = db.Column(db.String(50))
    address = db.Column(db.Text)

class Team(db.Model):
    __tablename__ = 'teams'
    team_name = db.Column(db.String(80), primary_key=True)
    code = db.Column(db.Text)
    submission_time = db.Column(db.String(50))

class HackathonSubmission(db.Model):
    __tablename__ = 'hackathon_submissions'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('users.username'))
    team_name = db.Column(db.String(80), db.ForeignKey('teams.team_name'))
    code = db.Column(db.Text)

class Credit(db.Model):
    __tablename__ = 'credits'
    username = db.Column(db.String(80), primary_key=True)
    points = db.Column(db.Integer, default=0)
    last_update = db.Column(db.Float, default=0)

class Reward(db.Model):
    __tablename__ = 'rewards'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), db.ForeignKey('users.username'))
    reward_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    date_earned = db.Column(db.String(50))

# Initialize database
def init_db():
    with app.app_context():
        db.create_all()

def generate_username(full_name, birthdate):
    # Keep your existing username generation logic
    return full_name.lower().replace(' ', '') + birthdate.replace('-', '')[:4]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        school_name = request.form['school_name']
        class_level = request.form['class']
        password = request.form['password']
        phone_no = request.form['phone_no']
        email = request.form['email']
        birthdate = request.form['birthdate']
        country = request.form['country']
        state = request.form['state']
        city = request.form['city']
        address = request.form['address']
        
        username = generate_username(full_name, birthdate)
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'error')
            return render_template('registration.html')
        
        # Create new user
        new_user = User(
            username=username,
            full_name=full_name,
            school_name=school_name,
            class_level=class_level,
            password=password,
            phone_no=phone_no,
            email=email,
            birthdate=birthdate,
            country=country,
            state=state,
            city=city,
            address=address
        )
        
        # Create initial credits
        new_credit = Credit(username=username, points=100)
        
        try:
            db.session.add(new_user)
            db.session.add(new_credit)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = User.query.filter_by(username=username).first()
    credit = Credit.query.filter_by(username=username).first()
    
    if not user:
        return redirect(url_for('login'))
    
    user_data = {
        'username': user.username,
        'full_name': user.full_name,
        'school_name': user.school_name,
        'class': user.class_level,
        'email': user.email,
        'credits': credit.points if credit else 0
    }
    
    return render_template('home.html', user=user_data)

@app.route('/courses')
def courses():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = User.query.filter_by(username=username).first()
    credit = Credit.query.filter_by(username=username).first()
    
    user_data = {
        'username': user.username,
        'full_name': user.full_name,
        'credits': credit.points if credit else 0
    }
    
    return render_template('courses.html', user=user_data)

@app.route('/projects')
def projects():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = User.query.filter_by(username=username).first()
    credit = Credit.query.filter_by(username=username).first()
    
    user_data = {
        'username': user.username,
        'full_name': user.full_name,
        'credits': credit.points if credit else 0
    }
    
    return render_template('projects.html', user=user_data)

@app.route('/ai-film-making')
def ai_film_making():
    return render_template('ai_film_making.html')

@app.route('/curriculum')
def curriculum():
    curriculum_data = {
        'modules': [
            {'title': 'Introduction to AI', 'description': 'Basic concepts and applications'},
            {'title': 'Machine Learning', 'description': 'Supervised and unsupervised learning'},
            {'title': 'Deep Learning', 'description': 'Neural networks and advanced techniques'}
        ]
    }
    return render_template('curriculum.html', curriculum=curriculum_data)

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = User.query.filter_by(username=username).first()
    credit = Credit.query.filter_by(username=username).first()
    
    if not user:
        return redirect(url_for('login'))
    
    user_data = {
        'username': user.username,
        'full_name': user.full_name,
        'school_name': user.school_name,
        'class': user.class_level,
        'email': user.email,
        'phone_no': user.phone_no,
        'birthdate': user.birthdate,
        'country': user.country,
        'state': user.state,
        'city': user.city,
        'address': user.address,
        'credits': credit.points if credit else 0
    }
    
    return render_template('portal.html', user=user_data)

@app.route('/offerings')
def offerings():
    return render_template('offerings.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/hackathon', methods=['GET', 'POST'])
def hackathon():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = User.query.filter_by(username=username).first()
    credit = Credit.query.filter_by(username=username).first()
    
    user_data = {
        'username': user.username,
        'full_name': user.full_name,
        'credits': credit.points if credit else 0
    }
    
    if request.method == 'POST':
        team_name = request.form['team_name']
        code = request.form['code']
        
        # Save hackathon submission
        submission = HackathonSubmission(
            username=username,
            team_name=team_name,
            code=code
        )
        
        try:
            db.session.add(submission)
            db.session.commit()
            flash('Hackathon submission successful!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Submission failed. Please try again.', 'error')
    
    return render_template('hackathon.html', user=user_data)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/school-transformation')
def school_transformation():
    return render_template('school_transformation.html')

@app.route('/success-stories')
def success_stories():
    return render_template('success_stories.html')

@app.route('/student-achievements')
def student_achievements():
    return render_template('student_achievements.html')

@app.route('/vouchers')
def vouchers():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    user = User.query.filter_by(username=username).first()
    credit = Credit.query.filter_by(username=username).first()
    rewards = Reward.query.filter_by(username=username).all()
    
    user_data = {
        'username': user.username,
        'full_name': user.full_name,
        'school_name': user.school_name,
        'class': user.class_level,
        'email': user.email,
        'credits': credit.points if credit else 0,
        'rewards': [{
            'type': reward.reward_type,
            'description': reward.description,
            'date': reward.date_earned
        } for reward in rewards]
    }
    
    return render_template('vouchers.html', user=user_data)

@app.route('/web-development')
def web_development():
    return render_template('web_development.html')

@app.route('/app-development')
def app_development():
    return render_template('app_development.html')

@app.route('/game-design')
def game_design():
    return render_template('game_design.html')

# Initialize database when app starts
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True)