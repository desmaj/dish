import eventlet
eventlet.monkey_patch()

import datetime
import itertools
import sys

from dish.actor import DSMActor
from dish.node import serve_node
from dish.messengers.udp import UDPMessenger

NODE_COUNT = int(sys.argv[1])
BASE_PORT = 30000

ports = [BASE_PORT + i for i in range(1, NODE_COUNT+1)]
nodes = [("127.0.0.1", port) for port in ports]

def main():
    greenthreads = [eventlet.spawn(serve_node, "127.0.0.1", port) for port in ports]

    actor = DSMActor(("", BASE_PORT), nodes, UDPMessenger)
    
    def _step_5(key, value):
        print datetime.datetime.now()
        print "read 2 result:{}".format(value)
        actor.write("voter.2", "Steve Ullman", lambda key, result: None)

    def _step_4(key, value):
        print datetime.datetime.now()
        print "Step 4"
        actor.read("voter.1", _step_5)
        
    def _step_3(key, value):
        print datetime.datetime.now()
        print "Step 3"
        print "read 1 result: {}".format(value)
        actor.write("voter.1", "Laura Bondi", _step_4)
    
    def _step_2(key, value):
        print datetime.datetime.now()
        print "Step 2"
        actor.read("voter.1", _step_3)

    print "Step 1"
    print datetime.datetime.now()
    actor.write("voter.1", "Matthew Desmarais", _step_2)

        
    
    [greenthread.wait() for greenthread in greenthreads]

if __name__ == '__main__':
    main()
