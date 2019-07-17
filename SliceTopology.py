from autobahn.twisted.wamp import ApplicationSession
from autobahn import wamp
import networkx as nx
import networkx.readwrite as nxparser
from uuid import uuid4

from SliceModels import TransportSwitch, TransportLink, TransportInterface
from SliceModels import VirtualInterface, VirtualSwitch, VirtualLink

PREFIX = "vsdnorches.topologyservice"


# TODO: Create injection from dictionary to model class

class TransportTopologyController(object):
    def __init__(self, type="physical_network", label=None):
        self._phy_top = nx.Graph(type=type, label=label)

    def _find_node(self, id):
        nodes = list(self._phy_top.nodes(data=True))
        if len(nodes) > 0:
            for n in nodes:
                did, _ = n
                if did == id:
                    return n
        else:
            return None

    def _find_link(self, id):
        links = list(self._phy_top.edges(data=True))
        for l in links:
            n1, n2, property = l
            lid = property["link_id"]
            if lid.__eq__(id):
                return l
        return None

    def _find_virt_nodes(self, id):
        node = self.get_node(id)
        _, property = node
        return property.get("virt_nodes", None)

    def get_type(self):
        return self._phy_top.graph.get("type", None)

    def get_label(self):
        return self._phy_top.graph.get("label", None)

    def set_label(self, label):
        self._phy_top.graph.update({"label": label})

    def get_nodes(self):
        return list(self._phy_top.nodes(data=True))

    def get_node(self, device_id):
        assert self._phy_top.has_node(device_id), "the node was not found"
        return self._find_node(device_id)

    def set_node(self, datapath_id, prefix_uri, label=None):
        device_id = str(uuid4())
        self._phy_top.add_node(device_id,
                               datapath_id=datapath_id,
                               prefix_uri=prefix_uri,
                               virt_nodes=[],
                               label=label)
        return device_id

    def del_node(self, device_id):
        if self._phy_top.has_node(device_id):
            self._phy_top.remove_node(device_id)
        else:
            raise ValueError("the node {i} was not found".format(i=id))

    def get_links(self):
        return list(self._phy_top.edges(data=True))

    def get_link(self, link_id):
        link = self._find_link(link_id)
        if link is not None:
            return link
        else:
            raise ValueError("the link {i} was not found".format(i=link_id))

    def set_link(self, source_id, target_id, source_portnum, target_portnum, tunnel=None, key=None):
        link_id = str(uuid4())
        self._phy_top.add_edge(source_id, target_id,
                               link_id=link_id,
                               ingress=source_portnum,
                               egress=target_portnum,
                               tunnel=tunnel,
                               key=key)
        return link_id

    def del_link(self, link_id):
        link = self._find_link(link_id)

        if link is not None:
            source = link[0]
            target = link[1]
            self._phy_top.remove_edge(source, target)
        else:
            raise ValueError("the link {i} was not found".format(i=link_id))

    def get_virt_nodes(self, device_id):
        return self._find_virt_nodes(device_id)

    def set_virt_node(self, device_id, virtdev_id):
        node = self.get_node(device_id)
        node[1]["virt_nodes"].append(virtdev_id)

    def del_virt_node(self, device_id, virtdev_id):
        node = self.get_node(device_id)
        node[1]["virt_nodes"].remove(virtdev_id)

    def len_virt_nodes(self, device_id):
        return len(self.get_virt_nodes(device_id))

    def get_topology(self):
        return nxparser.node_link_data(self._phy_top)

    @staticmethod
    def from_json(json):
        return nxparser.node_link_graph(json)


class SliceTopologyController(object):
    def __init__(self, tenant_id, type="virtual_network", label=None, controller=""):
        self._slice_top = nx.Graph(tenant_id=tenant_id,
                                   slice_id=str(uuid4()),
                                   status="CREATED",
                                   type=type,
                                   label=label,
                                   controller=controller)

    def get_slice_id(self):
        return self._slice_top.graph["slice_id"]

    def get_slice_status(self):
        return self._slice_top.graph["status"]

    def set_slice_status(self, code):
        status_code = {
            0: "CREATED",
            1: "DEPLOYED",
            2: "RUNNING",
            3: "STOPPED"
        }

        ret = status_code.get(code, None)
        if ret is not None:
            self._slice_top.graph["status"] = ret
        else:
            raise ValueError("the status code {i} is unknown".format(i=code))

    def get_slice_tenant_id(self):
        return self._slice_top.graph["tenant_id"]

    def set_slice_tenant_id(self, tenant_id):
        self._slice_top.graph["tenant_id"] = tenant_id

    def get_slice_label(self):
        return self._slice_top.graph["label"]

    def set_slice_label(self, label):
        self._slice_top.graph["label"] = label

    def get_slice_controller(self):
        return self._slice_top.graph["controller"]

    def set_slice_controller(self, controller):
        self._slice_top.graph["controller"] = controller

    def set_slice_node(self, physical_id, datapath_id=None, type="virtual_switch", label=None, protocols=None):

        device_id = str(uuid4())
        tenant_id = self.get_slice_tenant_id()

        if datapath_id is None:
            datapath_id = str(uuid4())[:16]

        self._slice_top.add_node(device_id,
                                 physical_id=physical_id,
                                 tenant_id=tenant_id,
                                 datapath_id=datapath_id,
                                 type=type,
                                 label=label,
                                 protocols=protocols)

        return device_id

    def get_slice_node(self, device_id):
        assert self._slice_top.has_node(device_id), "the node {i} was not found".format(i=device_id)

        nodes = self._slice_top.nodes(data=True)
        for n in nodes:
            id, _ = n
            if id == device_id:
                return n

        return None

    def del_slice_node(self, device_id):
        assert self._slice_top.has_node(device_id), "the node {i} was not found".format(i=device_id)
        self._slice_top.remove_node(device_id)

    def get_slice_count_node(self):
        return self._slice_top.number_of_nodes()

    def set_slice_link(self, src_device_id, dst_device_id, type="virtual_link", tunnel="vlan", key=None):
        assert self._slice_top.has_node(src_device_id), "the node {i} was not found".format(i=src_device_id)
        assert self._slice_top.has_node(dst_device_id), "the node {i} was not found".format(i=dst_device_id)

        link_id = str(uuid4())

        self._slice_top.add_edge(src_device_id,
                                 dst_device_id,
                                 link_id=link_id,
                                 type=type,
                                 tunnel=tunnel,
                                 key=key)

        return link_id

    def get_slice_link(self, link_id):
        links = self._slice_top.edges(data = True)

        for l in links:
            if l[2]["link_id"] == link_id:
                return l

        return None

    def del_slice_link(self, link_id):
        links = self._slice_top.edges(data = True)
        for l in links:
            if l[2]["link_id"] == link_id:
                source = l[0]
                target = l[1]
                self._slice_top.remove_edge(source, target)
                return True

        return None


class TopologyService(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super(TopologyService, self).__init__(*args, **kwargs)
        self._transport_topology = TransportTopologyController(label="Transport")
        self._virtual_topology = []

    def onJoin(self, details):
        self.log.info("Starting Topology Service...")

    @wamp.register(uri="{p}.set_phy_node".format(p=PREFIX))
    def set_phy_node(self, datapath_id, prefix_uri, label):
        try:
            device_id = self._transport_topology.set_node(datapath_id, prefix_uri, label)
            self.log.info("new transport device {i} has added".format(i=device_id))
            return False, device_id
        except Exception as ex:
            return True, ex

    @wamp.register(uri="{p}.del_phy_node".format(p=PREFIX))
    def del_phy_node(self, device_id):

        try:
            self._transport_topology.del_node(device_id)
            self.log.info("the transport device {i} was remove".format(i=device_id))
            return False, None
        except Exception as ex:
            return True, ex

    @wamp.register(uri="{p}.set_phy_link".format(p=PREFIX))
    def add_phy_link(self, link):
        try:
            self._transport_topology.add_link(link)
            self.log.info("new physical link {i} was added".format(i=link["link_id"]))
            return False, None
        except Exception as ex:
            return True, ex

    @wamp.register(uri="{p}.rem_phy_link".format(p=PREFIX))
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

    @wamp.register(uri="{p}.create_slice".format(p=PREFIX))
    def create_slice(self, slice):
        s = SliceTopologyController(slice=slice)

        try:
            self._virtual_topology.update({s.get_slice_id(): s})
            self.log.info("new slice {i} was created".format(i=s.get_slice_id()))
            return False, None
        except Exception as ex:
            return True, ex

    @wamp.register(uri="{p}.add_virt_node".format(p=PREFIX))
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

    """
    @wamp.register(uri="{i}.rem_virt_node")
    def rem_virt_node(self, slice_id, vnode_id):
        try:
            s = self._virtual_topology.get(slice_id, None)
            if s is not None:
                s.rem_virt_node(vnode_id)
                for n in s.get_nodes():

                    self._transport_topology.del_virtual_node()
    """
