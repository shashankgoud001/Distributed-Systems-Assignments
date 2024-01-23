# Distributed Systems Assignment 1
## Server
- Server has 2 endpoints viz., `Endpoint (/home, method=GET)` and `Endpoint (/heartbeat, method=GET)`.
- It runs on the port 8080.

## Loadbalancer
- Loadbalancer works with both the client and server which redirects the requests from client to server.
- It runs on the port 5000.
- It also maintains the number of servers consistent and if any server goes down, it will spawn a new server and add it to the list of servers.
- It forwards the requests using the **consistent hashing** algorithm.
- This has the following endpoints:
    - `Endpoint (/rep, method=GET)`
    - `Endpoint (/add, method=POST)`
    - `Endpoint (/rm, method=DELETE)`
    - `Endpoint (/<path>, method=GET)`

## Client
- Client sends the requests to the loadbalancer.

## Analysis
