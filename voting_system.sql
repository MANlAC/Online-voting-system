CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voter_id INTEGER UNIQUE,
    name TEXT,
    password TEXT,
    role TEXT,
    has_voted INTEGER DEFAULT 0
);

INSERT OR IGNORE INTO users (voter_id, name, password, role, has_voted)
VALUES (101, 'Test User', '1234', 'Voter', 0);

INSERT OR IGNORE INTO users (voter_id, name, password, role, has_voted)
VALUES (999, 'Admin', 'admin123', 'Admin', 0);

CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    votes INTEGER DEFAULT 0
);

INSERT OR IGNORE INTO candidates (name, votes) VALUES ('DONALD TRUMP', 0);
INSERT OR IGNORE INTO candidates (name, votes) VALUES ('VLADMIR PUTIN', 0);
INSERT OR IGNORE INTO candidates (name, votes) VALUES ('BARACK OBAMA', 0);

