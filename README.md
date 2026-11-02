# EDLBION secure dashboard starter

Private GitHub repository source. Financial records are NOT included.

## Render web service
- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
- Environment variables: `SECRET_KEY` (long random value), `DASHBOARD_PASSWORD_HASH` (Werkzeug password hash)
- Generate password hash locally with: `python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash(input('Password: ')))"`

Do NOT put the password or hash in GitHub. Set it as a Render environment variable. Keep repository Private.

## Important
This is a protected dashboard **shell**, not a finished OneDrive integration. No financial data is included. Upload/sync, durable storage, role-based accounts and director permissions require separate implementation before production use. A single shared password is not equivalent to role-based access. Never upload raw Excel or old HTML to the repository.
