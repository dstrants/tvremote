from fastapi import FastAPI

from remote import Remote


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Let's remote your tv"}


@app.get("/configure/{tv_ip}")
async def configure(tv_ip: str):
    Remote(tv_ip)
    return {"message": "Configuration done!"}


@app.get("/turnoff")
async def turnoff():
    remote = Remote()
    payload = remote.turn_off()
    return {"message": "TV closed", "payload": payload}


# Volume Endpoints

@app.get("/volume/mute")
async def mute():
    remote = Remote()
    payload = remote.mute()
    return {"message": "TV muted", "payload": payload}


@app.get("/volume/unmute")
async def unmute():
    remote = Remote()
    payload = remote.mute(False)
    return {"message": "TV muted", "payload": payload}


# Channel Endpoints

@app.get("/channels")
async def channels_list(sync: bool = False):
    remote = Remote()
    payload = remote.get_channels(sync)
    return {"message": "Channels fetched", "payload": payload}


@app.get("/channel/up")
async def channels_up():
    remote = Remote()
    payload = remote.channel_up()
    return {"message": "Channels up", "payload": payload}


@app.get("/channel/down")
async def channels_down():
    remote = Remote()
    payload = remote.channel_down()
    return {"message": "Channels down", "payload": payload}


@app.get("/channel/current")
async def channels_current():
    remote = Remote()
    payload = remote.get_current_channel()
    return {"message": "Channels down", "payload": payload}


# Application Endpoints

@app.get("/apps")
async def apps_list(sync: bool = False):
    remote = Remote()
    payload = remote.get_apps(sync)
    return {"message": "Channels fetched", "payload": payload}
