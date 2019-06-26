from autobahn.twisted.wamp import ApplicationSession
from autobahn import wamp
import networkx as nx

from SliceModels import TransportSwitch

PREFIX = "vsdnorches.topologyservice"


class TopologyService(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super(TopologyService, self).__init__(*args, **kwargs)
        self.transport_topology = nx.Graph()
        self.virtual_topology = {}

    def onJoin(self, details):
        self.log.info("Starting Topology Service...")

    @wamp.register(uri="{p}.add_device")
    def add_device(self, node):
        try:
            device_id = node["device_id"]
            self.transport_topology.add_node(device_id, data=node)
            self.log.info("new transport device {i} has added".format(i=device_id))
            return False, None
        except Exception as ex:
            return True, ex

    @wamp.register(uri="{p}.add_device")
    def rem_node(self, device_id):
        self.transport_topology.remove_node(device_id)
