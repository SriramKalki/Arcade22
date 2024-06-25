import sqlite3
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time

# Initialize with your Slack token
token = ''
client = WebClient(token=token)

# Connect to SQLite database
db = sqlite3.connect('slack_users.db')
cursor = db.cursor()

# # Ensure the table has a column for timezones
# cursor.execute('''
#     ALTER TABLE users ADD COLUMN timezone TEXT
# ''')
# db.commit()

def fetch_users_from_db():
    cursor.execute('SELECT id FROM users')
    return cursor.fetchall()

def fetch_user_timezone(user_id):
    try:
        response = client.users_info(user=user_id)
        if response['ok']:
            return response['user']['tz']
        else:
            print(f"Error fetching profile for user {user_id}: {response['error']}")
            return None
    except SlackApiError as e:
        print(f"Error fetching profile for user {user_id}: {e.response['error']}")
        return None

def update_timezone(user_id, timezone):
    cursor.execute('''
        UPDATE users SET timezone = ? WHERE id = ?
    ''', (timezone, user_id))
    db.commit()

def main():
    users = fetch_users_from_db()
    for i, user in enumerate(users):
        
        user_id = user[0]
        timezone = fetch_user_timezone(user_id)
        
        update_timezone(user_id, timezone)
        print(f"Updated timezone for user {user_id} to {timezone}")

if __name__ == '__main__':
    main()
    db.close()
