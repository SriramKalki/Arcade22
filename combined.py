import os
import sqlite3
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Initialize with your Slack token
token = 'null'
client = WebClient(token=token)

# Connect to SQLite database (or create it if it doesn't exist)
db = sqlite3.connect('slack_users.db')
cursor = db.cursor()

# Create table to store user data
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        total_hours REAL
    )
''')
db.commit()

def fetch_channel_members(channel_id):
    members = []
    cursor = None
    while True:
        try:
            response = client.conversations_members(channel=channel_id, cursor=cursor)
            if response['ok']:
                members.extend(response['members'])
                cursor = response['response_metadata'].get('next_cursor')
                print("ok")
                if not cursor:
                    break
            else:
                print('Error fetching channel members:', response['error'])
                break
        except SlackApiError as e:
            print('Error fetching channel members:', e.response['error'])
            break
    return members

def fetch_users():
    users = []
    cursor = None
    while True:
        try:
            response = client.users_list(cursor=cursor)
            if response['ok']:
                users.extend(response['members'])
                cursor = response['response_metadata'].get('next_cursor')
                if not cursor:
                    break
            else:
                print('Error fetching users:', response['error'])
                break
        except SlackApiError as e:
            print('Error fetching users:', e.response['error'])
            break
    return users

def fetch_total_hours(user_id):
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

def store_user_info(user,total_hours):
    cursor.execute('''
        INSERT OR REPLACE INTO users (id, total_hours) VALUES (?, ?)
    ''', (user, total_hours))
    db.commit()

def main(channel_id):
    # Fetch members of the specified channel
    channel_members = fetch_channel_members(channel_id)
    print(channel_members)
    # Fetch total hours for each user and store in the database
    for user in channel_members:
        total_hours = fetch_total_hours(user)
        if total_hours is not None:
            store_user_info(user,total_hours)
            print(f"Updated total hours for user {user}")

# Run the main function
if __name__ == '__main__':
    channel_id = 'C06SBHMQU8G'  # Replace with your channel ID
    main(channel_id)
    db.close()
