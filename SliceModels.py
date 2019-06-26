import time

from uuid import uuid4 as rnd_id

from enum import Enum, unique


def get_deploy_time():
    return time.asctime(time.localtime(time.time()))


def serial_dict(d):
    for k, v in d.items():
        d.update({k: v.serialize()})
    return d


def serial_list(l: list):
    t = []
    for v in l:
        t.append(v.serialize())
    return t.copy()


def get_id(dpid=None):
    rnd = rnd_id()
    if dpid is None:
        return rnd
    else:
        assert len(dpid) == 16, "dpid must have 16 digits hex decimal"
        return dpid + rnd[16:]


class SliceStatus(Enum):
    CREATED = 0
    DEPLOYING = 1
    DEPLOYED = 2
    RUNNING = 3
    STOPPED = 4
    ERROR = 5


class VirtualInterface(object):
    """
        vport = {
            type: "virtual_interface"
            interface_id: string
            vport_num: int
            tport_num: int
            properties: {
                vswitch_id: string
                bandwidth: long
                reserved: bool
                encap: String (e.g. Ethernet)
            }
        }

    """

    def __init__(self, vport_num, tport_num, vswitch_id, reserved=False, bandwidth=None, encap="Ethernet"):
        self.__id = get_id()
        self.vswitch_id = vswitch_id
        self.vport_num = vport_num
        self.tport_num = tport_num
        self.reserved = reserved
        self.bandwidth = bandwidth
        self.encap = encap
        self.type = "virtual_interface"

    @property
    def interface_id(self):
        return self.__id

    @interface_id.setter
    def interface_id(self, value):
        pass

    @property
    def vswitch_id(self):
        return self.__vsw

    @vswitch_id.setter
    def vswitch_id(self, value):
        self.__vsw = value

    @property
    def vport_num(self):
        return self.__vp

    @vport_num.setter
    def vport_num(self, value):
        self.__vp = value

    @property
    def tport_num(self):
        return self.__tp

    @tport_num.setter
    def tport_num(self, value):
        self.__tp = value

    @property
    def reserved(self):
        return self.__reserv

    @reserved.setter
    def reserved(self, value):
        self.__reserv = value

    @property
    def bandwidth(self):
        return self.__bwd

    @bandwidth.setter
    def bandwidth(self, value):
        self.__bwd = value

    @property
    def encap(self):
        return self.__encap

    @encap.setter
    def encap(self, value):
        self.__encap = value

    @classmethod
    def parser(cls, d):
        obj = cls(d["vswitch"], d["vport_num"], d["tport_num"], d["reserved"], d["bandwidth"], d["encap"])
        obj.__id = d["id"]

        return obj

    def serialize(self):
        vport = {
            "type": self.type,
            "interface_id": self.interface_id,
            "vport_num": self.vport_num,
            "tport_num": self.tport_num,
            "properties": {
                "vswitch_id": self.vswitch_id,
                "bandwidth": self.bandwidth,
                "reserved": self.reserved,
                "encap": self.encap
            },
        }

        return vport.copy()

    def __str__(self):
        return str(self.serialize())


class VirtualSwitch(object):
    """
        vswitch = {
            type: "virtual_switch"
            device_id: string,
            tenant_id: string,
            tswitch_id: string,
            label: string,
            properties:{
                dpid: string,
                protocols: [string] (e.g., OpenFlow13 or None)
            }
            interfaces:[
                interface_id: objects (VirtualPort)
            ]
    """

    def __init__(self, tenant_id, tswitch_id, label=None, dpid=None, protocols=None):
        self.__device_id = get_id(dpid=dpid)
        self.type = "virtual_switch"
        self.label = label
        self.tenant_id = tenant_id
        self.tswitch_id = tswitch_id
        self.dpid = dpid
        self.protocols = protocols
        self.__interfaces = {}

    @property
    def device_id(self):
        return self.__device_id

    @device_id.setter
    def device_id(self, value):
        pass

    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, value):
        if value is None:
            self.__label = self.dpid

        self.__label = value

    @property
    def dpid(self):
        return self.__dpid

    @dpid.setter
    def dpid(self, value):
        if value is None:
            self.__dpid = self.device_id[:16]
        else:
            assert len(value) == 16, "dpid must have 16 digits hex decimal"
            self.__dpid = value

    @property
    def tenant_id(self):
        return self.__tenant

    @tenant_id.setter
    def tenant_id(self, value):
        self.__tenant = value

    @property
    def tswitch_id(self):
        return self.__tsw

    @tswitch_id.setter
    def tswitch_id(self, value):
        self.__tsw = value

    @property
    def protocols(self):
        return self.__proto

    @protocols.setter
    def protocols(self, value):
        self.__proto = value

    def add_interface(self, interface):
        id = interface.interface_id
        p = self.__interfaces.get(id, None)
        if p is None:
            self.__interfaces.update({id: interface})
        else:
            raise ValueError("the interface already was registered")

    def rem_interface(self, interface_id):
        ret = self.__interfaces.get(interface_id, None)

        if ret is None:
            raise ValueError("the interface was not registered")
        else:
            self.__interfaces.pop(interface_id)

    def get_interfaces(self):
        return self.__interfaces.values()

    def get_interface(self, interface_id):
        return self.__interfaces.get(interface_id, None)

    def __hash__(self) -> int:
        return super().__hash__()

    @classmethod
    def parser(cls, d):
        obj = cls(tenant_id=d["tenant_id"],
                  label=d["label"],
                  tswitch_id=d["tswitch_id"],
                  dpid=d["dpid"],
                  protocols=d["protocols"])

        obj.__id = d["id"]

        if len(d["interfaces"]) > 0:
            interfaces = dict(d["interfaces"])

            for interface in interfaces:
                o = VirtualInterface.parser(interface)
                obj.add_interface(o)

        return obj

    def serialize(self):

        vswitch = {
            "type": self.type,
            "device_id": self.device_id,
            "tenant_id": self.tenant_id,
            "tswitch_id": self.tswitch_id,
            "label": self.label,
            "properties": {
                "dpid": self.dpid,
                "protocols": self.protocols
            },
            "interfaces": {
                "interface_id": serial_dict(self.__interfaces)
            }
        }

        return vswitch.copy()


class VirtualLink(object):
    """
        vlink = {
            type: "virtual_link"
            link_id: string
            ingress: {
                interface_id: string
                vswitch_id: string
            }
            egress:{
                interface_id: string
                vswitch_id: string
            }
            properties {
                tunnel: string (e.g., Vlan, Vxlan)
                key: string
            }
        }

    """

    def __init__(self, ingress, egress, tunnel, key):
        self.__link_id = get_id()
        self.type = "virtual_link"
        self.ingress = ingress
        self.egress = egress
        self.tunnel = tunnel
        self.key = key

    @property
    def link_id(self):
        return self.__link_id

    @link_id.setter
    def link_id(self, value):
        pass

    @property
    def ingress(self):
        return self.__ip

    @ingress.setter
    def ingress(self, value):
        self.__ip = value

    @property
    def egress(self):
        return self.__ep

    @egress.setter
    def egress(self, value):
        self.__ep = value

    @property
    def tunnel(self):
        return self.__tunnel

    @tunnel.setter
    def tunnel(self, value):
        self.__tunnel = value

    @property
    def key(self):
        return self.__key

    @key.setter
    def key(self, value):
        self.__key = value

    @classmethod
    def parser(cls, d):
        obj = cls(ingress=d["ingress"],
                  egress=d["egress"],
                  tunnel=d["tunnel"],
                  key=d["key"])

        obj.__link_id = d["link_id"]

        return obj

    def serialize(self):
        vlink = {
            "type": self.type,
            "link_id": self.link_id,
            "ingress": {
                "interface_id": self.ingress["interface_id"],
                "vswitch_id": self.ingress["vswitch_id"]
            },
            "egress": {
                "interface_id": self.egress["interface_id"],
                "vswitch_id": self.egress["vswitch_id"]
            },
            "properties": {
                "tunnel": self.tunnel,
                "key": self.key
            }
        }

        return vlink.copy()


class TransportSwitch(object):
    """
        tswitch = {
            type: const ("transport_switch")
            device_id: string,
            interfaces {
                interface_id: object (transport_interface)
            }
            properties: {
                dpid: string
                prefix: string
            }
        }
    """

    def __init__(self, dpid, prefix):
        self.__device_id = get_id(dpid)
        self.dpid = dpid
        self.prefix = prefix
        self.__interfaces = {}

    @property
    def device_id(self):
        return self.__device_id

    @device_id.setter
    def device_id(self, value):
        pass

    @property
    def dpid(self):
        return self.__dpid

    @dpid.setter
    def dpid(self, value):
        self.__dpid = value

    @property
    def prefix(self):
        return self.__prefix

    @prefix.setter
    def prefix(self, value):
        self.__prefix = value

    def add_interface(self, interface):

        id = interface.interface_id

        ret = self.__interfaces.get(id, None)
        if ret is None:
            self.__interfaces.update({id: interface})
        else:
            raise ValueError("the interface already has registered")

    def rem_interface(self, interface_id):
        ret = self.__interfaces.get(interface_id, None)
        if ret is None:
            raise ValueError("the interface was not found")
        else:
            self.__interfaces.pop(interface_id)

    def get_interface(self, interface_id):
        return self.__interfaces.get(interface_id, None)

    def get_interfaces(self):
        return self.__interfaces.copy()

    @classmethod
    def parser(cls, d):
        obj = cls(d["dpid"], d["prefix"])

        obj.__id = d["id"]

        if len(d["interfaces"]) > 0:
            interfaces = dict(d["interfaces"])
            for interface in interfaces:
                o = TransportInterface.parser(interface)
                obj.add_interface(o)

        return obj

    def serialize(self):

        tswitch = {
            "type": "transport_switch",
            "device_id": self.device_id,
            "interfaces": serial_dict(self.__interfaces),
            "properties": {
                "dpid": self.dpid,
                "prefix": self.prefix
            }
        }

        return tswitch.copy()

    def __hash__(self) -> int:
        return super().__hash__()


class TransportLinks(object):
    """
        tlink = {
            type: "transport_switch"
            link_id: string,
            ingress: {
                interface_id: string
                device_id: string
            }
            egress:{
                interface_id: string
                device_id: string
            }
        }
    """

    @classmethod
    def parser(cls, d):
        obj = cls(d["ingress"], d["egress"])
        obj.__link_id = d["link_id"]
        return obj

    def __init__(self, ingress, egress):
        self.type = "transport_switch"
        self.link_id = get_id()
        self.ingress = ingress
        self.egress = egress

    @property
    def link_id(self):
        return self.__link_id

    @link_id.setter
    def link_id(self, value):
        self.__link_id = value

    @property
    def ingress(self):
        return self.__ingress

    @ingress.setter
    def ingress(self, value):
        self.__ingress = value

    @property
    def egress(self):
        return self.__egress

    @egress.setter
    def egress(self, value):
        self.__egress = value

    def serialize(self):
        tlink = {
            "type": "transport_switch",
            "link_id": self.link_id,
            "ingress": {
                "interface_id": self.ingress["interface_id"],
                "device_id": self.ingress["device_id"]
            },
            "egress": {
                "interface_id": self.egress["interface_id"],
                "device_id": self.egress["device_id"]
            }
        }

        return tlink.copy()


class TransportInterface(object):
    """
        tport = {
            type: "transport_interface"
            id: string,
            properties:{
                device_id: string
                port_num: int
                encap: string
            }
        }
    """

    def __init__(self, device_id, port_num, encap="eth"):
        self.type = "transport_interface"
        self.interface_id = get_id()
        self.device_id = device_id
        self.port_num = port_num
        self.encap = encap

    @property
    def interface_id(self):
        return self.__interface_id

    @interface_id.setter
    def interface_id(self, value):
        self.__interface_id = value

    @property
    def device_id(self):
        return self.__device_id

    @device_id.setter
    def device_id(self, value):
        self.__device_id = value

    @property
    def port_num(self):
        return self.__port_num

    @port_num.setter
    def port_num(self, value):
        self.__port_num = value

    @property
    def encap(self):
        return self.__encap

    @encap.setter
    def encap(self, value):
        self.__encap = value

    @classmethod
    def parser(cls, d):
        obj = cls(device_id=d["device_id"],
                  port_num=d["port_num"],
                  encap=d["encap"])

        obj.__id = d["id"]
        return obj

    def serialize(self):
        tport = {
            "type": "transport_interface",
            "interface_id": self.interface_id,
            "properties": {
                "device_id": self.device_id,
                "port_num": self.port_num,
                "encap": self.encap
            }
        }

        return tport.copy()

    def __hash__(self) -> int:
        return super().__hash__()


class NetworkSlice(object):
    """
        netslice = {
            type: "virtual_network"
            slice_id: string,
            tenant_id: string
            label: string
            properties: {
                status: string
                revision: string
                controller: string
            }
            nodes: {
                device_id: object
            }

            links {
                link_id: object
            }
        }
    """

    def __init__(self, tenant_id, label, controller):

        self.type = "virtual_network"
        self.slice_id = get_id()
        self.tenant_id = tenant_id
        self.label = label
        self.status = SliceStatus.CREATED
        self.revision = get_deploy_time()
        self.controller = controller
        self.__nodes = {}
        self.__links = {}

    @property
    def slice_id(self):
        return self.__slice_id

    @slice_id.setter
    def slice_id(self, value):
        self.__slice_id = value

    @property
    def tenant_id(self):
        return self.__tenant_id

    @tenant_id.setter
    def tenant_id(self, value):
        self.__tenant_id = value

    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, value):
        self.__label = value

    @property
    def revision(self):
        return self.__revision

    @revision.setter
    def revision(self, value):
        self.__revision = value

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):

        self.__status = value

    @property
    def controller(self):
        return self.__controller

    @controller.setter
    def controller(self, value):
        self.__controller = value

    def add_node(self, device):

        id = device.device_id

        ret = self.__nodes.get(id, None)
        if ret is None:
            self.__nodes.update({id: device})
        else:
            raise ValueError("the node already has been included")

    def rem_node(self, device_id):

        ret = self.__nodes.get(device_id, None)
        if ret is None:
            raise ValueError("the node was not found")
        else:
            self.__nodes.pop(device_id)

    def get_node(self, device_id):
        return self.__nodes.get(device_id, None)

    def get_nodes(self):
        return self.__nodes.values()

    def add_link(self, link):
        id = link.link_id
        ret = self.__links.get(id)
        if ret is None:
            self.__nodes.update({id: link})
        else:
            raise ValueError("the link already has been included")

    def rem_link(self, link_id):

        ret = self.__links.get(link_id, None)
        if ret is None:
            raise ValueError("the node was not found")
        else:
            self.__links.pop(link_id)

    def get_link(self, link_id):
        return self.__links.get(link_id, None)

    def get_links(self):
        return self.__links.values()

    @classmethod
    def parser(cls, d: dict):
        obj = cls(tenant_id=d["tenant_id"],
                  controller=d["controller"],
                  label=d["label"])

        obj.__status = d["status"]
        obj.__revision = d["revision"]
        obj.__slice_id = d["slice_id"]

        if len(d["nodes"]) > 0:
            nodes = d["nodes"]
            for node in nodes:
                n = VirtualSwitch.parser(node)
                obj.add_node(n)

        if len(d["links"]) > 0:
            links = d["links"]
            for link in links:
                o = VirtualLink.parser(link)
                obj.add_link(link=o)

        return cls

    def serialize(self):

        netslice = {
            "type": "virtual_network",
            "slice_id": self.slice_id,
            "tenant_id": self.tenant_id,
            "label": self.label,
            "properties": {
                "status": self.status,
                "revision": self.revision,
                "controller": self.controller
            },
            "nodes": serial_dict(self.__nodes),

            "links": serial_dict(self.__links)
        }

        return netslice.copy()

    def __hash__(self) -> int:
        return super().__hash__()
