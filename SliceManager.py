from uuid import uuid4 as rnd_id
from autobahn.twisted.wamp import ApplicationSession
from autobahn import wamp

from twisted.internet.defer import inlineCallbacks

PREFIX = "vsdnorches.slicemanager"


def serial_dict(d):
    for k, v in d.items():
        d.update({k: v.serialize()})
    return d


def serial_list(l: list):
    t = []
    for v in l:
        t.append(v.serialize())
    return t.copy()


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


class VirtualSwitch(object):
    """
        vswitch = {
            id: string,
            tenant: string,
            dpid: string,
            name: string,
            tswitch: string (dpid),
            protocols: list[string]
            vport: dict[{int: object}] (port_num: virtual_port)
         }

    """

    def __init__(self, tenant, name, tswitch, dpid=None, protocols=None):
        self.id = str(rnd_id())
        self.tenant = tenant
        self.name = name
        self.tswitch = tswitch
        self.dpid = dpid
        self.protocols = protocols
        self.__vports = {}

    def set_vport(self, vport):
        pn = vport["port_num"]
        self.__vports.update({pn: vport})

    def del_vport(self, vport_id):
        ret = self.exist_vport(vport_id)
        if ret is not None:
            del (self.__vports[vport_id])
        else:
            raise ValueError("the virtual port was not found")

    def get_vport(self, vport_id):
        ret = self.exist_vport(vport_id)
        if ret is not None:
            return ret
        else:
            raise ValueError("the virtual port was not found")

    def get_vports(self):
        return self.__vports.values()

    def exist_vport(self, vport_id):
        vports = self.__vports.values()
        for vport in vports:
            if vport.id == vport_id:
                return vport
        return None

    def __hash__(self) -> int:
        return super().__hash__()

    @classmethod
    def parser(cls, d):
        obj = cls(tenant=d["tenant"], name=d["name"], tswitch=d["tswitch"], dpid=d["dpid"],
                  protocols=d["protocols"])

        obj.id = d["id"]

        if len(d["vports"]) > 0:
            vports = d["vport"]
            for vport in vports:
                o = VirtualPort.parser(vport)
                obj.set_vport(vport=o)

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


class VirtualPort(object):
    """
        vport = {
            id: string,
            vport_num: int,
            tport_num: int,
            bandwidth: long,
            reserved: bool,
            type: string
            encap: string
        }

    """

    def __init__(self, vport_num, tport_num, reserved=False, bandwidth=None, type="vlan", encap="eth"):
        self.id = str(rnd_id())
        self.vport_num = vport_num
        self.tport_num = tport_num
        self.reserved = reserved
        self.bandwidth = bandwidth
        self.type = type
        self.encap = encap

    @classmethod
    def parser(cls, d):
        obj = cls(d["vport_num"], d["tport_num"], d["reserved"], d["bandwidth"], d["type"], d["encap"])
        obj.id = d["id"]

        return obj

    def serialize(self):
        vport = dict()
        vport["id"] = self.id
        vport["vport_num"] = self.vport_num
        vport["tport_num"] = self.tport_num
        vport["reserved"] = self.reserved
        vport["bandwidth"] = self.bandwidth
        vport["type"] = self.type
        vport["encap"] = self.encap

        return vport.copy()


class VirtualLink(object):
    """
        vlink = {
            id: string
            ingress_port: string
            egress_port: string
            encap: string
            key: string (vlan id, vxlan_id)
        }

    """

    def __init__(self, ingress_port, egress_port, key):
        self.id = str(rnd_id())
        self.ingress_port = ingress_port
        self.egress_port = egress_port
        self.key = key

    @classmethod
    def parser(cls, d):
        obj = cls(d["ingress_port"], d["egress_port"], d["key"])
        obj.id = d["id"]

        return obj

    def serialize(self):
        vlink = dict()
        vlink["id"] = self.id
        vlink["ingress_port"] = self.ingress_port
        vlink["egress_port"] = self.egress_port
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
        self.id = str(rnd_id())
        self.dpid = dpid
        self.prefix = prefix
        self.tports = dict()

    @classmethod
    def parser(cls, d):
        obj = cls(d["dpid"], d["prefix"])
        obj.id = d["id"]

        tports = d["tports"]
        if len(tports) > 0:
            for tport in tports:
                o = TransportLinks.parser(tport)
                obj.set_tport(tport=o)

        return obj

    def serialize(self):
        tswitch = dict()
        tswitch["id"] = self.id
        tswitch["dpid"] = self.dpid
        tswitch["prefix"] = self.prefix
        tswitch["tports"] = serial_dict(self.tports)

        return tswitch.copy()

    def set_tport(self, tport):
        port_num = tport.port_num
        self.tports.update({port_num: tport})

    def del_tport(self, tport_id):

        ret = self.exist_tport(tport_id)

        if ret is not None:
            del (self.tports[ret.id])
        else:
            raise ValueError("the transport port was not found")

    def get_tlinks(self):
        return self.tports.values()

    def exist_tport(self, tport_id):
        tports = self.tports.values()

        for tport in tports:
            if tport.id == tport_id:
                return tport
        return None


class TransportPort(object):
    """
        tport = {
            id: string,
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


class TransportLinks(object):
    """
        tlink = {
            id: string,
            ingress_port: int,
            egrees_port: int
            ingress_id: string (dpid)
            egress_id: string (dpid)
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


class SliceManager(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super(SliceManager, self).__init__(*args, **kwargs)
        self.__networkslices = {}
        self.log.info("Starting Slice Manager...")

    @inlineCallbacks
    def _rem_slice_deployed(self, slice_id):
        mod_rem = "vsdnorches.slicebuilder.remove"
        error, ret = yield self.call(mod_rem, slice_id)
        if error:
            raise ValueError(ret)
        del (self.__networkslices[slice_id])

    def _rem_slice_created(self, slice_id):
        del (self.__networkslices[slice_id])

    @inlineCallbacks
    def get_slice_status(self, slice_id):
        module_status = "vsdnorches.slicebuilder.get_status"
        error, ret = yield self.call(module_status, slice_id)
        if error:
            self.log.error(ret)
            return None
        return ret

    @inlineCallbacks
    def onJoin(self, details):
        resp = yield self.call("wamp.session.list")
        print(resp)

    @wamp.register(uri="{p}.create".format(p=PREFIX))
    def create(self, slice):
        s = NetworkSlice.parser(slice)

        ret = self.get_slice_status(s.id)
        if ret is None:
            self.__networkslices.update({s.id: slice})
            return s.id
        else:
            self.log.info("the slice has been deployed")

    @wamp.register(uri="{p}.delete".format(p=PREFIX))
    def delete(self, slice_id):
        try:
            ret = self.get_slice_status(slice_id)
            if ret is None:
                self._rem_slice_created(slice_id)
                self.log.info("the slice {id} was deleted".format(id=slice_id))
                return False, None
            elif ret.__eq__("STOPPED"):
                self._rem_slice_deployed(slice_id)
                self.log.info("the slice {id} was deleted and undeployed".format(id=slice_id))
                return False, None
            elif ret.__eq__("DEPLOYING"):
                msg = "Cannot delete slice in deploying"
                self.log.error(msg)
                return True, msg
            elif ret.__eq__("RUNNING"):
                msg = "Cannot delete slice in running"
                self.log.error(msg)
                return True, msg
            elif ret.__eq__("ERROR"):
                self._rem_slice_created(slice_id)
                return False, None
            else:
                msg = "cannot delete slice"
                self.log.info(msg)
                return True, msg

        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri="{p}.add_vswitch".format(p=PREFIX))
    def add_vswitch(self, slice_id, vswitch):
        vsw = VirtualSwitch.parser(vswitch)
        slice = self.__networkslices.get(slice_id)

        ret = self.get_slice_status(slice_id)
        if ret is None:
            slice.add_vswitch(vsw)
            self.__networkslices.update({slice_id: slice})
            self.log.info()
            return False, None
        else:
            msg = "Cannot add a virtual switch in slice already has deployed"
            self.log.error(msg)
            return True, msg

    @wamp.register(uri="{p}.rem_vswitch".format(p=PREFIX))
    def rem_vswitch(self, slice_id, vswitch_id):
        slice = self.__networkslices.get(slice_id)
        vsw = slice.get_vswitch(vswitch_id)

        ret = self.get_slice_status(slice_id)
        if ret is None:
            slice.rem_vswitch(vsw.dpid)
            self.__networkslices.update({slice_id: slice})
            self.log.info()
            return False, None
        else:
            msg = "Cannot remove a virtual switch in slice already has deployed"
            self.log.error(msg)
            return True, msg

    @wamp.register(uri="{p}.add_vport".format(p=PREFIX))
    def add_vport(self, slice_id, vswitch_id, vport):
        slice = self.__networkslices.get(slice_id)
        vsw = slice.get_vswitch(vswitch_id)
        vp = VirtualPort.parser(vport)

        ret = self.get_slice_status(slice_id)

        if ret is None:
            vsw.set_vport(vp)
            slice.add_vswitch(vsw)
            self.__networkslices.update({slice_id: slice})
            self.log.info()
            return False, None
        else:
            msg = "Cannot add a virtual port in slice already has deployed"
            self.log.error(msg)
            return True, msg

    @wamp.register(uri="{p}.rem_vport".format(p=PREFIX))
    def rem_vport(self, slice_id, vswitch_id, vport_id):
        slice = self.__networkslices.get(slice_id)
        vsw = slice.get_vswitch(vswitch_id)

        ret = self.get_slice_status(slice_id)
        if ret is None:
            vsw.del_vport(vport_id)
            slice.add_vswitch(vsw)
            self.__networkslices.update({slice_id: slice})

        else:
            msg = "Cannot remove a virtual port in slice already has deployed"
            self.log.error(msg)
            return True, msg

    @wamp.register(uri="{p}.start_slice".format(p=PREFIX))
    def start_slice(self):
        pass

    @wamp.register(uri="{p}.stop_slice".format(p=PREFIX))
    def stop_slice(self):
        pass
