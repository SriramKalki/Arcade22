from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_leaderboard_data(timezones=None, sort_by="total_hours"):
    db = sqlite3.connect('slack_users.db')
    cursor = db.cursor()
    query = f'SELECT id, name, timezone, total_hours, tickets FROM users'
    params = []
    
    if timezones:
        placeholders = ','.join('?' for _ in timezones)
        query += f' WHERE timezone IN ({placeholders})'
        params.extend(timezones)
    
    if sort_by == "tickets":
        query += ' ORDER BY tickets DESC'
    else:
        query += ' ORDER BY total_hours DESC'
    
    cursor.execute(query, params)
    data = cursor.fetchall()
    db.close()
    return data

def get_timezones():
    db = sqlite3.connect('slack_users.db')
    cursor = db.cursor()
    cursor.execute('SELECT DISTINCT timezone FROM users')
    timezones = cursor.fetchall()
    db.close()
    return [tz[0] for tz in timezones]

@app.route('/', methods=['GET', 'POST'])
def leaderboard():
    selected_timezones = request.form.getlist('timezones')
    sort_by = request.form.get('sort_by', 'total_hours')
    data = get_leaderboard_data(selected_timezones, sort_by)
    timezones = get_timezones()
    return render_template('leaderboard.html', users=data, timezones=timezones, selected_timezones=selected_timezones, sort_by=sort_by)

if __name__ == '__main__':
    app.run(debug=True)
