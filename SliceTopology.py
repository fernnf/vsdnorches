from autobahn.twisted.wamp import ApplicationSession
from autobahn import wamp
import networkx as nx
import networkx.readwrite as nxparser

from SliceModels import TransportSwitch, TransportLink, TransportInterface
from SliceModels import VirtualInterface, VirtualSwitch, VirtualLink

PREFIX = "vsdnorches.topologyservice"


# TODO: Create injection from dictionary to model class

class TransportTopologyController(object):
    def __init__(self, label=None):
        self._transport_topology = nx.Graph(type="transport_network", label=label, tenant_id="0")

    @classmethod
    def from_json(cls, j):
        obj = cls()
        obj._transport_topology = nxparser.node_link_graph(j)
        return obj

    def add_node(self, node):
        n = TransportSwitch.parser(node)
        self._transport_topology.add_node(n.get_id(), properties=n.serialize(), interfaces={}, virtual_nodes=[])

    def rem_node(self, device_id):
        assert self._transport_topology.has_node(device_id), "the source node was not found"
        self._transport_topology.remove_node(device_id)

    def add_link(self, link):
        l = TransportLink.parser(link)
        src_device_id = l.get_ingress()["device_id"]
        dst_device_id = l.get_egress()["device_id"]

        assert self._transport_topology.has_node(src_device_id), "the source node was not found"
        assert self._transport_topology.has_node(dst_device_id), "the destination node was not found"

        self._transport_topology.add_edge(src_device_id, dst_device_id, properties=link, statistics=[])

    def rem_link(self, src_device_id, dst_device_id):
        assert self._transport_topology.has_edge(src_device_id, dst_device_id), "the link was not found"
        self._transport_topology.remove_edge(src_device_id, dst_device_id)

    def set_interface(self, interface):
        i = TransportInterface.parser(interface)
        assert self._transport_topology.has_node(i.get_device_id()), "the node was not found"
        ret = self._transport_topology[i.get_device_id()]["interfaces"].get(i.get_portnum(), None)
        if ret is None:
            self._transport_topology[i.get_device_id()]["interfaces"].update({i.get_portnum(): i})
        else:
            raise ValueError("the interface already was included")

    def del_interface(self, device_id, portnum):
        assert self._transport_topology.has_node(device_id()), "the node was not found"

        ret = self._transport_topology[device_id()]["interfaces"].get(portnum, None)

        if ret is not None:
            self._transport_topology[device_id()]["interfaces"].pop(portnum)
        else:
            raise ValueError("the interface not found on device {d}".format(d=device_id))

    def set_virtual_node(self, device_id, virt_device_id):
        self._transport_topology.nodes[device_id]["virtual_nodes"].append(virt_device_id)

    def del_virtual_node(self, device_id, virt_device_id):
        self._transport_topology.nodes[device_id]["virtual_nodes"].pop(virt_device_id)

    def get_count_virtual_node(self, transport_device_id):
        return len(self._transport_topology.nodes[transport_device_id]["virtual_nodes"])

    def get_count_nodes(self):
        return self._transport_topology.number_of_nodes()

    def get_count_links(self):
        return self._transport_topology.number_of_edges()

    def get_link(self, link_id):
        links = list(self._transport_topology.edges(data=True))
        for link in links:
            lid = link[2]["properties"]["link_id"]
            if lid.__eq__(link_id):
                return False, (link[0], link[1])

        return True, "the link was not found"

    def to_json(self):
        j = nxparser.node_link_data(self._transport_topology)
        return j


class SliceTopologyController(object):

    def __init__(self, slice=None):
        self._slice_topology = nx.Graph(properties=slice)

    @classmethod
    def from_json(cls, j):
        obj = cls()
        obj._slice_topology = nxparser.node_link_graph(j)
        return obj

    def set_proper_slice(self, slice):
        self._slice_topology.graph.update({"properties": slice})

    def get_slice_id(self):
        return self._slice_topology.graph["properties"].get("slice_id", None)

    def add_virt_node(self, node):
        vn = VirtualSwitch.parser(node)
        assert self._slice_topology.has_node(vn.get_id()), "the node already was included"
        self._slice_topology.add_node(vn.get_id(), properties=node, interfaces={}, statistics={})

    def rem_virt_node(self, device_id):
        assert self._slice_topology.has_node(device_id), "the node was not found"
        self._slice_topology.remove_node(device_id)

    def add_link(self, link):
        vl = VirtualLink.parser(link)
        src_device_id = vl.get_ingress()["device_id"]
        dst_device_id = vl.get_egress()["device_id"]

        assert self._slice_topology.has_node(src_device_id), "the node was not found"
        assert self._slice_topology.has_node(dst_device_id), "the node was not found"

        self._slice_topology.add_edge(src_device_id, dst_device_id, properties=link, statistics={})

    def rem_link(self, src_device_id, dst_device_id):
        assert self._slice_topology.has_edge(src_device_id, dst_device_id), "the link was not found"
        self._slice_topology.remove_edge(src_device_id, dst_device_id)

    def set_interface(self, device_id, interface):
        i = VirtualInterface.parser(interface)
        ret = self._slice_topology[device_id]["interfaces"].get(i.get_virt_portnum(), None)
        if ret is None:
            self._slice_topology[device_id]["interfaces"].update({i.get_virt_portnum(): interface})
        else:
            raise ValueError("the virtual interface already was included to node")

    def del_interface(self, device_id, portnum):
        ret = self._slice_topology[device_id]["interfaces"].get(portnum, None)
        if ret is not None:
            self._slice_topology[device_id]["interfaces"].pop(portnum)
        else:
            raise ValueError("the interface was not found")

    def get_count_nodes(self):
        return self._slice_topology.number_of_nodes()

    def get_count_links(self):
        return self._slice_topology.number_of_edges()

    def get_nodes(self):
        return self._slice_topology.nodes

    def to_json(self):
        j = nxparser.node_link_data(self._slice_topology)
        return j


class TopologyService(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super(TopologyService, self).__init__(*args, **kwargs)
        self._transport_topology = TransportTopologyController(label="Transport")
        self._virtual_topology = {}

    def onJoin(self, details):
        self.log.info("Starting Topology Service...")

    @wamp.register(uri="{p}.add_phy_node")
    def add_phy_node(self, node):
        try:
            self._transport_topology.add_node(node)
            self.log.info("new transport device {i} has added".format(i=node["device_id"]))
            return False, None
        except Exception as ex:
            return True, ex

    @wamp.register(uri="{p}.rem_phy_node")
    def rem_phy_node(self, device_id):

        try:
            self._transport_topology.rem_node(device_id)
            self.log.info("the transport device {i} was remove".format(i=device_id))
            return False, None
        except Exception as ex:
            return True, ex

    @wamp.register(uri="{i}.add_phy_link")
    def add_phy_link(self, link):
        try:
            self._transport_topology.add_link(link)
            self.log.info("new physical link {i} was added".format(i=link["link_id"]))
            return False, None
        except Exception as ex:
            return True, ex

    @wamp.register(uri="{i}.rem_phy_link")
    def rem_phy_link(self, link_id):
        try:
            error, d = self._transport_topology.get_link(link_id)
            if not error:
                self._transport_topology.rem_link(d[0], d[1])
                self.log.info("the link {i} was remove".format(i=link_id))
                return False, None
            else:
                self.log.error(d)
        except Exception as ex:
            return True, ex

    @wamp.register(uri="{i}.create_slice")
    def create_slice(self, slice):
        s = SliceTopologyController(slice=slice)

        try:
            self._virtual_topology.update({s.get_slice_id(): s})
            self.log.info("new slice {i} was created".format(i=s.get_slice_id()))
            return False, s.get_slice_id()
        except Exception as ex:
            return True, ex

    @wamp.register(uri="{i}.add_virt_node")
    def add_virt_node(self, slice_id, vnode):
        try:
            s = self._virtual_topology.get(slice_id, None)
            if s is not None:
                s.add_virt_node(vnode)
                self._transport_topology.set_virtual_node(vnode["transport_device_id"],
                                                          vnode["virtual_device_id"])
                self.log.info("new virtual switch {i} was added".format(i=vnode["virtual_device_id"]))

                return False, None
            else:
                msg = "the virtual switch was not found"
                self.log.error(msg)
                return True, msg
        except Exception as ex:
            return True, ex

    @wamp.register(uri="{i}.rem_virt_node")
    def rem_virt_node(self, slice_id, vnode_id):
        try:
            s = self._virtual_topology.get(slice_id, None)
            if s is not None:
                s.rem_virt_node(vnode_id)
                self._transport_topology.del_virtual_node()
