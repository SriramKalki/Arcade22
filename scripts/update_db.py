import os
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# Initialize with your Slack token
token = os.environ['BOT_API']
client = WebClient(token=token)

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

def store_user_info(user_id, name, timezone, total_hours):
    user_ref = db.collection('users').document(user_id)
    user_ref.set({
        'id': user_id,
        'name': name,
        'timezone': timezone,
        'total_hours': total_hours,
        'tickets': 0  # Default value
    }, merge=True)

def main(channel_id):
    channel_members = fetch_channel_members(channel_id)
    for user in channel_members:
        total_hours = fetch_total_hours(user)
        if total_hours is None or total_hours < 40:
            continue
        
        stats = fetch_user(user)
        name = stats['profile']['real_name']
        timezone = fetch_user_timezone(user).split('/')[0] if 'tz' in stats else None
        store_user_info(user, name, timezone, total_hours)
        print(f"Updated {user}")

# Run the main function
if __name__ == '__main__':
    channel_id = 'C06SBHMQU8G'  # Replace with your channel ID, this is the one for #arcade
    main(channel_id)
