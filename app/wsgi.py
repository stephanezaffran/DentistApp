from app import create_app
from services.event_services import scheduler

if __name__ == '__main__':
    scheduler.start()
    create_app().run(host='localhost', port=5000)

