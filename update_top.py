import sqlite3
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time
import requests

# Initialize with your Slack token
token = ''
client = WebClient(token=token)

# Connect to SQLite database
db = sqlite3.connect('slack_users.db')
cursor = db.cursor()


def fetch_users_from_db():
    cursor.execute('SELECT id FROM users')
    return cursor.fetchall()


def fetch_hours(user_id):
    try:
        response = requests.get(f'https://hackhour.hackclub.com/api/stats/{user_id}')
        data = response.json()
        if data['ok']:
            total_hours = data['data']['total'] / 60  # Convert minutes to hours
            return total_hours
        else:
            print(f"Error fetching stats for user {user_id}: {data['error']}")
            return None
    except Exception as e:
        print(f"Error fetching stats for user {user_id}: {e}")
        return None



def update_hours(user_id, total_hours):
    cursor.execute('''
        UPDATE users SET total_hours = ? WHERE id = ?
    ''', (total_hours, user_id))
    db.commit()

def main(channel_id):
    users = fetch_users_from_db()
    for i, user in enumerate(users):
        user_id = user[0]
        total_hours = fetch_hours(user_id)
        if total_hours:
            update_hours(user_id, total_hours)
            print(f"Updated total_hours for user {user_id}")


# Run the main function
if __name__ == '__main__':
    channel_id = 'C06SBHMQU8G'  # Replace with your channel ID
    main(channel_id)
    db.close()            