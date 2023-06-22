import requests

from flask import redirect, url_for
from whatsapp_api_client_python import API, response

from pathlib import Path
import os.path
import json


def get_project_root_dir():
    return Path(__file__).absolute().parent.parent.parent


def load_whatsapp_credentials():
    # if os.path.isfile('whatsapp_credentials.json'):
    root_dir = get_project_root_dir()
    whatsapp_credentials_path = f'{root_dir}\\credentials_data\\whatsapp_credentials.json'
    if os.path.exists(whatsapp_credentials_path):
        with open(whatsapp_credentials_path, 'r') as file:
            credentials = json.load(file)
            print(f"{credentials.get('cabinet')['id_instance']}, {credentials.get('cabinet')['token']}")
        return credentials.get('cabinet')['id_instance'], credentials.get('cabinet')['token']
    else:
        print("os.path.not.exists")
        return None, None


def send_patient_whatsapp_message(event, message):
    id_instance,api_token_instance = load_whatsapp_credentials()
    green_api = API.GreenApi(id_instance, api_token_instance)
    try:
        # print(f'send_patient_whatsapp_message event: {event}')
        response = green_api.sending.sendMessage(f'{972584868051}@c.us', f"{message}")
        return response.code

    except requests.HTTPError as e:

        # Handle API exceptions
        print(f"API Exception: {e.response.status_code} - {e.response.text}")

    except Exception as e:
        # Handle other exceptions
        print(f"Error occurred: {str(e)}")


load_whatsapp_credentials()