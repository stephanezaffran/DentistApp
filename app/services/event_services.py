from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from app.services import google_service
import pytz
from app.services.whatsapp_service import send_patient_whatsapp_message
import urllib.parse


def get_event_by_date_from_calendar():

    print('entered to get_event_by_date() ')

    israel_timezone = pytz.timezone('Israel')
    now = datetime.now(israel_timezone)

    # Ajouter 2 jours à la date actuelle
    reminder_2_days = now + timedelta(days=2)
    reminder_1_day = now + timedelta(days=1)

    # Formater la nouvelle date au format "aaaa-mm-jj"
    date_2_days = reminder_2_days.date()
    date_1_day = reminder_1_day.date()

    time_min_2_day = datetime.combine(date_2_days, datetime.min.time()).isoformat() + 'Z'
    time_max_2_day = datetime.combine(date_2_days, datetime.max.time()).isoformat() + 'Z'

    time_min_1_day = datetime.combine(date_1_day, datetime.min.time()).isoformat() + 'Z'
    time_max_1_day = datetime.combine(date_1_day, datetime.max.time()).isoformat() + 'Z'

    events_2 = google_service.get_events(time_min_2_day, time_max_2_day)
    doctor_message = f"sended message 2 days appointments\n {send_2_days_message(events_2)}"
    send_patient_whatsapp_message(None, doctor_message)

    events_1 = google_service.get_events(time_min_1_day, time_max_1_day)
    doctor_message = f"sended message for tomorrow appointments\n {send_1_days_message(events_1)}"
    send_patient_whatsapp_message(None, doctor_message)


def split_data_from_event(event):

    # Convert the string to datetime object
    datetime_start = datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
    datetime_end = datetime.strptime(event['end']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')

    # Extract the date and time components
    start_date = datetime_start.date()
    start_time = datetime_start.time()

    end_date = datetime_end.date()
    end_time = datetime_end.time()

    message = event.get('description', '')
    name = event.get('extendedProperties', '')['private']['name']
    surname = event.get('extendedProperties', '')['private']['surname']
    identity_number = event.get('extendedProperties', '')['private']['identity_number']
    email = event.get('extendedProperties', '')['private']['email']

    # Check if the phone number starts with '0'
    phone_number = event.get('extendedProperties', '')['private']['phone_number']
    if phone_number.startswith('0'):
        # Replace the leading '0' with '972'
        transformed_number = '972' + phone_number[1:]
    else:
        # Phone number doesn't start with '0', leave it as is
        transformed_number = phone_number

    splited_data = {key: value for key, value in [('start_date', start_date), ('start_time', start_time), ('end_date', end_date),
                                             ('end_time', end_time), ('message', message),  ('name', name), ('phone_number', transformed_number),
                                             ('surname', surname),  ('identity_number', identity_number), ('email', email)]}

    # print(f"transformed_number: {transformed_number}")
    # print(f"start_date: {start_date}  -  start_time: {start_time}")
    # print(f"end_date: {end_date}  -  end_time: {end_time}")

    return splited_data


def send_2_days_message(events):
    sended_message = ""
    if events:
        for event in events:
            if event.get('extendedProperties')['private']['app'] == 'DentistApp':
                # print(f" exist extendedProperties : {event.get('extendedProperties')}")
                splited_event = split_data_from_event(event)
                message = f"הודעת תזכורת.  שלום  {splited_event['surname']}  {splited_event['name']} יש לך פגישה במרפאת שיננים ברוכין ביום {splited_event['start_date']} בשעה {splited_event['start_time']} נה לאשר נוככות או לבטל עד 24 שעות לפני הפגישה . בברכה"
                valid = send_patient_whatsapp_message(splited_event, message)
                if valid == 200:
                    sended_message += f"sent message to {splited_event['surname']}  {splited_event['name']} for appointement on {splited_event['start_date']} at {splited_event['start_time']}\n"

    return sended_message


def send_1_days_message(events):
    sended_message = ""
    if events:
        for event in events:
            if event.get('extendedProperties')['private']['app'] == 'DentistApp':
                # print(f" exist extendedProperties : {event.get('extendedProperties')}")
                splited_event = split_data_from_event(event)
                print(message)
                message = f"הודעת תזכורת.  שלום  {splited_event['surname']}  {splited_event['name']} יש לך פגישה במרפאת שיננים ברוכין מחר בשעה {splited_event['start_time']}  בברכה "
                valid = send_patient_whatsapp_message(splited_event, message)
                if valid == 200:
                    sended_message += f"sent message to {splited_event['surname']}  {splited_event['name']} for appointement on tomorrow at {splited_event['start_time']}\n"

    return sended_message


def create_new_event(name, surname, phone_number, email, message, identity_number, date, start_time, end_time):
    # Call the Calendar API
    location = "israel brukhin"
    datetime_str = f'{date} {start_time}'
    event_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    formated_start_time = event_datetime.isoformat()
    datetime_str = f'{date} {end_time}'
    event_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    formated_end_time = event_datetime.isoformat()

    event = {
        'summary': f'evenement:  {name} {surname} {identity_number}',
        'location': location,
        'description': message,
        'start': {
            'dateTime': formated_start_time,
            'timeZone': 'Israel',
        },
        'end': {
            'dateTime': formated_end_time,
            'timeZone': 'Israel',
        },
        # 'recurrence': [
        #     'RRULE:FREQ=DAILY;COUNT=2'
        # ],
        'attendees': [
            {'email': 'lpage@example.com'},

        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
        'extendedProperties': {
            'private': {
                'app': 'DentistApp',
                'name': name,
                'surname': surname,
                'phone_number': phone_number,
                'identity_number': identity_number,
                'email': email
            }
        }
    }

    event_id = google_service.create_event(event)
    return event_id


def update_event(message, date, start_time, end_time, calendar_id):

    datetime_str = f'{date} {start_time}'
    event_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    formated_start_time = event_datetime.isoformat()

    datetime_str = f'{date} {end_time}'
    event_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    formated_end_time = event_datetime.isoformat()

    event = google_service.get_specific_event(calendar_id)

    event['start']['dateTime'] = formated_start_time
    event['end']['dateTime'] = formated_end_time
    event['description'] = message

    google_service.update_event(calendar_id, event)


def delete_event(calendar_id):
    google_service.delete_event(calendar_id)


def change_google_account():
    google_service.change_google_account()


scheduler = BackgroundScheduler(timezone='Asia/Jerusalem')
#scheduler.add_job(get_event_by_date, 'cron', hour=9, minute=0)  # Schedule function to run every day at 9:00
scheduler.add_job(get_event_by_date_from_calendar, 'interval', seconds=1000)
scheduler.start()
