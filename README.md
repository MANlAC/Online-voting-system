# Online Voting System

A Flask-based online voting app with admin and voter flows. Supports candidate photos, vote management, and is ready for deployment on Render.

## Features

- **Voter login** and one-click voting with candidate photos
- **Admin panel** to add/remove candidates, upload/replace photos, and reset votes
- **Results page** showing vote counts with candidate photos
- **PostgreSQL** support for production, **SQLite** fallback for local dev

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

## Deployment (Render)

This project is ready for deployment on Render using the included `render.yaml`.

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) and create a new "Blueprint" from your repo
3. Render will auto-detect `render.yaml` and create both the web service and PostgreSQL database
4. The `DATABASE_URL` is automatically connected to the database

### Default accounts (auto-created on first run)
- **Admin:** voter ID `999`, password `admin123`
- **Voter:** voter ID `101`, password `1234`

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | No | PostgreSQL connection string. If empty, uses local SQLite. |
| `SECRET_KEY` | Yes | Flask session secret key. |
| `PORT` | No | Port to listen on (default: 5000). |

## Tech Stack

- Python 3.12, Flask 3.1
- PostgreSQL (Render) / SQLite (local)
- Gunicorn for production
