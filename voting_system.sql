DROP DATABASE IF EXISTS votingsystem;
CREATE DATABASE votingsystem;
USE votingsystem;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    voter_id INT UNIQUE,
    name VARCHAR(100),
    password VARCHAR(255),
    role VARCHAR(20)
);
INSERT INTO users (voter_id, name, password, role)
VALUES (101, 'Test User', '1234', 'Voter');

CREATE TABLE candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    votes INT DEFAULT 0
);
INSERT INTO candidates (name) VALUES 
('DONALD TRUMP'),
('VLADMIR PUTIN'),
('BARACK OBAMA');
SELECT 
    *
FROM
    users;

ALTER TABLE users ADD COLUMN has_voted INT DEFAULT 0;

INSERT INTO users (voter_id, name, password, role)
VALUES (999, 'Admin', 'admin123', 'Admin');


 
 



