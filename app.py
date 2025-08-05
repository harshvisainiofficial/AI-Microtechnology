from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3
import os
import datetime

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))
app.secret_key = 'your_secret_key_here'  # Replace with a secure key
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Add this line

# Database setup
def init_db():
    if not os.path.exists('users.db'):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE users (
            username TEXT PRIMARY KEY,
            full_name TEXT,
            school_name TEXT,
            class TEXT,
            password TEXT,
            phone_no TEXT,
            email TEXT,
            birthdate TEXT,
            country TEXT,
            state TEXT,
            city TEXT,
            address TEXT
        )''')
        c.execute('''CREATE TABLE teams (
            team_name TEXT PRIMARY KEY,
            code TEXT,
            submission_time TEXT
        )''')
        c.execute('''CREATE TABLE hackathon_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            team_name TEXT,
            code TEXT,
            FOREIGN KEY (username) REFERENCES users (username),
            FOREIGN KEY (team_name) REFERENCES teams (team_name)
        )''')
        c.execute('''CREATE TABLE credits (
            username TEXT PRIMARY KEY,
            points INTEGER DEFAULT 0,
            last_update REAL DEFAULT 0,
            FOREIGN KEY (username) REFERENCES users (username)
        )''')
        c.execute('''CREATE TABLE rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            voucher TEXT,
            redeemed_at TEXT,
            FOREIGN KEY (username) REFERENCES users (username)
        )''')
        conn.commit()
        conn.close()

# Initialize database
init_db()

def generate_username(full_name, birthdate):
    lower_name = full_name.lower().replace(' ', '')
    birthdate_formatted = birthdate.replace('-', '')  # Remove hyphens (YYYY-MM-DD to YYYYMMDD)
    return f"{lower_name}{birthdate_formatted}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        school_name = request.form['school_name']
        class_name = request.form['class']
        password = request.form['password']
        phone_no = request.form['phone_no']
        email = request.form['email']
        birthdate = request.form['birthdate']
        username = generate_username(full_name, birthdate)

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute('''INSERT INTO users (username, full_name, school_name, class, password, phone_no, email, birthdate)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (username, full_name, school_name, class_name, password, phone_no, email, birthdate))
            # Add credits row
            now = datetime.datetime.now().timestamp()
            c.execute('INSERT INTO credits (username, points, last_update) VALUES (?, ?, ?)', (username, 0, now))
            conn.commit()
            flash(f'Successfully Registered! Your username is: {username}', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists! Please try again.', 'error')
        finally:
            conn.close()
    return render_template('registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!', 'error')
    return render_template('login.html')

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (session['username'],))
    user = c.fetchone()
    c.execute('SELECT points FROM credits WHERE username = ?', (session['username'],))
    credits_row = c.fetchone()
    credits = credits_row[0] if credits_row else 0
    conn.close()
    
    if user:
        user_data = {
            'full_name': user[1],
            'school_name': user[2],
            'class': user[3],
            'roll_no': user[4],
            'phone_no': user[6],
            'email': user[7],
            'username': user[0],
            'birthdate': user[8],
            'credits': credits
        }
        return render_template('home.html', user=user_data)
    return redirect(url_for('login'))

@app.route('/courses')
def courses():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT points FROM credits WHERE username = ?', (session['username'],))
    credits_row = c.fetchone()
    credits = credits_row[0] if credits_row else 0
    conn.close()
    
    user_data = {'credits': credits}
    return render_template('courses.html', user=user_data)

@app.route('/projects')
def projects():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT points FROM credits WHERE username = ?', (session['username'],))
    credits_row = c.fetchone()
    credits = credits_row[0] if credits_row else 0
    conn.close()
    
    user_data = {'credits': credits}
    return render_template('projects.html', user=user_data)

@app.route('/curriculum')
def curriculum():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('login'))
    
    user_data = {
        'id': session['user_id'],
        'username': session['username'],
        'email': session['email'],
        'credits': session.get('credits', 100)
    }
    
    return render_template('curriculum.html', user=user_data)

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (session['username'],))
    user = c.fetchone()
    c.execute('SELECT points FROM credits WHERE username = ?', (session['username'],))
    credits_row = c.fetchone()
    credits = credits_row[0] if credits_row else 0
    conn.close()

    if user:
        user_data = {
            'full_name': user[1],
            'school_name': user[2],
            'class': user[3],
            'roll_no': user[4],
            'phone_no': user[6],
            'email': user[7],
            'username': user[0],
            'birthdate': user[8],
            'credits': credits
        }
        return render_template('portal.html', user=user_data)
    return redirect(url_for('login'))

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
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        team_name = request.form['team_name']
        code = request.form['code']
        submission_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            c.execute('INSERT INTO teams (team_name, code, submission_time) VALUES (?, ?, ?)',
                     (team_name, code, submission_time))
            c.execute('INSERT INTO hackathon_submissions (username, team_name, code) VALUES (?, ?, ?)',
                     (session['username'], team_name, code))
            conn.commit()
            flash('Code submitted successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Team name already exists! Please choose a different name.', 'error')
    
    c.execute('SELECT points FROM credits WHERE username = ?', (session['username'],))
    credits_row = c.fetchone()
    credits = credits_row[0] if credits_row else 0
    conn.close()
    
    user_data = {'credits': credits}
    return render_template('hackathon.html', user=user_data)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.before_request
def award_credits():
    if 'username' in session:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Get current time
        now = datetime.datetime.now().timestamp()
        
        # Check last update time
        c.execute('SELECT last_update FROM credits WHERE username = ?', (session['username'],))
        result = c.fetchone()
        
        if result:
            last_update = result[0]
            # Award 1 credit every 10 minutes (600 seconds)
            if now - last_update >= 600:
                c.execute('UPDATE credits SET points = points + 1, last_update = ? WHERE username = ?', 
                         (now, session['username']))
                conn.commit()
        
        conn.close()

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
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (session['username'],))
    user = c.fetchone()
    c.execute('SELECT points FROM credits WHERE username = ?', (session['username'],))
    credits_row = c.fetchone()
    credits = credits_row[0] if credits_row else 0
    conn.close()

    if user:
        user_data = {
            'full_name': user[1],
            'school_name': user[2],
            'class': user[3],
            'roll_no': user[4],
            'phone_no': user[6],
            'email': user[7],
            'username': user[0],
            'birthdate': user[8],
            'credits': credits
        }
        return render_template('vouchers.html', user=user_data)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)