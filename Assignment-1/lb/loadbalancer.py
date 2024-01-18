from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import requests
import subprocess
import random
from urllib.parse import urlparse, urlunparse
from consistent_hashing import *
import uuid

app = FastAPI()
app.c_hash = ConsistentHashing(3, 512, 9)
app.request_count = 0
app.serverList = {}
app.servindex = 1


@app.get("/rep")
def replicas():
    response = {
        "message": {
            "N": len(app.serverList),
            "replicas": list(app.serverList.keys())
        },
        "status": "successful"
    }
    return JSONResponse(content=response)


@app.post("/add")
async def add_servers(request: Request):
    req = await request.json()
    n = req["n"]
    hostnames = req["hostnames"]

    # checking if requested container names were taken already
    namestaken = []
    for hostname in hostnames:
        if hostname in app.serverList:
            namestaken.append(hostname)

    # checking if duplicates exist
    has_duplicates = len(hostnames) != len(set(hostnames))

    while len(hostnames) < n:
        cname = uuid.uuid4().hex
        if cname in app.serverList:
            pass
        else:
            hostnames.append(cname)

    print(hostnames)
    if len(hostnames) > n:
        return JSONResponse(
            status_code=400,
            content={
                "message": "<Error> Length of hostname list is more than newly added instances",
                "status": "failure"
            }
        )
    elif namestaken != []:
        return JSONResponse(
            status_code=400,
            content={
                "message": f"Container names {', '.join(namestaken)} already in use.",
                "status": "failure"
            }
        )
    elif has_duplicates:
        return JSONResponse(
            status_code=400,
            content={
                "message": "duplicate names not allowed",
                "status": "failure"
            }
        )

    else:
        print("create containers")
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
                app.serverList[hostname] = app.servindex
                app.servindex = app.servindex+1
                ip = subprocess.run(
                    ipcommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
                ipaddr = ip.stdout.strip()
                # app.c_hash.add_server(app.serverList[hostname],ipaddr,8080)
                print(ipaddr)
        print(app.serverList)

        servers = list(app.serverList.keys())
        return JSONResponse(
            status_code=200,
            content={
                "message": {
                    "N": len(servers),
                    "replicas": servers
                },
                "status": "successful"
            }
        )


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
                indx = app.serverList[hostname]
                # app.c_hash.remove_server(indx)
                app.serverList.pop(hostname)
            else:
                return JSONResponse(status_code=400, content="failed to remove server")
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
        app.request_count += 1
        server_node = app.c_hash.get_nearest_server(
            app.c_hash.request_hash(app.request_count))
        modified_url = parsed_url._replace(
            netloc=f"{server_node.server_ip}:{server_node.server_port}")
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
