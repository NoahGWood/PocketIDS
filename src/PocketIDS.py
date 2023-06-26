#!/usr/bin/python3
"""PocketIDS.py

The main PocketIDS program
"""
import os
import uvicorn
OLD_ROOT = os.getcwd()
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT_DIR)
from threading import Thread
from configs import settings
from updates import update

def notify(level, summary, body):
    print("P:", level, summary, body)
    if level == "force":
        level = "low"
        os.popen(f"notify-send -u {level} -c a {summary} '{body}'")
    elif level == settings.NOTIFY_ON:
        os.popen(f"notify-send -u {level} -c a {summary} '{body}'")
    if level == "critical":
        settings.LOGGER.error(msg=f"{level} {summary} {body}")
    elif level == "normal":
        settings.LOGGER.warning(msg=f"{level} {summary} {body}")
    else:
        settings.LOGGER.info(msg=f"{level} {summary} {body}")

def main():
    notify("force","PocketIDS","PocketIDS has started.")
    notify("low", "PocketIDS", "Starting TCPDump.")
    x = f"{os.getcwd()}/PocketIDS -i {os.getcwd()}/{settings.UPDATES_FOLDER}/{settings.UPDATES_FILE} >> {settings.LOG_FILE}"
    print(x)
    os.popen(x)

if __name__ in '__main__':
    update.Update()
    thread = Thread(target=main, daemon=True)
    thread.start()
    print("Started")
    if settings.ENABLE_SERVER:
        notify("force",
               "PocketIDS",
               f"Starting Server on:\nhttp://{settings.SERVER_ADDR}:{settings.SERVER_PORT}")
        uvicorn.run("server:app", host=settings.SERVER_ADDR,
                    port=settings.SERVER_PORT,
                    reload=False)
        notify("force","PocketIDS","Shutting Down.")
    os.chdir(OLD_ROOT)