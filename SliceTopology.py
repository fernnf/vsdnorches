from uuid import uuid4

import networkx as nx
import networkx.readwrite as nxparser
from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession
from twisted.internet.defer import inlineCallbacks

PREFIX = "topologyservice"


# TODO: Create injection from dictionary to model class

class TopologyDAO(object):
    def __init__(self, type="physical_network", label=None):
        self._topo = nx.Graph(type=type, label=label)

    def _find_node(self, id):
        nodes = list(self._topo.nodes(data=True))
        if len(nodes) > 0:
            for n in nodes:
                did, _ = n
                if did == id:
                    return n
        else:
            return None

    def _find_link(self, id):
        links = list(self._topo.edges(data=True))
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
        return self._topo.graph.get("type", None)

    def get_label(self):
        return self._topo.graph.get("label", None)

    def set_label(self, label):
        self._topo.graph.update({"label": label})

    def get_nodes(self):
        return list(self._topo.nodes(data=True))

    def get_node(self, device_id):
        assert self._topo.has_node(device_id), "device {i} was not found".format(i=device_id)
        return self._find_node(device_id)

    def set_node(self, datapath_id, prefix_uri, label=None):
        device_id = str(uuid4())
        self._topo.add_node(device_id,
                            datapath_id=datapath_id,
                            prefix_uri=prefix_uri,
                            virt_nodes=[],
                            label=label)
        return device_id

    def del_node(self, device_id):
        assert self._topo.has_node(device_id), "Cannot del {i}, node was not found".format(i=device_id)
        self._topo.remove_node(device_id)

    def has_node(self, device_id):
        return self._topo.has_node(device_id)

    def get_links(self):
        return list(self._topo.edges(data=True))

    def get_link(self, link_id):
        link = self._find_link(link_id)
        if link is not None:
            return link
        else:
            raise ValueError("the link {i} was not found".format(i=link_id))

    def set_link(self, source_id, target_id, source_portnum, target_portnum, tunnel=None, key=None):
        if self.has_link(source_id, target_id) is not None:
            raise ValueError("there is a link between <{s},{t}>".format(s=source_id, t=target_id))

        link_id = str(uuid4())
        self._topo.add_edge(source_id, target_id,
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
            self._topo.remove_edge(source, target)
        else:
            raise ValueError("the link {i} was not found".format(i=link_id))

    def has_link(self, source_id, target_id):

        if self._topo.has_edge(source_id, target_id):
            proper = self._topo.get_edge_data(source_id,target_id)
            return proper
        else:
            raise ValueError("the link <{s},{t}> was not found".format(s=source_id, t=target_id))

    def get_virt_instaces(self, device_id):
        return self._find_virt_nodes(device_id)

    def set_virt_instance(self, device_id, virtdev_id):
        node = self.get_node(device_id)
        node[1]["virt_nodes"].append(virtdev_id)

    def del_virt_instace(self, device_id, virtdev_id):
        node = self.get_node(device_id)
        node[1]["virt_nodes"].remove(virtdev_id)

    def len_virt_instaces(self, device_id):
        return len(self.get_virt_instaces(device_id))

    def get_shortest_path(self, source_id, target_id):
        return nx.shortest_path(self._topo, source_id, target_id)


    def get_topology(self):
        return nxparser.node_link_data(self._topo)

    @staticmethod
    def from_json(json):
        return nxparser.node_link_graph(json)


class TopologyService(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super(TopologyService, self).__init__(*args, **kwargs)
        self._topo = TopologyDAO(label="Transport")



    @inlineCallbacks
    def onJoin(self, details):
        self.log.info("Topology Service Starting ...")
        yield self.register(self)
        yield self.subscribe(self)
        self.log.info("Topology Service Started ...")

    @wamp.subscribe(uri="topologyservice.new_device")
    def new_device(self, msg):
        try:
            device_id = self._topo.set_node(datapath_id=msg["datapath_id"],
                                            prefix_uri=msg["prefix_uri"],
                                            label=msg["label"])
            self.log.info("new device <{i}> has added to topology".format(i=device_id))
        except Exception as ex:
            self.log.error(str(ex))

    @wamp.register(uri="topologyservice.set_node")
    def set_node(self, datapath_id, prefix_uri, label):
        try:
            device_id = self._topo.set_node(datapath_id=datapath_id,
                                            prefix_uri=prefix_uri,
                                            label=label)
            self.log.info("new device <{i}> has added to topology".format(i=device_id))
            return False, device_id
        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="topologyservice.del_node")
    def del_node(self, device_id):

        try:
            self._topo.del_node(device_id)
            self.log.info("the device <{i}> was remove from topology".format(i=device_id))
            return False, None
        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="topologyservice.get_node")
    def get_node(self, device_id):
        try:
            node = self._topo.get_node(device_id)
            return False, node
        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="topologyservice.get_nodes")
    def get_nodes(self):
        try:
            nodes = self._topo.get_nodes()
            return False, nodes
        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="topologyservice.has_node")
    def has_node(self, device_id):
        try:
            msg = self._topo.has_node(device_id)
            return False, msg
        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="topologyservice.set_link")
    def set_link(self, source_id, target_id, source_portnum, target_portnum, tunnel, key):
        try:
            link_id = self._topo.set_link(source_id=source_id,
                                          target_id=target_id,
                                          source_portnum=source_portnum,
                                          target_portnum=target_portnum,
                                          tunnel=tunnel,
                                          key=key)
            self.log.info("new link <{i}> has added to topology".format(i=link_id))
            return False, link_id

        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="topologyservice.del_link")
    def del_link(self, link_id):
        try:
            self._topo.del_link(link_id)
            self.log.info("the link <{i}> has removed from topology".format(i=link_id))
            return False, None
        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="topologyservice.get_link")
    def get_link(self, link_id):
        try:
            link = self._topo.get_link(link_id)
            return False, link
        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="topologyservice.get_links")
    def get_links(self):
        try:
            links = self._topo.get_links()
            return False, links
        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="topologyservice.has_link")
    def has_link(self, source_id, target_id):
        try:
            proper = self._topo.has_link(source_id, target_id)
            return False, proper
        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="topologyservice.set_instance")
    def set_instance(self, device_id, virt_device_id):
        try:
            self._topo.set_virt_instance(device_id, virt_device_id)
            return False, None
        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="topologyservice.del_instance")
    def del_instance(self, device_id, virt_device_id):
        try:
            self._topo.del_virt_instace(device_id, virt_device_id)
            return False, None
        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="topologyservice.get_instances")
    def get_instances(self, device_id):
        try:
            virt = self._topo.get_virt_instaces(device_id)
            return False, virt
        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="topologyservice.get_shortest_path")
    def get_shortest_path(self, source_id, target_id):
        try:
            path = self._topo.get_shortest_path(source_id, target_id)
            return False, path
        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="topologyservice.get_topology")
    def get_topology(self):
        try:
            topo = self._topo.get_topology()
            return False, topo
        except Exception as ex:
            return True, str(ex)


"""
    @wamp.register(uri="{p}.set_phy_link".format(p=PREFIX))
    def set_phy_link(self, link):
        try:
            self._phy_topo.add_link(link)
            self.log.info("new physical link {i} was added".format(i=link["link_id"]))
            return False, None
        except Exception as ex:
            return True, ex

    @wamp.register(uri="{p}.rem_phy_link".format(p=PREFIX))
    def rem_phy_link(self, link_id):
        try:
            error, d = self._phy_topo.get_link(link_id)
            if not error:
                self._phy_topo.rem_link(d[0], d[1])
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
                self._phy_topo.set_virtual_node(vnode["transport_device_id"],
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
