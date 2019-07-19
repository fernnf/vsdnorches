from uuid import uuid4
import networkx as nx
import networkx.readwrite as nxparser

from autobahn.twisted.wamp import ApplicationSession
from autobahn import wamp

from twisted.internet.defer import inlineCallbacks


class SliceTopologyDAO(object):
    def __init__(self, tenant_id, type="virtual_network", label=None, controller=""):
        self._slice_top = nx.Graph(tenant_id=tenant_id,
                                   slice_id=str(uuid4()),
                                   status="CREATED",
                                   type=type,
                                   label=label,
                                   controller=controller)

    def get_slice(self):
        return nxparser.node_link_data(self._slice_top)

    def get_slice_id(self):
        return self._slice_top.graph["slice_id"]

    def get_slice_status(self):
        return self._slice_top.graph["status"]

    def set_slice_status(self, code):
        status_code = {
            0: "CREATED",
            1: "DEPLOY",
            2: "WITHDRAW",
            3: "RUN",
            4: "STOP"
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
        links = self._slice_top.edges(data=True)

        for l in links:
            if l[2]["link_id"] == link_id:
                return l

        return None

    def del_slice_link(self, link_id):
        links = self._slice_top.edges(data=True)
        for l in links:
            if l[2]["link_id"] == link_id:
                source = l[0]
                target = l[1]
                self._slice_top.remove_edge(source, target)
                return True

        return None


class SliceManager(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super(SliceManager, self).__init__(*args, **kwargs)
        self._slices = {}
        self.log.info("Starting Slice Manager...")

    @inlineCallbacks
    def onJoin(self, details):
        self.log.info("Slice Manager Starting ...")
        yield self.register(self)
        self.log.info("Slice Manager Started...")

    @wamp.register(uri="slicemanager.set_slice")
    def set_slice(self, tenant_id, label, controller):
        try:
            slice = SliceTopologyDAO(tenant_id=tenant_id,
                                     label=label,
                                     controller=controller)
            slice_id = slice.get_slice_id()
            self._slices.update({slice_id: slice})
            return False, slice_id
        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="slicemanager.del_slice")
    def del_slice(self, slice_id):
        try:
            slice = self._slices.get(slice_id, None)
            if slice is not None:
                status = slice.get_slice_status()
                if status == "RUN":
                    return True, "cannot delete a slice in running"
                elif status == "DEPLOY":
                    return True, "cannot delete a slice in deploying"
                elif status == "WITHDRAW":
                    return True, "cannot delete a slice in withdrawing"
                elif status == "CREATED":
                    self._slices.pop(slice.get_slice_id())
                    return False, None
                elif status == "STOPPED":
                    pass
                    #send a withdraw to slicebuilder
                else:
                    pass
            else:
                return True, "slice <{i}> was not found".format(i=slice_id)
        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="slicemanager.get_slice")
    def get_slice(self, slice_id):
        try:
            slice = self._slices.get(slice_id, None)
            if slice is not None:
                return False, slice.get_slice()
            else:
                return True, "slice <{i}> was not found".format(i=slice_id)
        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="slicemanager.get_slices")
    def get_slices(self):
        slices = []
        if self._slices.__len__() > 0:
            for v in self._slices.values():
                slices.append(v.get_slice())

            return False, slices
        else:
            return True, "There is no slices"

    @inlineCallbacks
    @wamp.register(uri="slicemanager.set_slice_node")
    def set_slice_node(self, slice_id, device_id, datapath_id, label, protocols):
        try:
            err, msg = yield self.call("topologyservice.has_node", device_id)
            if err:
                return True, msg

            slice = self._slices.get(slice_id, None)
            if slice is not None:

        except Exception as ex:
