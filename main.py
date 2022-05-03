"""Entrypoint to the application"""
import time
import threading
import requests

from app import app as flask_app


def start_loop():
    """loops until app is started"""
    def check_status():
        not_started = True
        while not_started:
            try:
                req = requests.get('https://127.0.0.1:8080/', verify=False)
                if req.status_code == 200:
                    print('Server started',flush=True)
                    not_started = False
            except: # pylint: disable=bare-except
                print('starting ...',flush=True)
            time.sleep(10)
    thread = threading.Thread(target=check_status)
    thread.start()

if __name__ == "__main__":
    start_loop()
    flask_app.run(host="0.0.0.0", port=8080,ssl_context='adhoc')
