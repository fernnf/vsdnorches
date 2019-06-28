from autobahn.twisted.wamp import ApplicationSession
from autobahn import wamp
import networkx as nx

from SliceModels import TransportSwitch, TransportLink

PREFIX = "vsdnorches.topologyservice"

# TODO: Create injection from dictionary to model class

class TopologyTransportController(object):
    def __init__(self):
        self._transport_topology = nx.Graph(tenant_id="0")

    def add_node(self, node: TransportSwitch):
        self._transport_topology.add_node(node.get_id(), node=node, virtual_nodes=[])

    def rem_node(self, device_id):
        self._transport_topology.remove_node(device_id)

    def add_link(self, link: TransportLink):

        ingress = link.get_ingress_interface().get_device_id()
        egress = link.get_egress_interface().get_device_id()

        self._transport_topology.add_edge(ingress, egress, link=link,)

    def set_virtual_node(self, transport_device_id, virtual_device_id):
        self._transport_topology.nodes[transport_device_id]["virtual_nodes"].append(virtual_device_id)

    def del_virtual_node(self,transport_device_id, virtual_device_id):
        self._transport_topology.nodes[transport_device_id]["virtual_nodes"].pop(virtual_device_id)

    def get_count_virtual_node(self, transport_device_id):
        return len(self._transport_topology.nodes[transport_device_id]["virtual_nodes"])



class TopologyService(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super(TopologyService, self).__init__(*args, **kwargs)
        self._transport_topology = nx.Graph()
        self._virtual_topology = {}

    def onJoin(self, details):
        self.log.info("Starting Topology Service...")

    @wamp.register(uri="{p}.add_device")
    def add_node(self, node):

        n = TransportSwitch.parser(node)
        try:
            self._transport_topology.add_node(n.device_id, data=node)
            self.log.info("new transport device {i} has added".format(i=n.device_id))
            return False, None
        except Exception as ex:
            return True, ex

    @wamp.register(uri="{p}.rem_device")
    def rem_node(self, device_id):

        try:
            self._transport_topology.remove_node(device_id)
            self.log.info("the transport device {i} was remove".format(i=device_id))
            return False, None
        except Exception as ex:
            return True, ex


    @wamp.register(uri = "{i}.add_link")
    def add_link(self, link):
        l = TransportLink.parser(link)
        try:
            self.