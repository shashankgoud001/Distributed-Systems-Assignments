import http.server
import socketserver
import sys

PORT = int(sys.argv[1])
ID = str(sys.argv[2])

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/home':
            self.send_response(200)
            # response json
            self.send_header('Content-type', 'application/json')
            response = {
                "messsage": "Hello from Server: " + ID,
                "status": "successful"
            }
            self.end_headers()
            self.wfile.write(bytes(str(response), 'utf-8'))
        elif self.path == '/heartbeat':
            self.send_response(200)
            self.end_headers()
        else:
            super().do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print("Server listening on port", PORT)
        httpd.serve_forever()
