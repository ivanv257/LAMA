DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS new_book;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT
);


CREATE TABLE new_book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    barcode TEXT,
    isbn TEXT,
    author TEXT,
    lang VARCHAR,
    publisher VARCHAR,
    title VARCHAR,
    publYear VARCHAR,
    FOREIGN KEY (author_id) REFERENCES user (id)
);