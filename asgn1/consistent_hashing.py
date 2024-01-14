# Map that holds virtual servers and requests
map = {}

# Consistent hashing parameters
num_servers = 3
num_slots = 512
vir_servers = 9

# Request mapping hash function
def request_hash(i) -> int:
    return (i**2 + 2*i + 17)

# Server mapping hash function
def server_hash(i, j) -> int:
    return (i**2 + j**2 + 2*i*j + 25)

# Linear Probing for servers in case of collision
def linear_probe(i, j):
    '''
        Linearly probes the next available
        slot in the map for the server
    '''
    pass

# Map request to server
def map_request(i):
    '''
        Maps request to the nearest virtual server
        in the clockwise direction
    '''
    pass

# Add Request
def add_request(i):
    '''
        Adds request to the map
    '''
    pass

# Add Server
def add_virtual_server(i, j):
    '''
        Adds virtual server to the map,and in 
        case of collision, linearly probes it also
        maps the requests to this new virtual server
        accordingly
    '''
    pass

# Remove Request
def remove_request(i):
    '''
        Removes request from the map
    '''
    pass

# Remove Server
def remove_server(i):
    '''
        Removes all the virtual server instances from
        the map and re-maps the requests that are pointed to
        this to the next closest virtual server in the 
        clockwise direction
    '''
    pass