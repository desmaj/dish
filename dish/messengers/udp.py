import json
import socket

import eventlet
from eventlet import queue

from .base import ExitMessage
from .base import NodeListLockedException

class UDPMessenger(object):

    def __init__(self, address, message_callback):
        self._nodes = []
        self._send_queue = queue.Queue()
        self._message_callback = message_callback
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(address)
        self._continue = True
    
    def add_node(self, address):
        self._nodes.append(address)

    def start(self):
        eventlet.spawn_n(self._send_worker)
        eventlet.spawn_n(self._receive_worker)

    def stop(self):
        self._continue = False

    def send(self, message):
        self._send_queue.put(message)
    
    def _send_worker(self):
        while self._continue:
            message = self._send_queue.get()
            json_message = json.dumps(message)
            for node in self._nodes:
                self._socket.sendto(json_message, node)

    def _receive_worker(self):
        while self._continue:
            json_message, node = self._socket.recvfrom(4096)
            message = json.loads(json_message)
            self._message_callback(node, message)
            
