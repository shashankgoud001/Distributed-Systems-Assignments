from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import requests
import subprocess
import random
from urllib.parse import urlparse, urlunparse
from consistent_hashing import *

app = FastAPI()
c_hash =ConsistentHashing(3,512,9)
request_count=0
serverList = {}
servindex=1

@app.get("/rep")
def replicas():
    response = {
        "message": {
            "N": len(serverList),
            "replicas": serverList
        },
        "status": "successful"
    }
    return JSONResponse(content=response)


@app.post("/add")
async def add_servers(request: Request):
    req = await request.json()
    n = req["n"]
    hostnames = req["hostnames"]
    if len(hostnames) > n:
        response = {
            "message": "<Error> Length of hostname list is more than newly added instances",
            "status": "failure"
        }
        return JSONResponse(status_code=400, content=response)
    else:
        for hostname in hostnames:
            command = "docker run --name {container_name} --env SERVER_ID={container_name} \
            --network {network_name}  -d serverimg".format(container_name=hostname, network_name="my-net")
            ipcommand = [
                'docker',
                'inspect',
                '--format={{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
                hostname
            ]
            result = subprocess.run(command, shell=True, text=True)
            print(result.returncode)
            if result.returncode == 0:
                serverList[hostname]=servindex
                servindex=servindex+1
                ip = subprocess.run(ipcommand,stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
                ipaddr=ip.stdout.strip()
                c_hash.add_server(serverList[hostname],ipaddr,8080)
                print(ipaddr)
        print(serverList)
    response = {
        "message": {
            "N": len(serverList),
            "replicas": serverList
        },
        "status": "successful"
    }
    return JSONResponse(content=response)


@app.delete("/rm")
async def delete_servers(request: Request):
    req = await request.json()
    n = req["n"]
    hostnames = req["hostnames"]
    if len(hostnames) > n:
        response = {
            "message": "<Error> Length of hostname list is more than newly added instances",
            "status": "failure"
        }
        return JSONResponse(status_code=400, content=response)
    else:
        for hostname in hostnames:
            command = f"docker rm -f {hostname}"
            result = subprocess.run(command, shell=True, text=True)

            if result.returncode == 0:
                indx=serverList[hostname]
                c_hash.remove_server(indx)
                serverList.pop(hostname)
            else:
                return JSONResponse(status_code=400,content="failed to remove server")
    return "deleted the server"


@app.get("/{_path:path}")
def catch_all_path(_path: str, request: Request):
    allowed = ["home", "heartbeat"]
    if _path not in allowed:
        response = {
            "message": "<Error> ’/other’ endpoint does not exist in server replicas",
            "status": "failure"
        }
        return JSONResponse(status_code=400, content=response)
    else:
        url = str(request.url)
        print(url)
        parsed_url = urlparse(url)
        request_count+=1
        server_node = c_hash.get_nearest_server(c_hash.request_hash(request_count))
        modified_url = parsed_url._replace(netloc=f"{server_node.server_ip}:{server_node.server_port}")
        modified_url = urlunparse(modified_url)
        # print(modified_url)
        try:
            response = requests.get(modified_url)

            if response.status_code == 200:
                data = response.json()
                print(data)
                return JSONResponse(content=data)
            else:
                return JSONResponse(status_code=400, content="bad req")

        except requests.RequestException as e:
            print(f"An error occurred during the request: {e}")
            return JSONResponse(content="error occured", status_code=400)

        # print(request.client)
