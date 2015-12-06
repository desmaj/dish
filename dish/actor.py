""" actor.py

    The actor is the intelligent portion of our DSM implementation. The nodes
    are just network-enabled dictionaries, it is the actor that knows how to
    perform the replication 
"""
import itertools
import math
import uuid

# An Item is a value, tag, creator id tuple
def Item(value, tag, creator):
    return (value, tag, creator)


# A Message is an id, command, item tuple
def Message(id, command, key, item):
    return (id, command, key, item)


class DSMCommand(object):
    """ A record of an outstanding DSM command
        
        
    """
    def __init__(self, quora, key, completion_callback):
        self.key = key
        self._quora = quora
        self._responses = {}
        self._completion_callback = completion_callback

    def add_response(self, address, item):
        self._responses[address] = item
        quorum = self.is_complete()
        if quorum:
            values = [self._responses[node] for node in quorum]
            self._process_values(values)

    def is_complete(self):
        for quorum in self._quora:
            if all(node in self._responses for node in quorum):
                return quorum
    
    def _process_values(self, values):
        if self._completion_callback:
            if all(item == 'OK' for item in values):
                self._completion_callback(self.key, "OK")
            else:
                current_item = None
                for item in values:
                    if current_item:
                        if item[1:] > current_item[1:]:
                            current_item = item
                    else:
                        current_item = item
                self._completion_callback(self.key, tuple(current_item))


class DSMActor(object):

    @staticmethod
    def make_quora(nodes):
        nodes_per_quora = len(nodes) / 2 + 1
        quora_count = len(nodes)
        quora = [[] for _ in range(quora_count)]
        for q, quorum in enumerate(quora):
            for i in range(q, q + nodes_per_quora):
                quorum.append(nodes[i % len(nodes)])
        return quora
    
    def __init__(self, address, nodes, messenger_factory):
        self._id = uuid.getnode()
        self._messenger = messenger_factory(address, self._received_message)
        
        self._nodes = nodes
        for node in nodes:
            self._messenger.add_node(node)
        
        self._quora = self.make_quora(nodes)
        
        self._outstanding_commands = {}

        self._messenger.start()
    
    def _received_message(self, address, message):
        message_id, item = message
        if message_id in self._outstanding_commands:
            self._outstanding_commands[message_id].add_response(address, item)
            if self._outstanding_commands[message_id].is_complete():
                del self._outstanding_commands[message_id]
                

    @property
    def quora(self):
        return self._quora
    
    def stop(self):
        self._messenger.stop()
    
    def read(self, key, callback):
        self._read(key, callback)

    def _read(self, key, callback):
        message_id = str(uuid.uuid4())
        message = Message(message_id, 'get', key, None)
        self._outstanding_commands[message_id] = DSMCommand(self._quora,
                                                            key,
                                                            self._propagate(callback))
        self._messenger.send(message)

    def _propagate(self, callback):
        def _complete(key, item):
            def _do_callback(key, result):
                callback(item)
            self._write(key, item, _do_callback)
        return _complete
    
    def write(self, key, value, callback):
        def _increment_tag_and_write(item):
            old_value, tag, creator = item
            new_item = Item(value, tag+1, self._id)
            self._write(key, new_item, callback)
        self._read(key, _increment_tag_and_write)

    def _write(self, key, item, callback):
        message_id = str(uuid.uuid4())
        message = Message(message_id, 'set', key, item)
        self._outstanding_commands[message_id] = DSMCommand(self._quora,
                                                            key,
                                                            callback)
        self._messenger.send(message)
