import psycopg2

def create_tables():
    conn = psycopg2.connect(
        dbname="salloc",
        user="postgres",
        password="Sarapus1",
        host="localhost" 
    )
    
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            balance DECIMAL(10, 2) NOT NULL
        );
    """)
    
    cur.execute("""
        CREATE TABLE posts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            name VARCHAR(50) NOT NULL,
            allocation_percentage DECIMAL(5, 2) NOT NULL,
            total_saved DECIMAL(10, 2) NOT NULL,
            goal DECIMAL(10, 2) NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE transactions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            savings_post_id INTEGER REFERENCES posts(id),
            amount DECIMAL(10, 2) NOT NULL,
            transaction_date DATE NOT NULL,
            transaction_type VARCHAR(50) NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            date DATE NOT NULL,
            post VARCHAR(50) NOT NULL,
            type TEXT NOT NULL,
            amount FLOAT NOT NULL,
            notes VARCHAR(250) 
        );
    """)
    
    # Add more cur.execute() calls here to create more tables

    conn.commit()  # Don't forget to commit the changes
    cur.close()
    conn.close()

if __name__ == "__main__":
    create_tables()