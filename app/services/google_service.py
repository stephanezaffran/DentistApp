from __future__ import print_function

import datetime
import os.path
import requests

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/calendar']


# Fonction utilitaire pour obtenir le jeton d'accès de l'utilisateur
def get_access_token():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('credentials_data/token.json'):
        creds = Credentials.from_authorized_user_file('credentials_data/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials_data/credentials.json', SCOPES)
            creds = flow.run_local_server(port=8000)
        # Save the credentials for the next run
        with open('credentials_data/token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def revoke_credentials():
    if os.path.exists('credentials_data/token.json'):
        with open('credentials_data/token.json', 'r') as token_file:
            token_data = token_file.read()

        # Send a POST request to revoke the token
        response = requests.post('https://oauth2.googleapis.com/revoke',
                                 params={'token': token_data},
                                 headers={'content-type': 'application/x-www-form-urlencoded'})

        if response.status_code == 200:
            # Token revoked successfully
            os.remove('credentials_data/token.json')
            print('Credentials revoked and token file deleted.')
        else:
            print('Failed to revoke credentials.')
    else:
        print('No token file found.')


def change_google_account():
    revoke_credentials()
    flow = InstalledAppFlow.from_client_secrets_file('credentials_data/credentials.json', SCOPES)
    creds = flow.run_local_server(port=8000)
    # Save the credentials for the next run
    with open('credentials_data/token.json', 'w') as token:
        token.write(creds.to_json())
    return creds


def get_specific_event(calendar_id):
    creds = get_access_token()
    try:
        service = build('calendar', 'v3', credentials=creds)
        event = service.events().get(calendarId='primary', eventId=calendar_id).execute()
        if not event:
            print('No upcoming events found.')
            return None
        return event

    except HttpError as error:
        print(f'An error occurred:  {error}')


def get_events(time_min, time_max):
    creds = get_access_token()
    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API

        events_result = service.events().list(calendarId='primary', timeMin=time_min, timeMax=time_max, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        return events
    except HttpError as error:
        print(f'An error occurred:  {error}')


def create_event(event):
    creds = get_access_token()
    try:
        service = build('calendar', 'v3', credentials=creds)

        return service.events().insert(calendarId='primary', body=event).execute().get('id')

    except HttpError as error:
        print(f'An error occurred:  {error}')


def update_event(calendar_id, event):
    creds = get_access_token()
    try:
        service = build('calendar', 'v3', credentials=creds)
        service.events().update(calendarId='primary', eventId=calendar_id, body=event).execute()
        return None

    except HttpError as error:
        print(f'An error occurred:  {error}')
        return error


def delete_event(calendar_id):
    creds = get_access_token()
    try:
        service = build('calendar', 'v3', credentials=creds)
        service.events().delete(calendarId='primary', eventId=calendar_id).execute()
        return None

    except HttpError as error:
        print(f'An error occurred:  {error}')
        return error




