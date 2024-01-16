from fastapi import FastAPI
import os

app = FastAPI()

server_id=os.getenv("SERVER_ID")

@app.get("/home")
def server_info():
    return {
        "message" : "Hello from Server:{}".format(server_id),
        "status" : "successful"
    }

@app.get("/heartbeat")
def heartbeat():
    return ""

