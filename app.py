from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_leaderboard_data(timezone=None):
    db = sqlite3.connect('slack_users.db')
    cursor = db.cursor()
    if timezone:
        cursor.execute('SELECT id, name, timezone, total_hours,tickets FROM users WHERE timezone = ? ORDER BY total_hours DESC', (timezone,))
    data = cursor.fetchall()
    print(data)
    db.close()
    return data

def get_timezones():
    db = sqlite3.connect('slack_users.db')
    cursor = db.cursor()
    cursor.execute('SELECT DISTINCT timezone FROM users')
    timezones = cursor.fetchall()
    db.close()
    print(timezones)
    return [tz[0] for tz in timezones]

@app.route('/', methods=['GET', 'POST'])
def leaderboard():
    selected_timezone = request.form.get('timezone')
    data = get_leaderboard_data(selected_timezone)
    timezones = get_timezones()
    return render_template('leaderboard.html', users=data, timezones=timezones, selected_timezone=selected_timezone)

if __name__ == '__main__':
    app.run(debug=True)
