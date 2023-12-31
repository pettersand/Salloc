CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    balance NUMERIC(10, 2) NOT NULL DEFAULT '0',
    cookies BOOLEAN DEFAULT TRUE,
    first_login BOOLEAN DEFAULT TRUE,
    currency TEXT DEFAULT 'NOK'
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(50) NOT NULL,
    allocation_percentage NUMERIC(5,2) NOT NULL,
    total_saved NUMERIC(10,2) DEFAULT 0,
    goal NUMERIC(10,2) NOT NULL
);

CREATE TABLE history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    post VARCHAR(50) NOT NULL,
    type TEXT NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    notes VARCHAR(250),
    time TIME WITHOUT TIME ZONE DEFAULT CURRENT_TIME
);