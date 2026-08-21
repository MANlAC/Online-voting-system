# Online Voting System

A Flask-based online voting app with admin and voter flows.

## Local development

1. Create a `.env` file from `.env.example` if needed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   python app.py
   ```

The app uses SQLite by default and creates the database automatically in the project folder as `voting_system.db`.

## Deployment

This project is ready for deployment on Render using the included `Procfile` and `requirements.txt`.

Set these environment variables in your hosting provider:
- `DATABASE_URL` (optional; defaults to the local SQLite database file)
- `SECRET_KEY`
- `PORT`

The app listens on `0.0.0.0:$PORT` when running with Gunicorn.
