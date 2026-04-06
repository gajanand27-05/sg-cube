from fastapi import FastAPI
from pydantic import BaseModel
import datetime

app = FastAPI()

class Command(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "SG CUBE AI Server Running"}

@app.post("/command")
def process_command(cmd: Command):

    command = cmd.text.lower()

    if "time" in command:
        now = datetime.datetime.now().strftime("%H:%M")
        return {"response": f"The time is {now}"}

    elif "hello" in command:
        return {"response": "Hello, I am SG Cube"}

    else:
        return {"response": "Command not recognized"}