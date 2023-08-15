from functools import wraps
from flask import Flask, render_template, request, session, redirect, url_for
import re

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
            return redirect(url_for('salloc.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def parse_numeric_value(value):
    try:
        # Try to convert value to integer
        return int(value)
    except ValueError:
        # If not a valid integer, remove non-numeric characters and try again
        numeric_part = ''.join(filter(str.isdigit, value))
        try:
            return int(numeric_part)
        except ValueError:
            return None
        
def capitalize_string(s):
    # Capitalize the first letter of each word in the string
    return ' '.join(word.capitalize() for word in s.split())

def is_valid_email(email):
    # Regular expression to validate email format
    pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
    return pattern.fullmatch(email) is not None

def is_valid_length(input_str, min_length, max_length):
    return min_length <= len(input_str) <= max_length

def sanitize_input(input_str):
    # Example of sanitizing input to prevent SQL injection
    return input_str.replace("'", "''")

def format_currency(value, currency):
    if currency == 'USD':
        return "${:,.2f}".format(value)
    elif currency == 'EUR':
        return "€{:,.2f}".format(value)
    else: # Default to NOK
        return "{:,.0f} kr".format(value)