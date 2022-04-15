from app import app as flask_app
import time
import requests
import threading

def start_loop():
    def check_status():
        not_started = True
        while not_started:
            try:
                r = requests.get('https://127.0.0.1:8080/', verify=False)
                if r.status_code == 200:
                    print('Server started',flush=True)
                    not_started = False
            except:
                print('starting ...',flush=True)
            time.sleep(10)
    thread = threading.Thread(target=check_status)
    thread.start()

if __name__ == "__main__":
    start_loop()
    flask_app.run(host="0.0.0.0", port=8080,ssl_context='adhoc')



