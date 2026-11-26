# QuizMaster — Gaming Edition

## Run locally
1. Install Python 3.10 or newer.
2. Open this folder in VS Code.
3. Create and activate a virtual environment (optional but recommended).
4. Run `pip install -r requirements.txt`.
5. Run `python app.py`.
6. Open http://127.0.0.1:5000 in your browser.

## Deploy on Render
1. Create a GitHub repository and upload the contents of this folder.
2. On Render, create **New + → Web Service** and connect the repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add environment variable `SECRET_KEY` with a long random value.
6. Deploy. Open the generated URL.

## Important deployment note
This starter stores users and progress in `progress.json`. On hosting platforms with temporary filesystems, this file may reset during redeploy/restart. For permanent multi-user data, connect a managed database (for example PostgreSQL) before relying on it for real student accounts. Do not use real or sensitive passwords for a classroom demo.

## Included features
- Username/password registration and login (passwords are hashed)
- Original four subjects and original question bank
- XP rewards, sequential subject unlocking, leaderboard
- Easy/Medium/Hard modes and countdown timer
- Performance dashboard, best scores and quiz history
- Daily Python challenge and achievement badges
- Gaming-inspired responsive UI, progress bar and simple sound effects
