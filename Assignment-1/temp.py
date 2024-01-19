class ServerNode:
    def __init__(self, i, j, ip, port):
        self.server_id_i = i
        self.server_id_j = j
        self.server_ip = ip
        self.server_port = port
    
    def __str__(self) -> str:
        return f"{self.server_id_i} : {self.server_port}"


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
    
    def __str__(self) -> str:
        return str(self.server)

class myclass:
    # Array that holds virtual servers and requests
    def __init__(self,num_servers,num_slots,vir_servers) -> None:
        self.circular_array = []
        for _ in range(num_slots):
            self.circular_array.append(Node())
        self.num_servers = num_servers
        self.num_slots = num_slots
        self.vir_servers = vir_servers

    # Server mapping hash function
    def server_hash(self,i, j) -> int:
        return (i**2 + j**2 + 2 * i * j + 25) % self.num_slots

    # Linear Probing for servers in case of collision
    def linear_probe(self,pos) -> int:
        """
        Linearly probes the next available
        slot in the map for the virtual server
        """
        count = 0
        while self.circular_array[pos].server is not None:
            pos = (pos + 1) % self.num_slots
            count = count + 1
            if count == self.num_slots:
                return -1

        return pos
    
    # Map server to request
    def map_server_to_request(self,pos):
        """
        Maps the requests to this virtual server and
        traverses in anti-clockwise direction
        """
        print(self.circular_array[pos].server)
        j = (pos - 1 + self.num_slots) % self.num_slots
        cntr = 0
        print("initial", j)
        while self.circular_array[j].server is None:
            self.circular_array[j].next = pos
            j = (j - 1 + self.num_slots) % self.num_slots
            cntr += 1
            # print(j, 'something')
            # print(cntr)
            # if cntr == self.num_slots:
            #     return

    # Add Server
    def add_server(self, i, ip, port):
        """
        Adds virtual servers to the map, and in
        case of collision, linearly probes it also
        maps the requests to this new virtual server
        accordingly
        """
        for j in range(self.vir_servers):
            pos = self.linear_probe(self.server_hash(i, j))
            if pos == -1:
                return "Slots are full cannot add new server"
            self.circular_array[pos].server = ServerNode(i, j, ip, port)
            print(self.circular_array[pos].server)
            self.map_server_to_request(pos)

cls = myclass(3, 10, 2)
cls.add_server(1, 533, 5345)

for i in range(10):
    if cls.circular_array[i].server is None:
        print('finally found')
    else:
        print(i, 'woah', cls.circular_array[i].server)
