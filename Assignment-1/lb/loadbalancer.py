from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse,RedirectResponse
from random import randint
import requests
from requests.adapters import HTTPAdapter, Retry
import subprocess
import random
from urllib.parse import urlparse, urlunparse
from consistent_hashing import *
import uuid
from time import sleep

app = FastAPI()
app.c_hash = ConsistentHashing(3, 512, 9)
app.max_request_count = 1e6 # 1 million
app.serverList = {}
app.max_servindex = 1024



def respawn_dead_servers():
    change_list = []
    for serv_name, details  in list(app.serverList.items()):
        request_url = f"http://{details['ip']}:8080/heartbeat"

        try:
            req_session = requests.Session()
            retries = Retry(total=3,
                            backoff_factor=0.1,
                            status_forcelist=[ 500, 502, 503, 504 ])

            req_session.mount('http://', HTTPAdapter(max_retries=retries))
            
            response = req_session.get(request_url, timeout=0.5)

            data = response.json()
            print(f'<+> Server {serv_name} is alive; Response: {data}')
               
        except requests.RequestException as e:
            print(f'<!> Server {serv_name} is dead; Error: {e}')
            new_server_name = serv_name + "_new"
            print(f'<!> Respawning a new server with name: {new_server_name}...')
            command = f"docker run --name {new_server_name} --env SERVER_ID={new_server_name} \
            --network my-net  -d serverimg " # HC

            result = subprocess.run(command, shell=True, text=True)
            
            if result.returncode != 0:
                print(f'<!> Failed to respawn a new server!')
                continue
            
            change_list.append((serv_name, new_server_name))
            print(f'<+> Successfully respawned a new server with name: {new_server_name}')
            
    
    for old_name, new_name in change_list:
        app.serverList[new_name] = app.serverList.pop(old_name)
        ipcommand = [
                'docker',
                'inspect',
                '--format={{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
                 new_name
            ]

        ip = subprocess.run(
            ipcommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        ipaddr = ip.stdout.strip()
        
        app.c_hash.remove_server(app.serverList[new_name]['index'])
        app.serverList[new_name]['ip'] = ipaddr
        app.c_hash.add_server(app.serverList[new_name]['index'], app.serverList[new_name]['ip'], 8080)
    
    if len(change_list) > 0:
        print(f'<+> Waiting for new servers to start properly ....')
        sleep(0.5)

  
@app.get("/rep") 
def replicas():
    respawn_dead_servers()
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
    respawn_dead_servers()
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
        cname = str(uuid.uuid4().hex)[:6]
        if not (cname in app.serverList or cname in hostnames):
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
                # app.servindex = app.servindex+1
                ip = subprocess.run(
                    ipcommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
                ipaddr = ip.stdout.strip()
                app.serverList[hostname] = {"index": randint(1, app.max_servindex), "ip": ipaddr}
                app.c_hash.add_server(app.serverList[hostname]['index'], ipaddr, 8080)
                print(ipaddr)
            else:
                return JSONResponse(
                    status_code=500,
                    content={
                        "message": {
                            "N": len(list(app.serverList.keys())),
                            "replicas": list(app.serverList.keys()),
                            "error": f"failed to create server: {hostname}"
                        },
                        "status": "failure"
                    }
                )
        print(app.serverList)

        servers = list(app.serverList.keys())
        sleep(1)
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
    respawn_dead_servers()
    req = await request.json()
    n = req["n"]
    hostnames = req["hostnames"]

    # picking at random if mentioned list is smaller than n
    if len(hostnames) < n:
        available_servers = list(app.serverList.keys())
        pickserv = [item for item in available_servers if item not in hostnames]
        if len(pickserv) + len(hostnames) < n:
            return JSONResponse(
                status_code=400,
                content={
                    "message": "failed as requested deletions exceeds the available number of servers",
                    "status": "failure"
                }
            )
        else:
            hostnames += random.sample(pickserv, n-len(hostnames))

    if len(hostnames) > n:
        response = {
            "message": "<Error> Length of hostname list is more than newly added instances",
            "status": "failure"
        }
        return JSONResponse(status_code=400, content=response)

    else:

        # making a preliminary check whether the requested server delete is possible or not
        invalidhosts = []
        for hostname in hostnames:
            if hostname not in app.serverList:
                invalidhosts.append(hostname)

        if invalidhosts != []:
            return JSONResponse(
                status_code=400,
                content={
                    "message": f"The following servers were not found: {', '.join(invalidhosts)}",
                    "status": "failure"
                }
            )

        servers_removed = []
        for hostname in hostnames:
            command = f"docker rm -f {hostname}"
            result = subprocess.run(command, shell=True, text=True)

            if result.returncode == 0:
                indx = app.serverList[hostname]['index']
                app.c_hash.remove_server(indx)
                app.serverList.pop(hostname)
                servers_removed.append(hostname)
            else:
                return JSONResponse(
                    status_code=400,
                    content={
                        "message": {
                            "N": len(list(app.serverList.keys())),
                            "replicas": list(app.serverList.keys()),
                            "error": f"failed to remove server: {hostname}"
                        },
                        "status": "failure"
                    }
                )

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


@app.get("/{_path:path}")
def catch_all_path(_path: str, request: Request):
    if len(app.serverList) == 0:
        return JSONResponse(
            status_code=500,
            content={
                "message": "No servers available",
                "status": "failure"
            }
        )
    
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
        # app.request_count += 1
        server_node = app.c_hash.get_nearest_server(
            app.c_hash.request_hash(randint(1, app.max_request_count)))
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
            respawn_dead_servers()
            return RedirectResponse(url=url)
            # return JSONResponse(content="error occured", status_code=400)

        # print(request.client)

if __name__ == "__main__":
    import uvicorn
    print("this code is running")
    uvicorn.run("loadbalancer:app", host="0.0.0.0", port=5000, reload=True)
