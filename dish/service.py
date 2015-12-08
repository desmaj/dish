import eventlet
eventlet.monkeypatch

from nameko.rpc import rpc
from nameko.runners import ServiceRunner

class DSMService(object):
    name = 'dsm'

    @rpc
    def read(self, key):
        pass

    @rpc
    def write(self, key, value):
        pass


def main():
    runner = ServiceRunner(config={})
    runner.add_service(DSMService)
    runner.start()

if __name__ == '__main__':
    main()

