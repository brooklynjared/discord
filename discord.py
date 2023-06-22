import os
import time
from email.mime import application
from dateutil.parser import isoparse
import requests
from decouple import config


CHANNEL_ID=config('CHANNEL_ID')
GUILD_ID=config('GUILD_ID')
BOT_TOKEN=config('BOT_TOKEN')



# Returns a Discord invite code
def get_invite():

    headers = {
      "Authorization": f"Bot {BOT_TOKEN}",
      "Content-type": "application/json"
    }

    body = {
      "max_age": 0,
      "max_uses": 1,
      "unique": True
    }
    endpoint=f"https://discord.com/api/v9/channels/{CHANNEL_ID}/invites"

    r = requests.post(endpoint, headers=headers, json=body)

    data = r.json()
    code = data['code']
    print(f"Invite Code: {code}")

    return code


# Returns a list of scheduled events for the guild, with handling for rate-limiting.
def get_events():

    headers = {
      "Authorization": f"Bot {BOT_TOKEN}"
    }

    endpoint=f"https://discord.com/api/v9/guilds/{GUILD_ID}/scheduled-events"

    r = requests.get(endpoint, headers=headers)

    if r.status_code == 200:
        data = r.json()
        events = data

        # convert ISO8601 dates to python datetime
        for event in events:
          event['scheduled_start_time'] = isoparse(event['scheduled_start_time'])

        return events

    elif r.status_code == 429:
        data = r.json()
        print("429 response.\n")
        print(data)

        # get the rate limiting wait period
        interval = data["retry_after"] + 0.5

        print(interval)

        # wait for the interval before trying again
        time.sleep(interval)
    
    else:
        status = r.status_code

        print(f"Error: status {status}")

        return f"Discord request error: status {status}"


# Creates a new event. (name, description, date, start_time, end_time, entity_type, location):
def add_event(name, entity_type, channel_id, description, start_datetime, end_datetime, location):

    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-type": "application/json"
    }

    endpoint=f"https://discord.com/api/v9/guilds/{GUILD_ID}/scheduled-events"

    body = {}

    if entity_type == 3:

      body = {
          "name": name,
          "description": description,
          "scheduled_start_time": start_datetime,
          "scheduled_end_time": end_datetime,
          "privacy_level": 2,
          "entity_type": 3,
          "entity_metadata": {
            "location": location
          }
        }
        
    elif entity_type == 2:
        body = {
          "name": name,
          "channel_id": channel_id,
          "description": description,
          "scheduled_start_time": start_datetime,
          "privacy_level": 2,
          "entity_type": 2
        }

    r = requests.post(endpoint, headers=headers, json=body)

    try:
        r.raise_for_status()
        response = r.json()
        print(response)
        return response
    except:
        return None


# Returns a guild object.
def get_guild():
    headers = {
      "Authorization": f"Bot {BOT_TOKEN}"
    }

    endpoint=f"https://discord.com/api/v9/guilds/{GUILD_ID}?with_counts=true"

    r = requests.get(endpoint, headers=headers)
    if r.status_code == 200:
        data = r.json()
        guild = data
    else:
      guild = None

    return guild
