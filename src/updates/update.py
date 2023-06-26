import os
import subprocess
import datetime
from configs import settings


def NeedsUpdate():
    """Returns whether file needs updated.
    """
    file = os.path.join(settings.UPDATES_FOLDER, settings.UPDATES_FILE)
    if not os.path.exists(file):
        return True
    if (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(file))).total_seconds() > settings.UPDATE_INTERVAL:
        return True

def PostProcessing():
    """PostProcessing() is called after a successful file download
    to complete any updating.

    Feel free to add additional functionality as needed.
    """
    pass

def Update():
    # Download the latest bad IP address
    if settings.AUTO_UPDATES:
        if NeedsUpdate():
            f = os.path.join(settings.UPDATES_FOLDER, settings.UPDATES_FILE)
            exists = os.path.exists(f)
            try:
                # save old file
                if exists:
                    os.rename(f, settings.UPDATES_FOLDER + "/tmp")
                subprocess.check_output(["wget", settings.UPDATES_URL,
                                         "-P", settings.UPDATES_FOLDER])
                # Download successful, delete old file.
                if exists:
                    os.remove(f)
                # Run any post processing
                PostProcessing()
            except subprocess.CalledProcessError as e:
                print("Exception: ", e.output)
                settings.LOGGER.error(f"Error updating. {e}")
                # Restore old file
                if exists:
                    os.rename(settings.UPDATES_FOLDER + "/tmp", f)
            print("Updates completed")
