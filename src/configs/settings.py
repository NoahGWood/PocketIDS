import logging
import configparser
import tempfile

CONF = configparser.ConfigParser()
CONF.read("configs/default.ini")

# Updates (known bad IP addresses)
AUTO_UPDATES = CONF["DEFAULT"]["AUTO_UPDATES"]
UPDATE_INTERVAL = int(CONF["DEFAULT"]["UPDATE_INTERVAL"])
UPDATES_URL = CONF["DEFAULT"]["UPDATES_URL"]
UPDATES_FOLDER = CONF["DEFAULT"]["UPDATES_FOLDER"]
UPDATES_FILE = CONF["DEFAULT"]["UPDATES_FILE"]

# Notifications
NOTIFY_ON = CONF["DEFAULT"]["NOTIFY_ON"] # (low, normal, critical)

# Server
ENABLE_SERVER = CONF["DEFAULT"]["ENABLE_SERVER"]
SERVER_ADDR = CONF["DEFAULT"]["SERVER_ADDR"]
SERVER_PORT = int(CONF["DEFAULT"]["SERVER_PORT"])

# Logging
if CONF["DEFAULT"]["LOG_FILE"] == "TMP":
    LOG_FILE = tempfile.mktemp() # Volatile Logging 
else:
    LOG_FILE = CONF["DEFAULT"]["LOG_FILE"]  # Persistent Logging

ll = CONF["DEFAULT"]["LOG_LEVEL"]
if ll == "ERROR":
    LOG_LEVEL = logging.ERROR
elif ll == "WARNING":
    LOG_LEVEL = logging.WARNING
elif ll == "INFO":
    LOG_LEVEL = logging.INFO
else:
    LOG_LEVEL = logging.DEBUG

_LOG_FORMAT = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOGGER = logging.getLogger("PocketIDS")
_FILE_HANDLER = logging.FileHandler(LOG_FILE)
_FILE_HANDLER.setLevel(LOG_LEVEL)
_FILE_HANDLER.setFormatter(_LOG_FORMAT)
_STREAM_HANDLER = logging.StreamHandler()
_STREAM_HANDLER.setLevel(LOG_LEVEL)
_STREAM_HANDLER.setFormatter(_LOG_FORMAT)
LOGGER.setLevel(LOG_LEVEL)
LOGGER.addHandler(_FILE_HANDLER)
LOGGER.addHandler(_STREAM_HANDLER)

def SaveConf():
    with open("configs/default.ini", "w") as configfile:
        CONF.write(configfile)