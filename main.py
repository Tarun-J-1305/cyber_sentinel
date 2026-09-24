from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'cyber'
DATABASE = 'app.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.executescript('''
        DROP TABLE IF EXISTS quiz_answers;
        DROP TABLE IF EXISTS quiz_results;
        DROP TABLE IF EXISTS quiz_questions;
        DROP TABLE IF EXISTS badges;
        DROP TABLE IF EXISTS progress;
        DROP TABLE IF EXISTS users;

        DROP TABLE IF EXISTS ctf_challenges;
        
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            level_id TEXT NOT NULL,
            videos_watched INTEGER DEFAULT 0,
            quiz_score REAL DEFAULT 0,
            quiz_passed INTEGER DEFAULT 0,
            attempts INTEGER DEFAULT 0,
            cooldown_until TEXT,
            UNIQUE(user_id, level_id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        
        CREATE TABLE quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level_id TEXT NOT NULL,
            question_index INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            choices TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            explanation TEXT NOT NULL,
            UNIQUE(level_id, question_index)
        );
        
        CREATE TABLE quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            level_id TEXT NOT NULL,
            score REAL NOT NULL,
            passed INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        
        CREATE TABLE quiz_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_result_id INTEGER NOT NULL,
            question_index INTEGER NOT NULL,
            user_answer TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            FOREIGN KEY (quiz_result_id) REFERENCES quiz_results(id)
        );
        
        CREATE TABLE badges (
            user_id INTEGER NOT NULL,
            badge_key TEXT NOT NULL,
            awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, badge_key),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        

        
        CREATE TABLE ctf_challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            attempts INTEGER DEFAULT 0,
            hints_used INTEGER DEFAULT 0,
            solved INTEGER DEFAULT 0,
            cooldown_until TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            solved_at TIMESTAMP,
            UNIQUE(user_id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')
    db.commit()
    db.close()


def is_level_complete(user_id, level_id):
    db = get_db()
    badge_key = CONTENT[level_id]['badge']
    badge = db.execute('SELECT * FROM badges WHERE user_id = ? AND badge_key = ?',
                      (user_id, badge_key)).fetchone()
    db.close()
    return bool(badge)

def is_level_unlocked(user_id, level_id):
    if level_id == 'beginner':
        return True
    
    levels = ['beginner', 'intermediate', 'advanced']
    try:
        idx = levels.index(level_id)
        prev_level = levels[idx - 1]
        return is_level_complete(user_id, prev_level)
    except ValueError:
        return False

CONTENT = {
    'beginner': {
        'title': 'Beginner: Phishing Detection',
        'game': 'phishing',
        'badge': 'Phishing Master',
        'videos': [
            {'id': 'XBkzBrXlle0', 'title': 'Phishing Basics'},
            {'id': 'AwYVRUqS3x0', 'title': 'Spotting Phishing Emails'},
            {'id': 'yuhOgyz1cXs', 'title': 'Safe Online Practices'}
        ],
        'quiz': [
            {'q': 'What is the main purpose of phishing?', 'choices': ['To improve email delivery', 'To steal sensitive information', 'To fix device performance', 'To update software'], 'answer': 'B', 'explain': 'Phishing attacks are designed to steal sensitive information like passwords and financial data through deceptive emails.'},
            {'q': 'Which of the following is a common red flag in phishing emails?', 'choices': ['Perfect grammar', 'Emails from known contacts', 'Urgent or threatening language', 'Verified support numbers'], 'answer': 'C', 'explain': 'Phishing emails create urgency to trick users into making quick decisions without verification.'},
            {'q': 'What should you do BEFORE clicking an email link?', 'choices': ['Forward it to IT support', 'Hover over the link to preview the real URL', 'Open it in another browser', 'Click it quickly before it expires'], 'answer': 'B', 'explain': 'Hovering over links reveals the actual destination URL, which may differ from the displayed text.'},
            {'q': 'Which domain is MOST suspicious?', 'choices': ['paypal.com', 'secure-paypal.com.verify-login.co', 'accounts.google.com', 'microsoftonline.com'], 'answer': 'B', 'explain': 'Complex domains with legitimate company names embedded are common phishing tactics using typosquatting.'},
            {'q': 'Why do phishing attackers create urgency?', 'choices': ['To help users update security', 'To make victims act without thinking', 'To improve customer service', 'To reduce mail size'], 'answer': 'B', 'explain': 'Urgency bypasses critical thinking and encourages quick actions like clicking links or providing information.'},
            {'q': 'Why is this address suspicious: support@faceb00k-security.com?', 'choices': ['It contains the word "security"', 'It includes digits replacing letters', 'It looks professional', 'It uses HTTPS'], 'answer': 'B', 'explain': 'Using digits to replace letters (like 0 for O) is a classic phishing tactic to mimic legitimate addresses.'},
            {'q': 'Which attachment is MOST dangerous?', 'choices': ['travel_ticket.pdf', 'invoice_2024.pdf.exe', 'meeting_notes.docx', 'logo.png'], 'answer': 'B', 'explain': 'Executable files (.exe) disguised with document-like names are classic malware delivery methods in phishing attacks.'},
            {'q': 'What should you do if you receive a prize email you never signed up for?', 'choices': ['Click to claim the offer', 'Ignore or delete it', 'Reply to verify', 'Download the confirmation file'], 'answer': 'B', 'explain': 'Unsolicited prize notifications are common phishing lures designed to capture personal information or spread malware.'},
            {'q': 'What is spear phishing?', 'choices': ['Pop-up ads', 'Targeted phishing toward specific people', 'Random spam messages', 'SMS marketing'], 'answer': 'B', 'explain': 'Spear phishing targets specific individuals with personalized attacks, making them more convincing and effective.'},
            {'q': 'What will a phishing email pretending to be your bank typically do?', 'choices': ['Ask you to verify your account via a link', 'Send account summary only', 'Tell you to visit the branch', 'Provide legal disclaimers'], 'answer': 'A', 'explain': 'Phishing emails impersonating banks often request account verification through suspicious links to steal credentials.'},
            {'q': 'What is the BEST way to verify an email sender?', 'choices': ['Check the full email address', 'Trust the logo', 'Rely on the subject line', 'Look at the background color'], 'answer': 'A', 'explain': 'Verify the complete email address format, as phishers often use addresses similar to legitimate senders.'},
            {'q': 'What do fake login pages aim to do?', 'choices': ['Reduce website load time', 'Steal usernames and passwords', 'Improve your browsing', 'Fix account errors'], 'answer': 'B', 'explain': 'Fake login pages are designed to capture credentials, which attackers then use to access real accounts.'},
            {'q': 'What is the safest way to visit your bank\'s website?', 'choices': ['Ask someone to forward the link', 'Click from email promotions', 'Type the official URL manually', 'Open random search results'], 'answer': 'C', 'explain': 'Manually typing the official URL ensures you reach the legitimate site and avoid phishing pages.'},
            {'q': 'Which sign suggests a spoofed email?', 'choices': ['Missing emojis', 'Sender address is slightly altered', 'Email uses your first name', 'Normal greeting'], 'answer': 'B', 'explain': 'Slightly altered sender addresses (like paypall.com or amaz0n.com) are telltale signs of spoofed emails.'},
            {'q': 'If you accidentally click a phishing link, what should you do FIRST?', 'choices': ['Change your password immediately', 'Ignore the page', 'Click again to check', 'Screenshot it and continue browsing'], 'answer': 'A', 'explain': 'Immediately change passwords for any accounts accessed through the link to prevent unauthorized access.'}
        ]
    },
    'intermediate': {
        'title': 'Intermediate: Password Security',
        'game': 'password',
        'badge': 'Password Guardian',
        'videos': [
            {'id': 'z4_oqTZJqCo', 'title': 'Password Basics'},
            {'id': 'eVIjEauSHZo', 'title': 'Strong Passwords'},
            {'id': 'cczlpiiu42M', 'title': 'Password Managers'},
            {'id': 'VDbMObpHWhw', 'title': 'Two-Factor Auth'},
            {'id': 'Pm9D-h7FqV4', 'title': 'Password Best Practices'}
        ],
        'quiz': [
            {'q': 'What is the main goal of password cracking?', 'choices': ['To optimize login speed', 'To guess or retrieve a user\'s password', 'To reduce CPU usage', 'To generate secure passwords'], 'answer': 'B', 'explain': 'Password cracking aims to guess or retrieve user passwords through various attack methods.'},
            {'q': 'Which attack tries every possible combination of characters?', 'choices': ['Dictionary attack', 'Phishing attack', 'Brute-force attack', 'Hybrid attack'], 'answer': 'C', 'explain': 'Brute-force attacks systematically try all possible character combinations until finding the correct password.'},
            {'q': 'Which factor makes a password easier to crack using dictionary attacks?', 'choices': ['Using unrelated symbols', 'Using common words like "password123"', 'Using a password manager', 'Using long random strings'], 'answer': 'B', 'explain': 'Dictionary attacks use lists of common words and phrases, making predictable passwords vulnerable.'},
            {'q': 'What does hashing do to a password?', 'choices': ['Sends it directly over the network', 'Converts it into a fixed-length irreversible value', 'Stores it as plain text', 'Deletes the password file'], 'answer': 'B', 'explain': 'Hashing converts passwords into irreversible values, making them impossible to reverse-engineer.'},
            {'q': 'Which hashing algorithm is considered outdated and insecure?', 'choices': ['SHA-256', 'SHA-3', 'Bcrypt', 'MD5'], 'answer': 'D', 'explain': 'MD5 has been deprecated for security purposes due to known collision vulnerabilities.'},
            {'q': 'What makes a password "strong"?', 'choices': ['Using only lowercase letters', 'Using a mix of uppercase, lowercase, numbers, and symbols', 'Using your pet\'s name', 'Using short phrases'], 'answer': 'B', 'explain': 'Strong passwords combine multiple character types to resist various cracking methods.'},
            {'q': 'Which method speeds up brute-force cracking by storing precomputed hashes?', 'choices': ['Firewall rules', 'Rainbow tables', 'VPN tunneling', 'SSL certificates'], 'answer': 'B', 'explain': 'Rainbow tables store precomputed hashes for rapid password matching during attacks.'},
            {'q': 'What does salting a password do?', 'choices': ['Adds random data to the password before hashing', 'Removes symbols', 'Converts password to uppercase', 'Sends it to the cloud'], 'answer': 'A', 'explain': 'Salting adds random data to each password before hashing, preventing rainbow table attacks.'},
            {'q': 'Why is "123456" or "password" considered weak?', 'choices': ['They are long', 'They are common and easily guessable', 'They contain symbols', 'They are encrypted'], 'answer': 'B', 'explain': 'These are among the most commonly used passwords and appear in every attacker\'s dictionary.'},
            {'q': 'How can a password manager improve security?', 'choices': ['By cracking passwords', 'By generating and storing complex unique passwords', 'By sharing passwords', 'By shortening passwords'], 'answer': 'B', 'explain': 'Password managers create and securely store unique complex passwords for each account.'},
            {'q': 'Which attack uses a list of common passwords and phrases?', 'choices': ['Dictionary attack', 'Brute-force attack', 'CAT attack', 'MITM attack'], 'answer': 'A', 'explain': 'Dictionary attacks use precompiled lists of known common passwords and words.'},
            {'q': 'What is the BEST way to protect against brute-force attacks?', 'choices': ['Use short passwords', 'Disable login alerts', 'Enable rate limiting & lockout policies', 'Disable hashing'], 'answer': 'C', 'explain': 'Rate limiting and lockout policies prevent attackers from making unlimited password attempts.'},
            {'q': 'What is the recommended minimum password length for strong security?', 'choices': ['4–6 characters', '6–8 characters', 'At least 12 characters', 'Exactly 20 characters'], 'answer': 'C', 'explain': 'At least 12 characters significantly increases password strength against modern attacks.'},
            {'q': 'What is multi-factor authentication (MFA)?', 'choices': ['Using multiple passwords', 'Using two or more verification methods', 'Changing password monthly', 'Using only symbols'], 'answer': 'B', 'explain': 'MFA requires multiple verification methods (password + phone code, biometric, etc.) for account access.'},
            {'q': 'What is a hybrid attack?', 'choices': ['Brute-force attack using only numbers', 'Attack combining dictionary words + random characters', 'Attack using only rainbow tables', 'Attack using malware'], 'answer': 'B', 'explain': 'Hybrid attacks combine dictionary words with random characters for more effective guessing.'}
        ]
    },
    'advanced': {
        'title': 'Advanced: Wi-Fi Security',
        'game': 'wifi',
        'badge': 'Network Guardian',
        'videos': [
            {'id': 'WfYxrLaqlN8', 'title': 'Wi-Fi Basics'},
            {'id': 'X49lIPHcurE', 'title': 'Wi-Fi Encryption'},
            {'id': '44I1wfgGT80', 'title': 'Router Security'}
        ],
        'quiz': [
            {'q': 'What does WPA3 primarily improve compared to WPA2?', 'choices': ['Better password recovery', 'Stronger encryption & protection against brute-force attacks', 'Faster internet speed', 'More router range'], 'answer': 'B', 'explain': 'WPA3 uses Simultaneous Authentication of Equals (SAE) for stronger protection against brute-force attacks compared to WPA2.'},
            {'q': 'What is the purpose of the 4-way handshake in WiFi security?', 'choices': ['To connect devices to Bluetooth', 'To authenticate a client & generate encryption keys', 'To boost WiFi speed', 'To scan for nearby devices'], 'answer': 'B', 'explain': 'The 4-way handshake establishes secure communication between the access point and client device, authenticating and generating encryption keys.'},
            {'q': 'Which encryption method is considered the most secure for modern WiFi networks?', 'choices': ['WEP', 'WPA', 'WPA2-PSK', 'WPA3-SAE'], 'answer': 'D', 'explain': 'WPA3-SAE (Simultaneous Authentication of Equals) is the most modern and secure WiFi encryption standard available.'},
            {'q': 'Why is WEP no longer secure?', 'choices': ['It requires a long password', 'Its encryption keys can be cracked quickly', 'It has strong protection', 'It uses modern protocols'], 'answer': 'B', 'explain': 'WEP\'s 24-bit initialization vector and weak key scheduling make it vulnerable to modern cracking tools.'},
            {'q': 'What is "SAE" in WPA3?', 'choices': ['Secure Access Extension', 'Simultaneous Authentication of Equals', 'Standard Access Encryption', 'Shared Access Exchange'], 'answer': 'B', 'explain': 'SAE is WPA3\'s authentication method that replaces Pre-Shared Key (PSK), providing stronger protection against dictionary attacks.'},
            {'q': 'What is the main purpose of WiFi encryption?', 'choices': ['Increase data speed', 'Protect data transmitted between devices', 'Strengthen router antennas', 'Share passwords easily'], 'answer': 'B', 'explain': 'WiFi encryption scrambles data to prevent unauthorized interception and eavesdropping on wireless networks.'},
            {'q': 'What is a deauthentication attack?', 'choices': ['Removing a device from the network by forcing disconnect packets', 'Automatically renewing the IP address', 'Speeding up authentication', 'Resetting router settings'], 'answer': 'A', 'explain': 'Deauth attacks send spoofed frames forcing WiFi devices to disconnect, enabling man-in-the-middle or other attacks.'},
            {'q': 'Which of the following is the BEST way to secure a home WiFi network?', 'choices': ['Use "admin" as the router password', 'Disable encryption', 'Use WPA3 with a strong password', 'Keep the SSID open'], 'answer': 'C', 'explain': 'WPA3 with a strong, unique password provides maximum security for home WiFi networks.'},
            {'q': 'What is a WiFi SSID?', 'choices': ['A security key', 'The WiFi network name', 'The router brand', 'The MAC address'], 'answer': 'B', 'explain': 'SSID (Service Set Identifier) is the broadcast name of the wireless network that devices use to identify and connect.'},
            {'q': 'What is the main purpose of MAC address filtering?', 'choices': ['Improve internet speed', 'Allow only approved devices to connect', 'Change router name', 'Increase WiFi range'], 'answer': 'B', 'explain': 'MAC filtering restricts network access to only devices with approved MAC addresses, adding an extra security layer.'},
            {'q': 'Why should default router credentials be changed?', 'choices': ['They are unique', 'They are publicly known and easy to abuse', 'They improve WiFi speed', 'They block all attackers'], 'answer': 'B', 'explain': 'Default credentials (often admin/admin) are publicly documented and used by attackers to compromise routers.'},
            {'q': 'What is a WiFi captive portal?', 'choices': ['A device for expanding WiFi', 'A login page used in public networks', 'A password-cracking tool', 'A router firmware updater'], 'answer': 'B', 'explain': 'Captive portals redirect users to login pages before granting network access, commonly used in public WiFi systems.'},
            {'q': 'Why are long, random WiFi passwords recommended?', 'choices': ['They reduce data usage', 'They prevent brute-force and dictionary attacks', 'They improve range', 'They enable auto-connect'], 'answer': 'B', 'explain': 'Long random passwords exponentially increase the time needed for brute-force and dictionary attacks to succeed.'},
            {'q': 'What is a PMK (Pairwise Master Key)?', 'choices': ['A router antenna', 'A key derived from WiFi password for encrypting sessions', 'A WiFi booster', 'A DNS cache file'], 'answer': 'B', 'explain': 'The PMK is derived from the WiFi password and used to generate session-specific encryption keys for secure communication.'},
            {'q': 'What is the safest place to perform WiFi penetration testing?', 'choices': ['Any network around you', 'Public WiFi networks', 'Only on networks you own or have permission for', 'Random hotspots'], 'answer': 'C', 'explain': 'Ethical WiFi security testing MUST only be performed on networks you own or have explicit written permission to test.'}
        ]
    },
    'crypto': {
        'title': 'FINAL: Crypto Crucible - Cipher Breaker',
        'game': 'ctf',
        'badge': 'crypto_master',
        'puzzle': 'a84bcf9fb5de660e0757547f3f5abcde14317f90',
        'flag': 'FLAG{cyber}',
        'cipher_type': 'SHA1 Hash Challenge',
        'description': 'A piece of data has been hashed. Identify the algorithm, crack the hash, and submit the original word as the flag in the format FLAG{answer}.',
        'hints': [
            'The hash is a 40-character hexadecimal string. This is a common length for a specific hashing algorithm.',
            'The original text is a common English word related to the theme of this application. You might need an online hash cracker or a wordlist.'
        ]
    }
}

@app.route('/initdb')
def initdb():
    init_db()
    return 'Database initialized'

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('landing'))

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/level/<lvl>')
def level(lvl):
    return render_template('level.html', level=lvl)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        db = get_db()
        error = None
        try:
            db.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                      (name, email, generate_password_hash(password)))
            db.commit()
        except db.IntegrityError:
            error = 'Email already exists'
        finally:
            db.close()
        
        if error:
            flash(error, 'error')
        else:
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        db.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['name'] = user['name']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'success')
    return redirect(url_for('landing'))

@app.route('/watch_status/<level_id>')
def watch_status(level_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    if level_id not in CONTENT:
        return jsonify({'error': 'Level not found'}), 404
    
    db = get_db()
    progress = db.execute('SELECT videos_watched FROM progress WHERE user_id = ? AND level_id = ?',
                         (session['user_id'], level_id)).fetchone()
    db.close()
    
    return jsonify({'watched': progress['videos_watched'] if progress else 0})

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    levels = []
    ctf_unlocked = True
    
    for level_id in ['beginner', 'intermediate', 'advanced']:
        progress = db.execute('SELECT * FROM progress WHERE user_id = ? AND level_id = ?',
                            (session['user_id'], level_id)).fetchone()
        if not progress:
            db.execute('INSERT INTO progress (user_id, level_id) VALUES (?, ?)',
                      (session['user_id'], level_id))
            db.commit()
            progress = db.execute('SELECT * FROM progress WHERE user_id = ? AND level_id = ?',
                                (session['user_id'], level_id)).fetchone()
        
        # Check if user has earned the badge for this level (means game was won)
        badge_key = CONTENT[level_id]['badge']
        badge = db.execute('SELECT * FROM badges WHERE user_id = ? AND badge_key = ?',
                          (session['user_id'], badge_key)).fetchone()
        
        level_complete = bool(badge)
        is_locked = not is_level_unlocked(session['user_id'], level_id)
        
        levels.append({
            'id': level_id,
            'title': CONTENT[level_id]['title'],
            'videos_watched': progress['videos_watched'],
            'quiz_passed': progress['quiz_passed'],
            'game_won': level_complete,
            'is_locked': is_locked
        })
        
    # Check if CTF is unlocked (requires Advanced level completion)
    ctf_unlocked = is_level_complete(session['user_id'], 'advanced')
    
    badges = db.execute('SELECT badge_key FROM badges WHERE user_id = ?',
                       (session['user_id'],)).fetchall()
    db.close()
    
    return render_template('dashboard.html', levels=levels, badges=[b['badge_key'] for b in badges], ctf_unlocked=ctf_unlocked)

@app.route('/course/<level_id>')
def course(level_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if level_id not in CONTENT:
        flash('Level not found', 'error')
        return redirect(url_for('dashboard'))

    if not is_level_unlocked(session['user_id'], level_id):
        flash(f'Complete previous levels to unlock {CONTENT[level_id]["title"]}', 'error')
        return redirect(url_for('dashboard'))
    
    db = get_db()
    progress = db.execute('SELECT * FROM progress WHERE user_id = ? AND level_id = ?',
                         (session['user_id'], level_id)).fetchone()
    db.close()
    
    return render_template('course.html',
                         level_id=level_id,
                         title=CONTENT[level_id]['title'],
                         videos=CONTENT[level_id]['videos'],
                         videos_watched=progress['videos_watched'],
                         total_videos=len(CONTENT[level_id]['videos']),
                         quiz_passed=progress['quiz_passed'])

@app.route('/course/<level_id>/mark_watched', methods=['POST'])
def mark_watched(level_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    if level_id not in CONTENT:
        return jsonify({'error': 'Level not found'}), 404
    
    total_videos = len(CONTENT[level_id]['videos'])
    db = get_db()
    db.execute('UPDATE progress SET videos_watched = ? WHERE user_id = ? AND level_id = ?',
              (total_videos, session['user_id'], level_id))
    db.commit()
    db.close()
    
    return jsonify({'success': True})

@app.route('/quiz/<level_id>')
def quiz(level_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if level_id not in CONTENT:
        flash('Level not found', 'error')
        return redirect(url_for('dashboard'))

    if not is_level_unlocked(session['user_id'], level_id):
        flash(f'Complete previous levels to unlock {CONTENT[level_id]["title"]}', 'error')
        return redirect(url_for('dashboard'))
    
    db = get_db()
    progress = db.execute('SELECT * FROM progress WHERE user_id = ? AND level_id = ?',
                         (session['user_id'], level_id)).fetchone()
    db.close()
    
    if not progress or not progress['videos_watched']:
        flash('Please watch all videos first!', 'error')
        return redirect(url_for('course', level_id=level_id))
    
    questions = []
    for i, q in enumerate(CONTENT[level_id]['quiz']):
        choices_with_letters = []
        for j, choice in enumerate(q['choices']):
            choices_with_letters.append({
                'letter': chr(65 + j),
                'text': choice
            })
        questions.append({
            'index': i,
            'q': q['q'],
            'choices': choices_with_letters
        })
    
    return render_template('quiz.html', level_id=level_id, title=CONTENT[level_id]['title'], questions=questions)

@app.route('/quiz_submit/<level_id>', methods=['POST'])
def quiz_submit(level_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if level_id not in CONTENT:
        flash('Level not found', 'error')
        return redirect(url_for('dashboard'))
    
    quiz_data = CONTENT[level_id]['quiz']
    correct = 0
    answers = []
    
    for i, q in enumerate(quiz_data):
        user_answer = request.form.get(f'q{i}')
        correct_answer = q['answer']
        answer_choices = q['choices']
        user_answer_text = 'Not answered'
        
        if user_answer:
            try:
                choice_index = ord(user_answer) - 65
                if 0 <= choice_index < len(answer_choices):
                    user_answer_text = answer_choices[choice_index]
            except:
                user_answer_text = user_answer
        
        correct_answer_text = answer_choices[ord(correct_answer) - 65] if correct_answer else correct_answer
        
        answers.append({
            'index': i,
            'q': q['q'],
            'user_answer': user_answer_text,
            'correct_answer': correct_answer_text,
            'explain': q['explain'],
            'is_correct': user_answer == correct_answer
        })
        if user_answer == correct_answer:
            correct += 1
    
    score = round((correct / len(quiz_data)) * 100, 2)
    passed = score >= 80
    
    db = get_db()
    
    # Update progress
    db.execute('UPDATE progress SET quiz_score = ?, quiz_passed = ? WHERE user_id = ? AND level_id = ?',
              (score, 1 if passed else 0, session['user_id'], level_id))
    
    # Save quiz result to database
    cursor = db.execute(
        'INSERT INTO quiz_results (user_id, level_id, score, passed, total_questions) VALUES (?, ?, ?, ?, ?)',
        (session['user_id'], level_id, score, 1 if passed else 0, len(quiz_data))
    )
    quiz_result_id = cursor.lastrowid
    
    # Save each answer to database
    for i, answer in enumerate(answers):
        db.execute(
            'INSERT INTO quiz_answers (quiz_result_id, question_index, user_answer, correct_answer, is_correct) VALUES (?, ?, ?, ?, ?)',
            (quiz_result_id, i, answer['user_answer'], answer['correct_answer'], 1 if answer['is_correct'] else 0)
        )
    
    db.commit()
    db.close()
    
    return render_template('quiz_result.html',
                         level_id=level_id,
                         title=CONTENT[level_id]['title'],
                         score=score,
                         correct=correct,
                         total=len(quiz_data),
                         passed=passed,
                         answers=answers,
                         quiz_result_id=quiz_result_id)

@app.route('/game/<level_id>')
def game(level_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if level_id not in CONTENT:
        flash('Level not found', 'error')
        return redirect(url_for('dashboard'))

    if not is_level_unlocked(session['user_id'], level_id):
        flash(f'Complete previous levels to unlock {CONTENT[level_id]["title"]}', 'error')
        return redirect(url_for('dashboard'))
    
    db = get_db()
    progress = db.execute('SELECT * FROM progress WHERE user_id = ? AND level_id = ?',
                         (session['user_id'], level_id)).fetchone()
    db.close()
    
    if not progress or not progress['quiz_passed']:
        flash('Please pass the quiz first!', 'error')
        return redirect(url_for('course', level_id=level_id))
    
    if progress['cooldown_until']:
        cooldown_until = datetime.fromisoformat(progress['cooldown_until'])
        if datetime.now() < cooldown_until:
            remaining = int((cooldown_until - datetime.now()).total_seconds() / 60)
            flash(f'Cooldown active. Try again in {remaining} minutes.', 'warning')
            return redirect(url_for('course', level_id=level_id))
    
    game_type = CONTENT[level_id]['game']
    attempts_left = max(0, 3 - progress['attempts'])
    
    if game_type == 'phishing':
        return render_template('game_phishing.html', level_id=level_id, attempts_left=attempts_left)
    elif game_type == 'password':
        return render_template('game_password.html', level_id=level_id, attempts_left=attempts_left)
    else:
        return render_template('game_wifi.html', level_id=level_id, attempts_left=attempts_left)

@app.route('/game_submit/<level_id>', methods=['POST'])
def game_submit(level_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    if level_id not in CONTENT:
        return jsonify({'error': 'Level not found'}), 404
    
    data = request.get_json()
    outcome = data.get('outcome')
    
    db = get_db()
    progress = db.execute('SELECT * FROM progress WHERE user_id = ? AND level_id = ?',
                         (session['user_id'], level_id)).fetchone()
    
    new_attempts = progress['attempts'] + 1
    db.execute('UPDATE progress SET attempts = ? WHERE user_id = ? AND level_id = ?',
              (new_attempts, session['user_id'], level_id))
    
    if outcome == 'win':
        db.execute('INSERT OR IGNORE INTO badges (user_id, badge_key) VALUES (?, ?)',
                  (session['user_id'], CONTENT[level_id]['badge']))
        db.commit()
        db.close()
        return jsonify({'result': 'win', 'message': 'Badge earned!', 'attempts': 3 - new_attempts})
    else:
        if new_attempts >= 3:
            cooldown_until = (datetime.now() + timedelta(minutes=30)).isoformat()
            db.execute('UPDATE progress SET cooldown_until = ? WHERE user_id = ? AND level_id = ?',
                      (cooldown_until, session['user_id'], level_id))
            db.commit()
            db.close()
            return jsonify({'result': 'cooldown', 'attempts': 0})
        else:
            db.commit()
            db.close()
            return jsonify({'result': 'lose', 'attempts': 3 - new_attempts})



@app.route('/ctf')
def ctf():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if not is_level_complete(session['user_id'], 'advanced'):
        flash('Complete all levels to unlock the Final CTF Challenge!', 'error')
        return redirect(url_for('dashboard'))
    
    # Define the static challenge as requested
    challenge = {
        'flag': 'hello hacker', 
        'hash': 'f9b7cf2236757efbd6b41138e475b109a6aad207', 
        'hint': 'Common greeting + profession'
    }
    
    # Store the correct flag in session for verification
    session['ctf_flag'] = challenge['flag']
    
    return render_template('sha1_lab_challenge.html', 
                         target_hash=challenge['hash'],
                         hint_text=challenge['hint'])

@app.route('/api/sha1/encrypt', methods=['POST'])
def sha1_encrypt():
    data = request.get_json()
    text = data.get('text', '')
    import hashlib
    sha1_hash = hashlib.sha1(text.encode()).hexdigest()
    return jsonify({'hash': sha1_hash})

@app.route('/api/sha1/decrypt', methods=['POST'])
def sha1_decrypt():
    # This endpoint might be legacy or used for the rainbow table tool if we kept it.
    # For the challenge itself, we use /api/sha1/verify
    data = request.get_json()
    sha1_hash = data.get('hash', '').lower()
    return jsonify({'found': False, 'message': 'Rainbow table lookup not implemented for this challenge.'})

@app.route('/api/sha1/verify', methods=['POST'])
def sha1_verify():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    data = request.get_json()
    mission_id = data.get('mission_id')
    answer = data.get('answer', '').strip()
    
    success = False
    
    if mission_id == 2:
        # Verify against the session-stored flag
        correct_flag = session.get('ctf_flag')
        print(f"DEBUG: Session Flag: {correct_flag}, User Answer: {answer}", flush=True)
        if correct_flag and answer.lower() == correct_flag.lower():
            success = True
            
            # Award Badge
            db = get_db()
            db.execute('INSERT OR IGNORE INTO badges (user_id, badge_key) VALUES (?, ?)', 
                      (session['user_id'], 'crypto_master'))
            db.commit()
            db.close()
            
            # Clear the flag from session so they get a new one next time (optional, but good for rotation)
            session.pop('ctf_flag', None)
            
    return jsonify({'success': success})

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not user:
        db.close()
        return redirect(url_for('login'))
    
    badges = db.execute('SELECT badge_key, awarded_at FROM badges WHERE user_id = ?',
                       (session['user_id'],)).fetchall()
    db.close()
    
    return render_template('profile.html', user=user, badges=badges)

def initialize_database_if_needed():
    if not os.path.exists(DATABASE):
        with app.app_context():
            init_db()

if __name__ == '__main__':
    initialize_database_if_needed()
    app.run(host='0.0.0.0', port=5004, debug=False)
