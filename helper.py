# Helper file, commonly used functions

def log_history(conn, user_id, post, amount, type, notes):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO history (user_id, post, type, amount, notes) VALUES (%s, %s, %s, %s, %s)",
            (user_id, post, type, amount, notes)
        )
    conn.commit()