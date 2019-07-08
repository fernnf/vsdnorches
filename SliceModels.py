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


class VirtualSwitch(object):
    """
        vswitch = {
            "type": "virtual_switch"
            "virtual_device_id": string,
            "transport_device_id": string
            "tenant_id": string,
            "label": string,
            "datapath_id": string
            "protocols": list
            "interfaces": { "string"}
        }
    """

    def __init__(self):
        self._type = "virtual_switch"
        self._virtual_device_id = get_id()
        self._transport_device_id = None
        self._tenant_id = None
        self._label = None
        self._datapath_id = None
        self._protocols = []

    def get_type(self):
        return self._type

    def get_id(self):
        return self._virtual_device_id

    def get_transport_device_id(self):
        return self._transport_device_id

    def get_tenant_id(self):
        return self._tenant_id

    def get_label(self):
        return self._label

    def get_datapath_id(self):
        return self._datapath_id

    def get_protocols(self):
        return self._protocols

    def set_transport_device_id(self, device_id):
        self._transport_device_id = device_id

    def set_tenant_id(self, tenant_id):
        self._tenant_id = tenant_id

    def set_label(self, label):
        self._label = label

    def set_datapath_id(self, dpid=None):
        if dpid is None:
            dpid = str(rnd_id())[:16]

        self._datapath_id = dpid

    def set_protocols(self, protocols):
        self._protocols = protocols

    @classmethod
    def parser(cls, d):
        obj = cls()

        obj._virtual_device_id = d["virtual_device_id"]
        obj.set_transport_device_id(device_id=d["transport_device_id"])
        obj.set_tenant_id(tenant_id=d["tenant_id"])
        obj.set_label(label=d["label"])
        obj.set_datapath_id(dpid=d["datapath_id"])
        obj.set_protocols(protocols=d["protocols"])

        return obj

    def serialize(self):
        vswitch = {
            "type": self.get_type(),
            "virtual_device_id": self.get_id(),
            "transport_device_id": self.get_transport_device_id(),
            "tenant_id": self.get_tenant_id(),
            "label": self.get_label(),
            "datapath_id": self.get_datapath_id(),
            "protocols": self.get_protocols(),
        }

        return vswitch.copy()


class VirtualInterface(object):
    """
        vport = {
            "type": "virtual_interface"
            "interface_id": string
            "device_id": string
            "virtual_portnum": int
            "transport_portnum": int
            "reserved": bool
            "bandwidth": string
            "encap": string
        }

    """

    def __init__(self):
        self._type = "virtual_interface"
        self._interface_id = get_id()
        self._device_id = None
        self._virt_portnum = None
        self._phy_portnum = None
        self._reserved = None
        self._bandwidth = None
        self._encap = None

    def get_type(self):
        return self._type

    def get_id(self):
        return self._interface_id

    def get_device_id(self):
        return self._device_id

    def get_virt_portnum(self):
        return self._virt_portnum

    def get_phy_portnum(self):
        return self._phy_portnum

    def get_reserved(self):
        return self._reserved

    def get_bandwidth(self):
        return self._bandwidth

    def get_encap(self):
        return self._encap

    def set_device_id(self, device_id):
        self._device_id = device_id

    def set_vir_portnum(self, virt_portnum):
        self._virt_portnum = virt_portnum

    def set_phy_portnum(self, phy_portnum):
        self._phy_portnum = phy_portnum

    def set_reserved(self, reserved):
        self._reserved = reserved

    def set_bandwidth(self, bandwidth):
        self._bandwidth = bandwidth

    def set_encap(self, encap):
        self._encap = encap

    @classmethod
    def parser(cls, d):
        obj = cls()
        obj._interface_id = d["id"]
        obj.set_device_id(device_id=d["device_id"])
        obj.set_phy_portnum(phy_portnum=d["phy_portnum"])
        obj.set_vir_portnum(virt_portnum=d["vir_portnum"])
        obj.set_reserved(reserved=d["reserved"])
        obj.set_bandwidth(bandwidth=d["bandwidth"])
        obj.set_encap(encap=d["encap"])

        return obj

    def serialize(self):
        vport = {
            "type": self.get_type(),
            "interface_id": self.get_id(),
            "device_id": self.get_device_id(),
            "virt_portnum": self.get_virt_portnum(),
            "phy_portnum": self.get_phy_portnum(),
            "reserved": self.get_reserved(),
            "bandwidth": self.get_bandwidth(),
            "encap": self.get_encap()
        }

        return vport.copy()

    def __eq__(self, o: object) -> bool:
        return super().__eq__(o)

    def __str__(self) -> str:
        return super().__str__(self.serialize())

    def __hash__(self) -> int:
        return super().__hash__()


class VirtualLink(object):
    """
        vlink = {
            "type": "virtual_link"
            "link_id": string
            "tunnel": string
            "key": string
            "ingress": object
            "egress": objetc
        }

    """

    def __init__(self):
        self._type = "virtual_link"
        self._link_id = get_id()
        self._tunnel = None
        self._key = None
        self._ingress = None
        self._egress = None

    def get_type(self):
        return self._type

    def get_id(self):
        return self._link_id

    def get_tunnel(self):
        return self._tunnel

    def get_key(self):
        return self._key

    def get_ingress(self):
        return self._ingress

    def get_egress(self):
        return self._egress

    def set_tunnel(self, tunnel):
        self._tunnel = tunnel

    def set_key(self, key):
        self._key = key

    def set_ingress(self, device_id, portnum):
        self._ingress = {"device_id": device_id, "portnum":portnum}

    def set_egress(self, device_id, portnum):
        self._egress = {"device_id": device_id, "portnum":portnum}

    @classmethod
    def parser(cls, d):
        obj = cls()
        obj._link_id = d["link_id"]
        obj.set_tunnel(tunnel=d["tunnel"])
        obj.set_key(key=d["key"])

        ingress = d["ingress"]
        obj.set_ingress(ingress["device_id"], ingress["portnum"])

        egress = d["egress"]
        obj.set_egress(egress["device_id"], egress["portnum"])

        return obj

    def serialize(self):
        vlink = {
            "type": self.get_type(),
            "link_id": self.get_id(),
            "tunnel": self.get_tunnel(),
            "key": self.get_key(),
            "ingress": self.get_ingress(),
            "egress": self.get_egress()
        }
        return vlink.copy()

    def __eq__(self, o: object) -> bool:
        return super().__eq__(o)

    def __str__(self) -> str:
        return super().__str__(self.serialize())

    def __hash__(self) -> int:
        return super().__hash__()


class TransportSwitch(object):
    """
        tswitch = {
            "type": const ("transport_switch")
            "device_id": string,
            "datapath_id": string
            "prefix_uri": string
        }
    """

    def __init__(self):
        self._type = "transport"
        self._device_id = get_id()
        self._datapath_id = None
        self._prefix_uri = None

    def get_type(self):
        return self._type

    def get_id(self):
        return self._device_id

    def get_datapath_id(self):
        return self._datapath_id

    def get_prefix_uri(self):
        return self._prefix_uri

    def set_datapath_id(self, dpid):
        self._datapath_id = dpid

    def set_prefix_uri(self, prefix):
        self._prefix_uri = prefix

    @classmethod
    def parser(cls, d):
        obj = cls()

        obj._device_id = d["device_id"]
        obj.set_datapath_id(dpid=d["datapath_id"])
        obj.set_prefix_uri(prefix=d["prefix_uri"])

        return obj

    def serialize(self):
        tswitch = {
            "type": self.get_type(),
            "device_id": self.get_id(),
            "datapath_id": self.get_datapath_id(),
            "prefix_uri": self.get_prefix_uri(),
        }

        return tswitch.copy()

    def __hash__(self) -> int:
        return super().__hash__()

    def __eq__(self, o: object) -> bool:
        return super().__eq__(o)

    def __str__(self) -> str:
        return super().__str__(str(self.serialize()))


class TransportInterface(object):
    """
        tport = {
            "type": "transport"
            "interface_id": string,
            "device_id": string
            "portnum": string
            "encap": string
        }
    """

    def __init__(self):
        self._type = "transport"
        self._interface_id = get_id()
        self._device_id = None
        self._portnum = None
        self._encap = None

    def get_type(self):
        return self._type

    def get_id(self):
        return self._interface_id

    def get_portnum(self):
        return self._portnum

    def get_device_id(self):
        return self._device_id

    def get_encap(self):
        return self._encap

    def set_portnum(self, portnum):
        self._portnum = portnum

    def set_device_id(self, device_id):
        self._device_id = device_id

    def set_encap(self, encap="ethernet"):
        self._encap = encap

    @classmethod
    def parser(cls, d):
        obj = cls()
        obj._interface_id = d["id"]

        obj.set_device_id(device_id=d["device_id"])
        obj.set_encap(encap=d["encap"])
        obj.set_portnum(portnum=d["portnum"])

        return obj

    def serialize(self):

        tport = {
            "type": self.get_type(),
            "interface_id": self.get_id(),
            "device_id": self.get_device_id(),
            "portnum": self.get_portnum(),
            "encap": self.get_encap()
        }

        return tport.copy()

    def __hash__(self) -> int:
        return super().__hash__()

    def __eq__(self, o: object) -> bool:
        return super().__eq__(o)

    def __str__(self) -> str:
        return super().__str__(str(self.serialize()))


class TransportLink(object):
    """
        tlink = {
            "type": string (transport)
            "link_id": string,
            "tunnel": string,
            "key": string
            "ingress": {device_id: string, portnum: int}
            "egress": {device_id: string, portnum: int}
        }
    """

    @classmethod
    def parser(cls, d):
        obj = cls()
        obj._link_id = d["link_id"]

        ingress = d["ingress"]
        egress = d["egress"]

        obj.set_ingress(device_id=ingress["device_id"], portnum=ingress["portnum"])
        obj.set_egress(device_id=egress["device_id"], portnum=egress["portnum"])

        obj.set_key(key=d["key"])
        obj.set_tunnel(tunnel=d["tunnel"])

        return obj

    def __init__(self):
        self._type = "transport"
        self._link_id = get_id()
        self._tunnel = None
        self._key = None
        self._ingress = None
        self._egress = None

    def get_type(self):
        return self._type

    def get_id(self):
        return self._link_id

    def get_tunnel(self):
        return self._tunnel

    def get_key(self):
        return self._key

    def get_ingress(self):
        return self._ingress

    def get_egress(self):
        return self._egress

    def set_tunnel(self, tunnel):
        """tunnel can be vlan, vxlan, gre, geneve"""
        self._tunnel = tunnel

    def set_key(self, key):
        self._key = key

    def set_ingress(self, device_id, portnum):
        self._ingress = {"device_id": device_id, "portnum": portnum}

    def set_egress(self, device_id, portnum):
        self._egress = {"device_id": device_id, "portnum": portnum}

    def serialize(self):
        tlink = {
            "type": self.get_type(),
            "link_id": self.get_id(),
            "tunnel": self.get_tunnel(),
            "key": self.get_key(),
            "ingress": self.get_ingress(),
            "egress": self.get_egress()
        }

        return tlink.copy()

    def __str__(self) -> str:
        return super().__str__(str(self.serialize()))

    def __hash__(self) -> int:
        return super().__hash__()

    def __eq__(self, o: object) -> bool:
        return super().__eq__(o)


class NetworkSlice(object):
    """
        netslice = {
            "type": "virtual_network"
            "slice_id": string,
            "tenant_id": string,
            "revision": string,
            "label": string,
            "status": string,
            "controller": string,
        }
    """

    def __init__(self):
        self._type = "virtual_network"
        self._slice_id = get_id()
        self._tenant_id = None
        self._status = SliceStatus.CREATED.name
        self._revision = get_deploy_time()
        self._label = None
        self._controller = None

    def get_type(self):
        return self._type

    def get_id(self):
        return self._slice_id

    def get_tenant_id(self):
        return self._tenant_id

    def get_status(self):
        return self._status

    def get_label(self):
        return self._label

    def get_controller(self):
        return self._controller

    def get_revision(self):
        return self._revision

    def set_tenant_id(self, tenant_id):
        self._tenant_id = tenant_id

    def set_status(self, status):
        self._status = status

    def set_controller(self, controller):
        self._controller = controller

    def set_label(self, label):
        self._label = label

    def set_revision(self, revision):
        self._revision = revision

    @classmethod
    def parser(cls, d):
        obj = cls()
        obj._slice_id = d["slice_id"]
        obj.set_status(status=d["status"])
        obj.set_label(label=d["label"])
        obj.set_tenant_id(tenant_id=d["tenant_id"])
        obj.set_controller(controller=d["controller"])
        obj.set_revision(revision=d["revision"])

        return obj

    def serialize(self):

        netslice = {
            "type": self.get_type(),
            "slice_id": self.get_id(),
            "tenant_id": self.get_tenant_id(),
            "revision": self.get_revision(),
            "label": self.get_label(),
            "status": self.get_status(),
            "controller": self.get_controller(),
        }

        return netslice.copy()

    def __hash__(self) -> int:
        return super().__hash__()

    def __eq__(self, o: object) -> bool:
        return super().__eq__(o)

    def __str__(self) -> str:
        return super().__str__(str(self.serialize()))
