class ServerNode:
    def __init__(self, i, j, ip, port):
        self.server_id_i = i
        self.server_id_j = j
        self.server_ip = ip
        self.server_port = port

class RequestNode:
    def __init__(self):
        self.req = {}

class Node:
    def __init__(self):
        self.server = None
        self.requests = []
        # `next` helps in storing the next virtual server and this is dependent on number of slots but 
        # not on number of requests which is an optimization
        self.next = None

# Consistent hashing parameters
num_servers = 3
num_slots = 512
vir_servers = 9

# Array that holds virtual servers and requests
circular_array = [Node]*num_slots

# Request mapping hash function
def request_hash(i) -> int:
    return (i**2 + 2*i + 17)%num_slots

# Server mapping hash function
def server_hash(i, j) -> int:
    return (i**2 + j**2 + 2*i*j + 25)%num_slots

# Linear Probing for servers in case of collision
def linear_probe(pos) -> int:
    '''
        Linearly probes the next available
        slot in the map for the virtual server
    '''
    while circular_array[pos].server is not None:
        pos = (pos + 1)%num_slots
    
    return pos

# Finds the nearest server
def find_nearest_server(pos) -> int:
    '''
        Finds the position of nearest virtual server
        in the clockwise direction
    '''
    j = pos
    while True:
        if circular_array[j].server is not None:
            return j

        j = (j + 1)%num_slots

# Map server to request
def map_server_to_request(pos):
    '''
        Maps the requests to this virtual server and
        traverses in anti-clockwise direction
    '''
    j = (pos - 1 + num_slots)%num_slots
    while circular_array[j].server is not None:
        circular_array[j].next = pos
        j = (j - 1 + num_slots)%num_slots

# Add Request
def add_request(i, request : RequestNode):
    '''
        Adds request to the map
    '''
    pos = request_hash(i)
    circular_array[pos].requests.append(request)
    circular_array[pos].next = find_nearest_server(pos)

# Add Server
def add_server(i, ip, port):
    '''
        Adds virtual servers to the map, and in 
        case of collision, linearly probes it also
        maps the requests to this new virtual server
        accordingly
    '''
    for j in range(num_servers):
        pos = server_hash(i,j)
        if circular_array[pos].server is not None:
            pos = linear_probe(pos)

        circular_array[pos].server = ServerNode(i, j, ip, port)
        map_server_to_request(pos)

# Remove Request
def remove_request(i, request : RequestNode):
    '''
        Removes request from the map
    '''
    pos = request_hash(i)
    if request not in circular_array[pos].requests:
        # needs to return error
        pass
    else:
        circular_array[pos].requests.remove(request)

# Remove Server
def remove_server(i):
    '''
        Removes all the virtual server instances from
        the map and re-maps the requests that are pointed to
        this to the next closest virtual server in the 
        clockwise direction
    '''
    for j in range(num_servers):
        pos = server_hash(i, j)
        while circular_array[pos].server is None or circular_array[pos].server.server_id_i != i:
            pos = (pos + 1)%num_slots
        
        circular_array[pos].server = None
        next_pos = find_nearest_server(pos)
        circular_array[pos].next = next_pos

        # re-map requests
        k = (pos - 1 + num_slots)%num_slots
        while circular_array[k].server is not None:
            circular_array[k].next = next_pos
            k = (k - 1 + num_slots)%num_slots