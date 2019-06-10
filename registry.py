from autobahn.twisted.wamp import ApplicationSession
from autobahn import wamp

PREFIX = "vsdnorches.registry"

class NodeRegistry(ApplicationSession):

    @wamp.register("{p}.new_tswitch".format(p=PREFIX))
    def __new_tswitch(self, msg):
        p = msg.get["prefix"]
        n = msg.get["node"]

        self.node_registred.update({p:n})

    def get_nodes(self):
        return self.node_registred.copy()

    def TransportSwitch(self, prefix,switch):




    def onJoin(self, details):
        self.node_registred = {}

        pass
