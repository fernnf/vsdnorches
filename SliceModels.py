import time
from uuid import uuid4 as rnd_id


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

class VirtualPort(object):
    """
        vport = {
            id: string,
            vswitch: string (vswitch_id),
            vport_num: int,
            tport_num: int,
            bandwidth: long,
            reserved: bool,
            encap: string
        }

    """

    def __init__(self, vswitch, vport_num, tport_num, reserved=False, bandwidth=None, encap="eth"):
        self.__id = get_id()
        self.vswitch = vswitch
        self.vport_num = vport_num
        self.tport_num = tport_num
        self.reserved = reserved
        self.bandwidth = bandwidth
        self.encap = encap

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        pass

    @property
    def vswitch(self):
        return self.__vsw

    @vswitch.setter
    def vswitch(self, value):
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
        vport = dict()
        vport["id"] = self.id
        vport["vswitch"] = self.vswitch
        vport["vport_num"] = self.vport_num
        vport["tport_num"] = self.tport_num
        vport["reserved"] = self.reserved
        vport["bandwidth"] = self.bandwidth
        vport["encap"] = self.encap

        return vport.copy()


class VirtualSwitch(object):
    """
        vswitch = {
            id: string,
            tenant: string,
            dpid: string,
            name: string,
            tswitch: string (id),
            protocols: list[string]
            ports: Dict[PortNum: VirtualPort]
         }

    """

    def __init__(self, tenant, name, tswitch, dpid=None, protocols=None):
        self.__id = get_id(dpid=dpid)
        self.tenant = tenant
        self.name = name
        self.tswitch = tswitch
        self.protocols = protocols
        self.__vports = {}

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        pass

    @property
    def dpid(self):
        return self.__dpid

    @dpid.setter
    def dpid(self, value):
        if value is None:
            self.__dpid = self.id[:16]
        else:
            assert len(value) == 16, "dpid must have 16 digits hex decimal"
            self.__dpid = value

    @property
    def tenant(self):
        return self.__tenant

    @tenant.setter
    def tenant(self, value):
        self.__tenant = value

    @property
    def tswitch(self):
        return self.__tsw

    @tswitch.setter
    def tswitch(self, value):
        self.__tsw = value

    @property
    def protocols(self):
        return self.__proto

    @protocols.setter
    def protocols(self, value):
        self.__proto = value

    def set_vports(self, vport):
        vport.vswitch = self.id
        port_num = vport.vport_num
        self.__vports.update({port_num: vport})

    def get_vport(self, port_num):
        return self.__vports.get(port_num, None)

    def get_vports(self):
        return self.__vports

    def __hash__(self) -> int:
        return super().__hash__()

    @classmethod
    def parser(cls, d):
        obj = cls(tenant=d["tenant"],
                  name=d["name"],
                  tswitch=d["tswitch"],
                  dpid=d["dpid"],
                  protocols=d["protocols"])

        obj.__id = d["id"]

        if len(d["vports"]) > 0:
            vports = dict(d["vports"])
            obj.__vports = vports

        return obj

    def serialize(self):
        vswitch = dict()
        vswitch["id"] = self.id
        vswitch["tenant"] = self.tenant
        vswitch["name"] = self.name
        vswitch["tswitch"] = self.tswitch
        vswitch["dpid"] = self.dpid
        vswitch["protocols"] = self.protocols
        vswitch["vports"] = serial_dict(self.__vports)

        return vswitch.copy()




class VirtualLink(object):
    """
        vlink = {
            id: string
            start_node: string (vswitch id)
            stop_node: string (vswitch id)
            ingress_port: int (port_num)
            egress_port: int (port_num)
            type: string (vlan, vxlan)
            key: string (vlan id, vxlan_id)
        }

    """

    def __init__(self, start_node, stop_node, ingress_port, egress_port, type, key):
        self.__id = get_id()
        self.start_node = start_node
        self.stop_node = stop_node
        self.ingress_port = ingress_port
        self.egress_port = egress_port
        self.type = type
        self.key = key

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        pass

    @property
    def start_node(self):
        return self.__sn

    @start_node.setter
    def start_node(self, value):
        self.__sn = value

    @property
    def stop_node(self):
        return self.__stn

    @stop_node.setter
    def stop_node(self, value):
        self.__stn = value

    @property
    def ingress_port(self):
        return self.__ip

    @ingress_port.setter
    def ingress_port(self, value):
        self.__ip = value

    @property
    def egress_port(self):
        return self.__ep

    @egress_port.setter
    def egress_port(self, value):
        self.__ep = value

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = value

    @property
    def key(self):
        return self.__key

    @key.setter
    def key(self, value):
        self.__key = value

    @classmethod
    def parser(cls, d):
        obj = cls(start_node = d["start_node"],
                  stop_node = d["stop_node"],
                  ingress_port=d["ingress_port"],
                  egress_port=d["egress_port"],
                  type=d["type"],
                  key=d["key"])
        obj.__id = d["id"]

        return obj

    def serialize(self):
        vlink = dict()
        vlink["id"] = self.id
        vlink["start_node"] = self.start_node
        vlink["stop_node"] = self.stop_node
        vlink["ingress_port"] = self.ingress_port
        vlink["egress_port"] = self.egress_port
        vlink["type"] = self.type
        vlink["key"] = self.key

        return vlink.copy()


class TransportSwitch(object):
    """
        tswitch = {
            id: string,
            dpid: string,
            prefix: string,
            tports: list
        }
    """

    def __init__(self, dpid, prefix):
        self.__id = get_id(dpid = dpid)
        self.dpid = dpid
        self.prefix = prefix
        self.__tports = {}

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        pass

    @property
    def dpid(self):
        return self.__dpid

    @dpid.setter
    def dpid(self, value):
        if value is None:
            self.__dpid = self.id[:16]
        else:
            assert len(value) == 16, "dpid must have 16 digits hex decimal"
            self.__dpid = value

    @property
    def prefix_node(self):
        return self.__pn

    @prefix_node.setter
    def prefix_node(self, value):
        self.__pn = value

    @classmethod
    def parser(cls, d):
        obj = cls(d["dpid"],
                  d["prefix"])

        obj.__id = d["id"]

        tports = dict(d["tports"])
        if len(tports) > 0:
            obj.__tports = tports

        return obj

    def set_tports(self, tport):
        tport.tswitch = self.id
        port_num =  tport.port_num
        self.__tports.update({port_num: tport})

    def get_vport(self, port_num):
        return self.__tports.get(port_num, None)

    def get_vports(self):
        return self.__tports.values()

    def del_vport(self, port_num):
        vport = self.get_vport(port_num)
        if vport is None:
            raise ValueError("virtual port not found")

        self.__tports.pop(port_num)

    def serialize(self):
        tswitch = dict()
        tswitch["id"] = self.id
        tswitch["dpid"] = self.dpid
        tswitch["prefix"] = self.prefix
        tswitch["tports"] = serial_dict(self.__tports)

        return tswitch.copy()



class TransportLinks(object):
    """
        tlink = {
            id: string,
            start_node: string (id),
            stop_node: string (id),
            ingress_port: int (port_num)
            egress_port: int (port_num)
        }
    """

    @classmethod
    def parser(cls, d):
        obj = cls(d["ingress_port"], d["egress_port"], d["ingress_id"], d["egress_id"])
        obj.id = d["id"]
        return obj

    def __init__(self, ingress_port, egress_port, tswitch_id, peer_id):
        self.id = str(rnd_id())
        self.ingress_port = ingress_port
        self.egress_port = egress_port
        self.ingress_id = tswitch_id
        self.egress_id = peer_id

    def serialize(self):
        tlink = dict()
        tlink["id"] = self.id
        tlink["ingress_port"] = self.ingress_port
        tlink["egress_port"] = self.egress_port
        tlink["ingress_id"] = self.ingress_id
        tlink["egress_id"] = self.egress_id
        return tlink.copy()


class TransportPort(object):
    """
        tport = {
            id: string,
            tswitch: string
            port_num: int
            encap: string
        }
    """

    def __init__(self, port_num, encap="eth"):
        self.id = str(rnd_id())
        self.port_num = port_num
        self.encap = encap

    @classmethod
    def parser(cls, d):
        obj = cls(d["port_num"], d["encap"])
        obj.id = d["id"]

    def serialize(self):
        tport = dict()
        tport["port_num"] = self.port_num
        tport["encap"] = self.encap
        return tport.copy()

    def __hash__(self) -> int:
        return super().__hash__()


class NetworkSlice(object):
    """
        netslice = {
            id: string,
            status: String
            tenant: int
            controller: string
            vswitches: list[string]
            vlinks: list[string]
        }
    """

    status_slice = {
        0: "CREATED",
        1: "DEPLOYED",
        2: "RUNNING",
        3: "ERROR",
        4: "STOP"
    }

    @classmethod
    def parser(cls, d: dict):
        obj = cls(tenant=d["tenant"], controller=d["controller"])
        obj.id = d["id"]

        if len(d["vswitches"]) > 0:

            vswitches = d["vswitches"]
            for vswitch in vswitches:
                o = VirtualSwitch.parser(vswitch)
                obj.add_vswitch(vswitch=o)

        if len(d["vlinks"]) > 0:
            vlinks = d["vlinks"]
            for vlink in vlinks:
                o = VirtualLink.parser(vlink)
                obj.add_vlink(vlink=o)

        return cls

    def __init__(self, tenant, controller):
        self.id = str(rnd_id())
        self.status = self.status_slice.get(0)
        self.tenant = tenant
        self.controller = controller
        self.__vswitches = {}
        self.__vlinks = []

    def add_vswitch(self, vswitch):
        dpid = vswitch["dpid"]
        self.__vswitches.update({dpid: vswitch})

    def rem_vswitch(self, dpid):
        if self.exist_vswitch(dpid):
            del (self.__vswitches[dpid])
        else:
            raise ValueError("the virtual switch was not found")

    def add_vlink(self, vlink):
        self.__vlinks.append(vlink)

    def rem_vlink(self, vlink_id):
        ret = self.exist_vlink(vlink_id)
        if ret is not None:
            self.__vlinks.remove(ret)
        else:
            raise ValueError("the virtual link was not found")

    def get_vswitches(self):
        return self.__vswitches.keys()

    def get_vswitch(self, dpid):
        return self.__vswitches.get(dpid)

    def get_links(self):
        return self.__vlinks.copy()

    def exist_vswitch(self, dpid):
        ret = self.__vswitches.get(dpid, None)

        if ret is None:
            return False
        return True

    def exist_vlink(self, vlink_id):
        for vlink in self.__vlinks:
            if vlink.id == vlink_id:
                return vlink
        return None

    def serialize(self):
        netslice = dict()
        netslice["id"] = self.id
        netslice["status"] = self.status
        netslice["tenant"] = self.tenant
        netslice["vswitches"] = serial_dict(self.__vswitches)
        netslice["vlinks"] = serial_list(self.__vlinks)

        return netslice.copy()

    def set_status(self, status):
        s = self.status_slice.get(status, None)
        if s is None:
            raise ValueError("The status value is not valid")

        self.status = s

    def get_status(self):
        return self.status

    def __hash__(self) -> int:
        return super().__hash__()


class SliceInfo(object):
    def __init__(self, slice):
        self.status = 0
        self.date = get_deploy_time()
        self.slice = slice

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = {
            0: "DEPLOYING",
            1: "RUNNING",
            2: "STOPPED",
            3: "ERROR"
        }.get(value, None)

    @property
    def deploy_time(self):
        return self.__date

    @deploy_time.setter
    def deploy_time(self, value):
        self.__date = value

    @property
    def slice(self):
        return self.__slice

    @slice.setter
    def slice(self, value):
        self.__slice = value

    @property
    def slice_id(self):
        return self.slice.id

    @slice_id.setter
    def slice_id(self, value):
        pass

    def serialize(self):
        info = dict()
        info["status"] = self.status
        info["deploy_time"] = self.deploy_time
        info["slice"] = self.slice.serialized()

        return info.copy()
