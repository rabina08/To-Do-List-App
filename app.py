from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'todo.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date DATE,
            status TEXT CHECK(status IN ('Pending', 'In Progress', 'Completed')) DEFAULT 'Pending',
            label TEXT
        )''')

@app.before_request
def initialize():
    init_db()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    label = request.args.get('label')
    status = request.args.get('status')
    sort = request.args.get('sort')

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if label:
        query += " AND label = ?"
        params.append(label)

    if status:
        query += " AND status = ?"
        params.append(status)

    if sort == 'due_date':
        query += " ORDER BY due_date"

    conn = get_db_connection()
    tasks = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['due_date']
        label = request.form['label']
        status = request.form['status']

        conn = get_db_connection()
        conn.execute('INSERT INTO tasks (title, description, due_date, label, status) VALUES (?, ?, ?, ?, ?)',
                     (title, description, due_date, label, status))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('task_form.html', task=None, form_action=url_for('add_task'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['due_date']
        label = request.form['label']
        status = request.form['status']

        conn.execute('UPDATE tasks SET title=?, description=?, due_date=?, label=?, status=? WHERE id=?',
                     (title, description, due_date, label, status, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('task_form.html', task=task)

@app.route('/delete/<int:id>')
def delete_task(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
