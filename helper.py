from functools import wraps
from flask import Flask, render_template, request, session, redirect, url_for

# Helper file, commonly used functions

# Logs transaction to history
def log_history(conn, user_id, post, amount, type, notes):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO history (user_id, post, type, amount, notes) VALUES (%s, %s, %s, %s, %s)",
            (user_id, post, type, amount, notes)
        )
    conn.commit()
    
# Checks login status
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

