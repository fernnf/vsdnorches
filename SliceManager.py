import json
from enum import Enum
from uuid import uuid4

import networkx as nx
import networkx.readwrite as nxparser
from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.python.failure import Failure

from SliceUtils import return_msg as result


class SliceTopologyDAO(object):
    def __init__(self, tenant_id, type="virtual_network", label=None, controller=""):
        self._slice_top = nx.Graph(tenant_id=tenant_id,
                                   slice_id=str(uuid4()),
                                   status=str(SliceStatus.CREATED),
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

        if SliceStatus.CREATED.value == code:
            self._slice_top.graph["status"] = str(SliceStatus.CREATED)
        elif SliceStatus.STOP.value == code:
            self._slice_top.graph["status"] = str(SliceStatus.STOP)
        elif SliceStatus.RUN.value == code:
            self._slice_top.graph["status"] = str(SliceStatus.RUN)
        elif SliceStatus.WITHDRAW.value == code:
            self._slice_top.graph["status"] = str(SliceStatus.WITHDRAW)
        elif SliceStatus.DEPLOY.value == code:
            self._slice_top.graph["status"] = str(SliceStatus.DEPLOY)
        elif SliceStatus.DONE.value == code:
            self._slice_top.graph["status"] = str(SliceStatus.DONE)
        elif SliceStatus.MODIFIED.value == code:
            self._slice_top.graph["status"] = str(SliceStatus.MODIFIED)
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

    def set_slice_node(self, device_id, datapath_id=None, type="virtual_switch", label=None, protocols=None):

        virtdev_id = str(uuid4())
        tenant_id = self.get_slice_tenant_id()

        if datapath_id is None:
            datapath_id = str(uuid4()).replace("-", "")[:16]

        self._slice_top.add_node(virtdev_id,
                                 device_id=device_id,
                                 tenant_id=tenant_id,
                                 datapath_id=datapath_id,
                                 type=type,
                                 label=label,
                                 protocols=protocols)

        return virtdev_id

    def get_slice_node(self, virtdev_id):
        assert self._slice_top.has_node(virtdev_id), "the virtual node {i} was not found".format(i=virtdev_id)

        nodes = self._slice_top.nodes(data=True)
        for n in nodes:
            id, _ = n
            if id == virtdev_id:
                return n

        return None

    def get_slice_nodes(self):
        nodes = self._slice_top.nodes(data=True)
        return nodes

    def del_slice_node(self, virtdev_id):
        assert self._slice_top.has_node(virtdev_id), "the node {i} was not found".format(i=virtdev_id)
        self._slice_top.remove_node(virtdev_id)

    def set_slice_link(self, src_virtdev_id, dst_virtdev_id, type="virtual_link", tunnel="vlan", key=None):
        assert self._slice_top.has_node(src_virtdev_id), "the node {i} was not found".format(i=src_virtdev_id)
        assert self._slice_top.has_node(dst_virtdev_id), "the node {i} was not found".format(i=dst_virtdev_id)

        def get_next(u):
            gen = self._slice_top.neighbors(u)
            nb = len([n for n in gen])
            return nb + 1

        link_id = str(uuid4())

        ingress = get_next(src_virtdev_id)
        egress = get_next(dst_virtdev_id)

        self._slice_top.add_edge(src_virtdev_id,
                                 dst_virtdev_id,
                                 ingress=ingress,
                                 egress=egress,
                                 link_id=link_id,
                                 type=type,
                                 tunnel=tunnel,
                                 key=key)

        return link_id

    def get_slice_link(self, link_id):
        ret, link = self.has_link(link_id)
        if not ret:
            raise ValueError("the link {i} was not found".format(i=link_id))

        return link

    def get_slice_links(self):
        return self._slice_top.edges(data=True)

    def del_slice_link(self, link_id):

        ret, link = self.has_link(link_id)
        if not ret:
            raise ValueError("the link {i} was not found".format(i=link_id))

        self._slice_top.remove_edge(link[0], link[1])

    def has_link(self, link_id):
        lks = self._slice_top.edges(data=True)
        for l in lks:
            if l[2]["link_id"] == link_id:
                return True, l
        return False, None


class SliceStatus(Enum):
    CREATED = 1
    DEPLOY = 2
    WITHDRAW = 3
    RUN = 4
    STOP = 5
    DONE = 6
    MODIFIED = 7

    def __str__(self):
        return self.name


class SliceManagerService(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super(SliceManagerService, self).__init__(*args, **kwargs)
        self._slices = {}

    @inlineCallbacks
    def _deploy_builder(self, slice):
        uri = "slicebuilderservice.deploy"
        yield self.call(uri, slice=slice.get_slice())

    @inlineCallbacks
    def _has_device_topo(self, device_id):
        uri = "topologyservice.has_node"
        data = yield self.call(uri, device_id=device_id)
        returnValue(data)

    @inlineCallbacks
    def onJoin(self, details):
        self.log.info("Slice Service Starting ...")
        yield self.register(self)
        self.log.info("Slice Service Started...")

    @wamp.register(uri="sliceservice.update_slice_status")
    def update_slice_status(self, slice_id, code):
        slice = self._slices.get(slice_id, None)
        if slice is None:
            error = 'sliceservice.error.update_slice_status.slice_not_found'
            raise ApplicationError(error)
        try:
            slice.set_slice_status(code)
        except Exception as ex:
            error = 'sliceservice.error.update_slice_status'
            raise ApplicationError(error, msg=str(ex))

    @wamp.register(uri="sliceservice.deploy_slice")
    def deploy_slice(self, slice_id):
        slice = self._slices.get(slice_id, None)

        if slice is None:
            error = 'sliceservice.error.deploy_slice.slice_not_found'
            raise ApplicationError(error)
        try:
            self._deploy_builder(slice)
        except Exception as ex:
            error = 'sliceservice.error.deploy_slice'
            raise ApplicationError(error, msg=str(ex))

    @wamp.register(uri="sliceservice.set_slice")
    def set_slice(self, tenant_id, label, controller):
        try:
            slice = SliceTopologyDAO(tenant_id=tenant_id,
                                     label=label,
                                     controller=controller)
            slice_id = slice.get_slice_id()
            self._slices.update({slice_id: slice})
            self.log.info("new slice <{i}> has created ".format(i=slice_id))

            return slice_id
        except Exception as ex:
            error = "sliceservice.error.set_slice"
            raise ApplicationError(error, msg=str(ex))

    @wamp.register(uri="sliceservice.del_slice")
    def del_slice(self, slice_id):

        def delete():
            status = slice.get_slice_status()
            if status == str(SliceStatus.RUN):
                raise ValueError("cannot delete a slice in running")
            elif status == str(SliceStatus.DEPLOY):
                raise ValueError("cannot delete a slice in deploying")
            elif status == str(SliceStatus.WITHDRAW):
                raise ValueError("cannot delete a slice in withdrawing")
            elif status == str(SliceStatus.CREATED):
                self._slices.pop(slice.get_slice_id())
                self.log.info("the slice <{i}> has deleted".format(i=slice_id))
            elif status == str(SliceStatus.STOP):
                pass
                # send a withdraw to slicebuilder
            else:
                pass

        try:
            slice = self._slices.get(slice_id, None)
            if slice is None:
                error = "sliceservice.error.del_slice.slice_not_found"
                raise ApplicationError(error)
            delete()
        except Exception as ex:
            error = "sliceservice.error.del_slice"
            raise ApplicationError(error, msg=str(ex))

    @wamp.register(uri="sliceservice.get_slice")
    def get_slice(self, slice_id):
        try:
            slice = self._slices.get(slice_id, None)
            if slice is None:
                error = "sliceservice.error.get_slice.slice_not_found"
                raise ApplicationError(error)
            ret = slice.get_slice()
            return ret
        except Exception as ex:
            error = "sliceservice.error.get_slice"
            raise ApplicationError(error, msg=str(ex))

    @wamp.register(uri="sliceservice.get_slices")
    def get_slices(self):
        try:
            slices = []
            if len(self._slices) == 0:
                error = "sliceservice.error.get_slices.no_slices"
                raise ApplicationError(error)

            for s in self._slices.values():
                slices.append(s.get_slice())

            return slices
        except Exception as ex:
            error = "sliceservice.error.get_slices"
            raise ApplicationError(error, msg=str(ex))

    @wamp.register(uri="sliceservice.set_slice_node")
    def set_slice_node(self, slice_id, device_id, datapath_id, label, protocols):
        try:
            slice = self._slices.get(slice_id, None)
            if slice is None:
                error = "sliceservice.error.set_slice_node.slice_not_found"
                raise ApplicationError(error)

            if self._has_device_topo(device_id):
                virtdev_id = slice.set_slice_node(device_id=device_id,
                                                  datapath_id=datapath_id,
                                                  label=label,
                                                  protocols=protocols)
                return virtdev_id

        except Exception as ex:
            error = "sliceservice.error.set_slice_node"
            raise ApplicationError(error, msg=str(ex))

    @wamp.register(uri="sliceservice.del_slice_node")
    def del_slice_node(self, slice_id, virtdev_id):
        try:
            slice = self._slices.get(slice_id, None)
            if slice is None:
                error = "sliceservice.error.del_slice_node.slice_not_found"
                raise ApplicationError(error)

            slice.del_slice_node(virtdev_id)
        except Exception as ex:
            error = "sliceservice.error.del_slice_node"
            raise ApplicationError(error, msg=str(ex))

    @wamp.register(uri="sliceservice.get_slice_node")
    def get_slice_node(self, slice_id, virtdev_id):
        try:
            slice = self._slices.get(slice_id, None)
            if slice is None:
                error = "sliceservice.error.get_slice_node.slice_not_found"
                raise ApplicationError(error)

            node = slice.get_slice_node(virtdev_id)
            return node
        except Exception as ex:
            error = "sliceservice.error.get_slice_node"
            raise ApplicationError(error, msg=str(ex))

    @wamp.register(uri="sliceservice.get_slice_nodes")
    def get_slice_nodes(self, slice_id):
        try:
            slice = self._slices.get(slice_id, None)
            if slice is None:
                error = "sliceservice.error.get_slice_nodes.slice_not_found"
                raise ApplicationError(error)

            nodes = slice.get_slice_nodes()
            return nodes
        except Exception as ex:
            error = "sliceservice.error.get_slice_nodes"
            raise ApplicationError(error, msg=str(ex))

    @wamp.register(uri="sliceservice.set_slice_link")
    def set_slice_link(self, slice_id, src_virtdev_id, dst_virtdev_id, tunnel, key):
        try:
            slice = self._slices.get(slice_id, None)
            if slice is None:
                error = "sliceservice.error.set_slice_link.slice_not_found"
                raise ApplicationError(error)

            virtlink_id = slice.set_slice_link(src_virtdev_id=src_virtdev_id,
                                               dst_virtdev_id=dst_virtdev_id,
                                               tunnel=tunnel,
                                               key=key)
            return virtlink_id
        except Exception as ex:
            error = "sliceservice.error.set_slice_link"
            raise ApplicationError(error, msg=str(ex))

    @wamp.register(uri="sliceservice.del_slice_link")
    def del_slice_link(self, slice_id, virtlink_id):
        try:
            slice = self._slices.get(slice_id, None)
            if slice is None:
                error = "sliceservice.error.del_slice_link.slice_not_found"
                raise ApplicationError(error)

            slice.del_slice_link(virtlink_id)
        except Exception as ex:
            error = "sliceservice.error.del_slice_link"
            raise ApplicationError(error, msg=str(ex))

    @wamp.register(uri="sliceservice.get_slice_link")
    def get_slice_link(self, slice_id, virtlink_id):
        try:
            slice = self._slices.get(slice_id, None)
            if slice is None:
                error = "sliceservice.error.get_slice_link.slice_not_found"
                raise ApplicationError(error)

            link = slice.get_slice_link(virtlink_id)
            return link
        except Exception as ex:
            error = "sliceservice.error.get_slice_link"
            raise ApplicationError(error, msg=str(ex))

    @wamp.register(uri="sliceservice.get_slice_links")
    def get_slice_links(self, slice_id):
        try:
            slice = self._slices.get(slice_id, None)
            if slice is None:
                error = "sliceservice.error.get_slice_links.slice_not_found"
                raise ApplicationError(error)

            link = slice.get_slice_links()
            return link
        except Exception as ex:
            error = "sliceservice.error.get_slice_links"
            raise ApplicationError(error, msg=str(ex))

    @wamp.register(uri="sliceservice.get_slice_status")
    def get_slice_status(self, slice_id):
        try:
            slice = self._slices.get(slice_id, None)
            if slice is None:
                error = "sliceservice.error.get_slice_status.slice_not_found"
                raise ApplicationError(error)

            status = slice.get_slice_status()
            return status
        except Exception as ex:
            error = "sliceservice.error.get_slice_status"
            raise ApplicationError(error, msg=str(ex))
