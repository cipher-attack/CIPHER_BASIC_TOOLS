#!/usr/bin/env python3
"""
Local-only vulnerable lab (for learning):
- SQL injection in /login and /search
- Reflected XSS in /xss

Run:
  python lab/app.py
Then visit http://127.0.0.1:8000

Ethical use only: Use on systems you own or have permission to test.
"""
from __future__ import annotations
import os
import sqlite3
from flask import Flask, request, Response

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), 'lab.db')


def init_db() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        'CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)'
    )
    # Seed data if empty
    cur.execute('SELECT COUNT(*) FROM users')
    count = cur.fetchone()[0]
    if count == 0:
        cur.executemany(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            [
                ('admin', 'admin123'),
                ('alice', 'password'),
                ('bob', 'qwerty'),
            ],
        )
        conn.commit()
    conn.close()


@app.get('/')
def index() -> Response:
    return Response(
        '\n'.join(
            [
                '<h1>Vulnerable Lab</h1>',
                '<p>This lab is intentionally vulnerable and runs on localhost only.</p>',
                '<ul>',
                '<li><a href="/login">/login</a> (SQLi via username/password)</li>',
                '<li><a href="/search?q=alice">/search?q=alice</a> (SQLi via q)</li>',
                '<li><a href="/xss?message=Hello">/xss?message=Hello</a> (Reflected XSS)</li>',
                '</ul>',
                '<p>Example SQLi payloads:</p>',
                '<pre>username: admin\npassword: anything\n-- or --\nusername: '"'"' OR '1'='1\npassword: '"'"'</pre>',
            ]
        ),
        mimetype='text/html',
    )


@app.route('/login', methods=['GET', 'POST'])
def login() -> Response:
    if request.method == 'GET':
        return Response(
            '\n'.join(
                [
                    '<h2>Login (Intentionally Vulnerable to SQLi)</h2>',
                    '<form method="post">',
                    '<label>Username <input name="username"></label><br>',
                    '<label>Password <input name="password" type="password"></label><br>',
                    '<button type="submit">Login</button>',
                    '</form>',
                ]
            ),
            mimetype='text/html',
        )

    username = request.form.get('username', '')
    password = request.form.get('password', '')

    # Intentionally UNSAFE query for learning (do not copy to real apps)
    query = f"SELECT id, username FROM users WHERE username = '{username}' AND password = '{password}'"

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(query)
        row = cur.fetchone()
    finally:
        conn.close()

    if row:
        return Response(f"<p>Welcome, {row[1]}!</p>", mimetype='text/html')
    return Response('<p>Login failed</p>', mimetype='text/html')


@app.get('/search')
def search() -> Response:
    q = request.args.get('q', '')
    # Intentionally vulnerable to SQLi (do not do this in real code)
    query = f"SELECT id, username FROM users WHERE username LIKE '%{q}%'"

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
    finally:
        conn.close()

    items = ''.join(f'<li>{uid}: {uname}</li>' for uid, uname in rows)
    return Response(
        f"<h2>Search results for '{q}'</h2><ul>{items or '<li>No results</li>'}</ul>",
        mimetype='text/html',
    )


@app.get('/xss')
def xss() -> Response:
    message = request.args.get('message', 'Hello')
    # Intentionally reflected without escaping (XSS)
    return Response(f"<p>Message: {message}</p>", mimetype='text/html')


if __name__ == '__main__':
    init_db()
    # Bind to localhost only, safe default
    app.run(host='127.0.0.1', port=8000, debug=False)
