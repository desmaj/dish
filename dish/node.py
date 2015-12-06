import json
import socket
import sys


def Response(message_id, item):
    return (message_id, item)


class DSMNode(object):

    def __init__(self):
        self._data = {}

    def get(self, key, _):
        return self._data.get(key, (None, 0, 0))
    
    def set(self, key, item):
        current = self._data.get(key, (None, 0, 0))
        if item[1:] > current[1:]:
            self._data[key] = item
        return 'OK'
    
    def __repr__(self):
        return "{}::{}".format(id(self), json.dumps(self._data))

    
def serve_node(host, port):
    node = DSMNode()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    while True:
        print repr(node)
        data, address = sock.recvfrom(4096)
        message = json.loads(data)
        operation = getattr(node, message[1])
        if operation:
            key, item = message[2], tuple(message[3] or [])
            result = operation(key, item)
            response = Response(message[0], result)
            sock.sendto(json.dumps(response), address)
        elif message['command'] == 'exit':
            break


if __name__ == '__main__':
    host = sys.argv[1]
    port = sys.argv[2]
    serve_node(host, port)
