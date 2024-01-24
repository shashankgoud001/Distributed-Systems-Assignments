# Distributed Systems Assignment 1
## Server
- Server has 2 endpoints viz., `Endpoint (/home, method=GET)` and `Endpoint (/heartbeat, method=GET)`.
- Each Server runs in a container with a unique IP address and port number as 8080. (This information is hidden from the client)

## Loadbalancer
- Loadbalancer works with both the client and server which redirects the requests from client to server.
- It runs on the port 5000.
- It sends and recieves heartbeats to keep track of which servers are up and which servers have crashed
- It also maintains the number of servers consistent and if any server goes down, it will spawn a new server and add it to the list of servers.
- It forwards the requests using the **consistent hashing** algorithm.
    - There is a circular array with 512 slots which stores the information of servers
    - Hash functions are utilized to map server to a slot in the cirular array and map request to a server
    - Virtual servers are used to make the requests get distributed evenly among all the servers 
- This has the following endpoints:
    - `Endpoint (/rep, method=GET)`
    - `Endpoint (/add, method=POST)`
    - `Endpoint (/rm, method=DELETE)`
    - `Endpoint (/<path>, method=GET)`

## Client
- Client sends the requests to the loadbalancer.
- Client recieves response from the server via loadbalancer.


## Run Locally
Ensure docker, docker-compose and jupyter-notebook are installed.

Clone the project

```bash
  git clone https://github.com/shashankgoud001/Distributed-Systems-Assignments.git
```

Go to the project directory

```bash
  cd Distributed-Systems-Assignments/Assignment1
```

Install dependencies (For Analysis part)  


```bash
  pip3 install requests, aiohttp, matplotlib
```

Build docker images for Loadbalancer and Server

```bash
  sudo make build
```
Start the Loadbalancer

```bash
  sudo make 
```
Now run the code from **analysis.ipynb**z (covers task A1, A2, A3) and **analysis-task-A4.ipynb** (covers task A4)

Remove all containers

```bash
  sudo make clean
```

## Analysis

1. Launching 10,000 async requests on 3 servers produced the bar graph given below.From the bar graph, we can see that Server 1 is handling 4300 requests, Server 2 is handling 2900 requests and Server 3 is handling 2800 requests. Server 1 is getting a little bit more requests but still the performance is good and the response is fast. Changing the hash function or adding more servers might help to further optimize load balancing and enhance performance.
![Bar Graph for A1](./assets/A1_bargraph.png)

2. Launching 10,000 async requests on variying servers count(from 2 to 6) yielded the line graph given below. From the line graph, we can see that as we increase the number of servers from 2 to 6 we can observe that the requests are getting distributed evenly. Initially when number of servers are 2 the difference in number of requests handled by server with maximum requests and server with minimum requests is nearly 1800. But as we increase the number of servers to 3,4,5,6, we can see that the difference in number of requests handled by server with maximum requests and server with minimum requests changes to 760, 1600, 1850, 1790 respectively. As we can see that the distribution of the load was best when number of servers were 3. Hence the performance is best when there are 3 servers. Although the difference between the server with maximum and mininum requests is variying the overall requests are being distributed more evenly as we increase the number of servers. Hence we can scale this and have more servers and handle higher client requests efficiently.
![Line Graph for A2](./assets/A2_linegraph.png)
![Max-min Difference of requests](./assets/A2_difference_linegraph.png)

3. All endpoints of the load balancer were tested successfully, and the load balancer distributed incoming requests among the available server instances. It can be verified by running the `analysis.ipynb` notebook. When a server running is stopped the loadbalancer was able to detect it. It was detected by using heartbeat. When loadbalancer sent a heartbeat and didn't recieve one back from this server within certain period, it concluded that this server is down. It respawned a new server quickly and the new server was able to handle the incoming requests just like other servers. The load distribution was even.


4. The new hash functions used for both H and Φ is sha256. From the bar graph below, we can see that the 10,000 async requests are being distributed evenly among all the 3 servers present. Server 1 is handling 3300 requests, Server 2 is handling 2000 requests and Server 3 is handling 4700 requests. Server 2 is getting a little bit less requests and Server 3 is getting high load. Overall the performance is still good. 
![Bar Graph for A4](./assets/A4_bargraph.png)

From the line graph below, we can see that as we increase the number of servers from 2 to 6 we can observe that the requests are getting distributed more evenly. Initially when number of servers are 2 the difference in number of requests handled by server with maximum requests and server with minimum requests is nearly 4000. But as we increase the number of servers to 3,4,5,6, we can see that the difference in number of requests handled by server with maximum requests and server with minimum requests changes to 1800, 1100, 1500, 1400 respectively. The distribution of load is best when there were 4 servers. Hence the performance is best when there are 4 servers. Although the difference between the server with maximum and mininum requests is variying the overall requests are being distributed more evenly as we increase the number of servers. Hence we can scale this and have more servers and handle higher client requests efficiently. Also we notice that hash function plays key role in how the load gets distributed among the servers. The better the hash function the more balanced is the distribution of load among the servers. 

![Line Graph for A4](./assets/A4_linegraph.png)
