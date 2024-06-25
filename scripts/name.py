import sqlite3
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time

# Initialize with your Slack token
token = 'null'
client = WebClient(token=token)

# Connect to SQLite database
db = sqlite3.connect('slack_users.db')
cursor = db.cursor()

# Ensure the table has a column for profile names
cursor.execute('''
    ALTER TABLE users ADD COLUMN profile_name TEXT
''')
db.commit()

def fetch_users_from_db():
    cursor.execute('SELECT id FROM users')
    return cursor.fetchall()

def fetch_user_profile_name(user_id):
    try:
        response = client.users_info(user=user_id)
        if response['ok']:
            return response['user']['profile']['real_name']
        else:
            print(f"Error fetching profile for user {user_id}: {response['error']}")
            return None
    except SlackApiError as e:
        print(f"Error fetching profile for user {user_id}: {e.response['error']}")
        return None

def update_profile_name(user_id, profile_name):
    cursor.execute('''
        UPDATE users SET profile_name = ? WHERE id = ?
    ''', (profile_name, user_id))
    db.commit()

def main():
    users = fetch_users_from_db()
    for i, user in enumerate(users):
        user_id = user[0]
        profile_name = fetch_user_profile_name(user_id)
        if profile_name:
            update_profile_name(user_id, profile_name)
            print(f"Updated profile name for user {user_id} to {profile_name}")

if __name__ == '__main__':
    main()
    db.close()
