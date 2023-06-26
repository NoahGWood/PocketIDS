
import asyncio
from fastapi import FastAPI, Request, WebSocket, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from configs import settings

app = FastAPI(
    title="PocketIDS",
    description="Pocket-Sized IDS System",
    version="1.0.0",
)

TEMPLATES = Jinja2Templates(directory="templates")

#with open(settings.LOG_FILE, 'r') as f:
#    data = iter(f.readlines())

@app.get("/")
@app.post("/")
async def index(request:Request):
    return TEMPLATES.TemplateResponse("index.html",
                                      context={"request":request,
                                               "url":settings.SERVER_ADDR,
                                               "port":settings.SERVER_PORT})

@app.websocket("/raw_log")
async def raw(websocket:WebSocket):
    await websocket.accept()
    with open(settings.LOG_FILE, 'r') as f:
        lines = f.readlines()
        count = len(lines)
        data = iter(lines)
        current = 0
        while True:
            current+=1
            if current >= count:
                data = iter(f.readlines())
            await asyncio.sleep(0.01)
            payload = next(data,"")
            await websocket.send_text(payload)

@app.get("/settings")
async def get_settings(request:Request):
    configs = {
        "AUTO_UPDATES":settings.AUTO_UPDATES,
        "UPDATE_INTERVAL":settings.UPDATE_INTERVAL,
        "UPDATES_URL":settings.UPDATES_URL,
        "UPDATES_FOLDER":settings.UPDATES_FOLDER,
        "UPDATES_FILE":settings.UPDATES_FILE,
        "NOTIFY_ON":settings.NOTIFY_ON,
        "ENABLE_SERVER":settings.ENABLE_SERVER,
        "SERVER_ADDR":settings.SERVER_ADDR,
        "SERVER_PORT":settings.SERVER_PORT,
        "LOG_LEVEL":settings.LOG_LEVEL,
        "LOG_FILE":settings.LOG_FILE,
    }
    print(settings.SERVER_ADDR, settings.SERVER_PORT)
    return TEMPLATES.TemplateResponse("settings.html",
                                      context={"request":request,
                                               "configs":configs})
@app.post("/settings")
async def post_settings(request:Request,                   
        AUTO_UPDATES: str = Form(),
        UPDATE_INTERVAL: str = Form(),
        UPDATES_URL: str = Form(),
        UPDATES_FOLDER: str = Form(),
        UPDATES_FILE: str = Form(),
        NOTIFY_ON: str = Form(),
        ENABLE_SERVER: str = Form(),
        SERVER_ADDR: str = Form(),
        SERVER_PORT: str = Form(),
        LOG_LEVEL: str = Form(),
        LOG_FILE: str = Form()):
    configs = {
        "AUTO_UPDATES":AUTO_UPDATES,
        "UPDATE_INTERVAL":UPDATE_INTERVAL,
        "UPDATES_URL":UPDATES_URL,
        "UPDATES_FOLDER":UPDATES_FOLDER,
        "UPDATES_FILE":UPDATES_FILE,
        "NOTIFY_ON":NOTIFY_ON,
        "ENABLE_SERVER":ENABLE_SERVER,
        "SERVER_ADDR":SERVER_ADDR,
        "SERVER_PORT":SERVER_PORT,
        "LOG_LEVEL":LOG_LEVEL,
        "LOG_FILE":LOG_FILE,
    }
    settings.CONF["DEFAULT"] = configs
    settings.SaveConf()
    return RedirectResponse("/")

@app.get("/log")
async def get_log(request:Request):
    return TEMPLATES.TemplateResponse("log.html",
                                      context={"request":request,
                                               "url":settings.SERVER_ADDR,
                                               "port":settings.SERVER_PORT})