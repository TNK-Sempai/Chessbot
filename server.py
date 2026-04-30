from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def start_server():
    server = HTTPServer(('localhost', 8765), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=start_server, daemon=True).start()