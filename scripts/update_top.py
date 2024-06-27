import sqlite3
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import time
import requests
import os
# Initialize with your Slack token
token = os.environ['USER_API']
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


def search_messages_for_user_mentions(user_id):
    mention_count = 0
    try:
        response = client.search_messages(
            query=f"from:hakkuun <@{user_id}> approved",
            count=1000
        )
        if response['ok']:
            messages = response['messages']['total']
            mention_count = messages
        else:
            print(f"Error searching messages for user {user_id}: {response['error']}")
    except SlackApiError as e:
        print(f"Error searching messages for user {user_id}: {e.response['error']}")
    return mention_count

def update_mention_count(user_id, count):
    cursor.execute('''
        UPDATE users SET tickets = ? WHERE id = ?
    ''', (count, user_id))
    db.commit()


def main(channel_id):
    users = fetch_users_from_db()
    # Update total hours for each user
    for i, user in enumerate(users):
        user_id = user[0]
        total_hours = fetch_hours(user_id)
        if total_hours:
            update_hours(user_id, total_hours)
            print(f"Updated total_hours for user {user_id}")

    # Update mention counts for each user
    for i, user in enumerate(users):
        if i > 0 and i % 45 == 0:
            print("Rate limit reached. Sleeping for 60 seconds...")
            time.sleep(60)
        
        user_id = user[0]  # Get the user_id from the tuple
        counted = search_messages_for_user_mentions(user_id)
        update_mention_count(user_id, counted)
        
        print(f"Updated mention count for user {user_id} to {counted}")


# Run the main function
if __name__ == '__main__':
    channel_id = 'C06SBHMQU8G'  # Replace with your channel ID, this is the one for #arcade
    main(channel_id)
    db.close()
