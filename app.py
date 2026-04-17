from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'games.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS genres (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT    UNIQUE NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            price       REAL    NOT NULL DEFAULT 0,
            image       TEXT,
            max_players INTEGER NOT NULL DEFAULT 1,
            genre_id    INTEGER,
            FOREIGN KEY (genre_id) REFERENCES genres(id)
        )
    ''')

    default_genres = ['Co-op', 'Farming Sim', 'MMO', 'RPG', 'FPS']
    for g in default_genres:
        cur.execute('INSERT OR IGNORE INTO genres (name) VALUES (?)', (g,))

    conn.commit()
    conn.close()


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    conn = get_db()
    games = conn.execute('''
        SELECT g.id, g.name, g.price, g.image, g.max_players,
               genres.name AS genre_name
        FROM games g
        LEFT JOIN genres ON g.genre_id = genres.id
        ORDER BY g.id DESC
    ''').fetchall()
    conn.close()
    return render_template('index.html', games=games)


@app.route('/append', methods=['GET', 'POST'])
def append():
    conn = get_db()
    genres = conn.execute('SELECT * FROM genres ORDER BY name').fetchall()

    if request.method == 'POST':
        name        = request.form['name'].strip()
        price       = float(request.form['price'] or 0)
        image       = request.form['image'].strip()
        max_players = int(request.form['max_players'] or 1)
        genre_id    = request.form['genre_id'] or None

        conn.execute(
            'INSERT INTO games (name, price, image, max_players, genre_id) VALUES (?, ?, ?, ?, ?)',
            (name, price, image, max_players, genre_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('append.html', genres=genres)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    game   = conn.execute('SELECT * FROM games WHERE id = ?', (id,)).fetchone()
    genres = conn.execute('SELECT * FROM genres ORDER BY name').fetchall()

    if not game:
        conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        name        = request.form['name'].strip()
        price       = float(request.form['price'] or 0)
        image       = request.form['image'].strip()
        max_players = int(request.form['max_players'] or 1)
        genre_id    = request.form['genre_id'] or None

        conn.execute(
            'UPDATE games SET name=?, price=?, image=?, max_players=?, genre_id=? WHERE id=?',
            (name, price, image, max_players, genre_id, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit.html', game=game, genres=genres)


@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    conn.execute('DELETE FROM games WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
