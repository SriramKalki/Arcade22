from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_leaderboard_data():
    db = sqlite3.connect('slack_users.db')
    cursor = db.cursor()
    cursor.execute('SELECT profile_name, total_hours, tickets FROM users ORDER BY total_hours DESC')
    data = cursor.fetchall()
    db.close()
    return data

@app.route('/')
def leaderboard():
    data = get_leaderboard_data()
    return render_template('leaderboard.html', users=data)

if __name__ == '__main__':
    app.run(debug=True)

