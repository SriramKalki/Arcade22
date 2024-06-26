import os
import sqlite3
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Initialize with your Slack token
token = ''
client = WebClient(token=token)

# Connect to SQLite database (or create it if it doesn't exist)
db = sqlite3.connect('slack_users.db')
cursor = db.cursor()


# Create table to store user data
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT,
        timezone TEXT,
        total_hours REAL
        
    )
''')
db.commit()

def fetch_user(user_id):
    try:
        response = client.users_info(user=user_id)
        if response['ok']:
            return response['user']
        else:
            print(f"Error fetching profile for user {user_id}: {response['error']}")
            return None
    except SlackApiError as e:
        print(f"Error fetching profile for user {user_id}: {e.response['error']}")
        return None


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

def fetch_user_timezone(user_id):
    try:
        response = client.users_info(user=user_id)
        if response['ok'] and 'tz' in response['user']:
            return response['user']['tz']
        else:
            print(f"Error fetching profile for user {user_id}: {response['error']}")
            return None
    except SlackApiError as e:
        print(f"Error fetching profile for user {user_id}: {e.response['error']}")
        return None

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

def store_user_info(user,name,timezone,total_hours):
    cursor.execute('''
        INSERT OR REPLACE INTO users (id, name,timezone,total_hours) VALUES (?, ?, ?, ?)
    ''', (user, name, timezone,total_hours))
    db.commit()

def main(channel_id):
    channel_members = fetch_channel_members(channel_id)
    print(channel_members)
    for user in channel_members:
        total_hours = fetch_total_hours(user)
        if total_hours is None or total_hours < 40:
            continue
        
        stats = fetch_user(user)
        name = stats['profile']['real_name']
        if 'tz' in stats:
            timezone = fetch_user_timezone(user)
        else:
            timezone = None    
        
        store_user_info(user,name,timezone,total_hours)
        print(f"Updated {user}")

# Run the main function
if __name__ == '__main__':
    channel_id = 'C06SBHMQU8G'  # Replace with your channel ID
    main(channel_id)
    db.close()            