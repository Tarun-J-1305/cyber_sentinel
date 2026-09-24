# Cyber Sentinel — Gamified Journey into Online Safety

A comprehensive cybersecurity education platform built with Flask and SQLite. Learn online safety through interactive videos, quizzes, and game simulations.

## Features

- **Three Difficulty Levels**: Beginner (Phishing), Intermediate (Passwords), Advanced (Wi-Fi Security)
- **Video Learning**: YouTube-embedded videos with completion tracking
- **Knowledge Quizzes**: 8-10 questions per level with 80% pass requirement
- **Game Challenges**: Interactive simulations to apply learned concepts
- **Badge System**: Earn badges by completing all levels
- **Progress Tracking**: All progress saved to SQLite database
- **Cooldown System**: 30-minute cooldown after 3 failed game attempts

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python main.py
```
Then open your browser and visit `http://localhost:5000/initdb` to create the database tables.

### 3. Start the App
```bash
python main.py
```
Open `http://localhost:5000` in your browser.

### 4. Test the Full Flow
1. **Sign Up** → Create a new account
2. **Beginner Level** → Watch all 3 videos (wait for completion)
3. **Quiz** → Answer all 10 questions (80%+ to pass)
4. **Game** → Complete the challenge
5. **Profile** → View your badge!

## Project Structure

```
app/
├── main.py                 # Flask backend & routes
├── templates/
│   ├── base.html          # Base layout
│   ├── landing.html       # Homepage
│   ├── signup.html        # Registration
│   ├── login.html         # Authentication
│   ├── dashboard.html     # Level selection
│   ├── level.html         # Video + quiz unlock
│   ├── quiz.html          # Quiz form
│   ├── quiz_result.html   # Quiz feedback
│   ├── game_phishing.html # Phishing game
│   ├── game_password.html # Password game
│   ├── game_wifi.html     # Wi-Fi game
│   └── profile.html       # User badges
├── static/
│   ├── style.css          # Styling
│   ├── app.js             # General functionality
│   ├── youtube.js         # YouTube API tracking
│   └── quiz.js            # Quiz validation
├── app.db                 # SQLite database
├── requirements.txt       # Python dependencies
└── schema.sql             # Database schema

README.md
```

## Database Schema

**users** - User accounts
- id, name, email (unique), password_hash, created_at

**progress** - Learning progress per level
- id, user_id, level_id, videos_watched, quiz_score, quiz_passed, attempts, cooldown_until

**badges** - Earned achievements
- id, user_id, badge_key, awarded_at

## Routes

### Authentication
- `GET /signup` - Registration form
- `POST /signup` - Create account
- `GET /login` - Login form
- `POST /login` - Authenticate user
- `GET /logout` - End session

### Learning
- `GET /` - Dashboard (requires login)
- `GET /course/<level_id>` - Videos & quiz unlock
- `POST /course/<level_id>/mark_watched` - Mark videos complete
- `GET /quiz/<level_id>` - Quiz form (requires videos watched)
- `POST /quiz_submit/<level_id>` - Submit answers & grade

### Games
- `GET /game/<level_id>` - Game interface (requires quiz passed)
- `POST /game_submit/<level_id>` - Game result submission

### User
- `GET /profile` - View badges & progress
- `GET /initdb` - Initialize database

## Quiz Structure

Each quiz contains 8-10 multiple-choice questions:
```python
{
    'q': 'Question text',
    'choices': ['Option A', 'Option B', 'Option C'],
    'answer': 1,  # Index of correct answer
    'explain': 'Explanation for learning'
}
```

## Game Attempts & Cooldown

- **Max Attempts**: 3 per game
- **Cooldown**: 30 minutes after 3 failed attempts
- **Win Condition**: Passing the game challenge before reaching attempt limit
- **Badge Award**: Badge awarded immediately upon game win

## Video IDs

**Beginner (Phishing Detection)**
- XBkzBrXlle0, AwYVRUqS3x0, yuhOgyz1cXs

**Intermediate (Password Strength)**
- z4_oqTZJqCo, eVIjEauSHZo, cczlpiiu42M, VDbMObpHWhw, Pm9D-h7FqV4

**Advanced (Wi-Fi Security)**
- WfYxrLaqlN8, X49lIPHcurE, 44I1wfgGT80

## Troubleshooting

### "Template not found" error
- Ensure all template files are in `app/templates/`
- Check file names match exactly (case-sensitive)

### Videos not tracking completion
- Clear browser cache and refresh
- Verify YouTube API is loading (check browser console)
- Allow iframes to load in browser settings

### Quiz answers not submitting
- Ensure ALL questions are answered before submit
- Check browser console for JavaScript errors
- Verify form is posting to correct endpoint

### Database errors
- Delete `app.db` and visit `/initdb` to reset
- Ensure database file has write permissions

## Security Notice

This application is for learning and simulation only. It does not provide instructions for illegal activities. All game simulations are educational and focus on cybersecurity defense.

## License

Educational use only.
