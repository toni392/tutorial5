import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["ecse3038"]
devices = db["tutorial5"]

app = FastAPI()


class Device(BaseModel):
    name: str
    room: str
    temp: float
    online: bool


# Your handlers go below this line.

#task 1: get all devices
@app.get("/devices")
def get_devices():
    return list(devices.find({}, {"_id":0}))

#task 2: get a specific device
@app.get("/devices/{name}")
def get_device(name: str):
    device = devices.find_one({"name": name}, {"_id":0})
    if device is None:
        raise HTTPException(status_code=404, detail=f"Device '{name}' not found")
    return device

#task 3: add a device
@app.post("/devices", status_code=201)
def create_device(device: Device):
    if devices.find_one({"name": device.name}):
        raise HTTPException(status_code=409, detail=f"Device '{device.name}' already exists")
    devices.insert_one(device.model_dump())
    return device

#task 4: put a device
@app.put("/devices/{name}")
def update_device(name: str, device: Device):
    if device.name != name:
        raise HTTPException(status_code=409, detail="Name in body does not match name in URL")
    result = devices.replace_one({"name": name}, device.model_dump())
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="No device called " + name)
    return device
