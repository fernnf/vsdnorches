from uuid import uuid4 as rnd_id
from autobahn.twisted.wamp import ApplicationSession
from autobahn import wamp

from twisted.internet.defer import inlineCallbacks

from datetime import date, time, datetime

PREFIX = "vsdnorches.slicemanager"


class NetworkSlice(object):
    """
        netslice = {
            id: string,
            tenant: int
            controller: string
            vswitches: list[string]
            vlinks: list[string]
        }
    """

    @classmethod
    def from_dict(cls, d):
        obj = cls(tenant=d["tenant"], controller=d["controller"])
        obj.id = d["id"]
        for vswitch in d["vswitches"]:
            obj.add_vswitch(vswitch)
        for vlink in d["vlinks"]:
            obj.add_vlink(vlink)

        return cls

    def __init__(self, tenant, controller):
        self.id = str(rnd_id())
        self.tenant = tenant
        self.controller = controller
        self.__vswitch = []
        self.__vlink = []

    def add_vswitch(self, vswitch_id):
        self.__vswitch.append(vswitch_id)

    def rem_vswitch(self, vswitch_id):
        self.__vswitch.remove(vswitch_id)

    def add_vlink(self, vlink):
        pass

    def rem_vlink(self, vlink_id):
        pass

    def get_vswitchs(self):
        return self.__vswitch.copy()

    def get_links(self):
        return self.__vlink.copy()

    def __dict__(self):
        netslice = dict()
        netslice["id"] = self.id
        netslice["tenant"] = self.tenant
        netslice["vswitch"] = self.__vswitch.copy()
        netslice["vlink"] = self.__vlink.copy()
        return netslice.copy()


class VirtualSwitch(object):
    """
        vswitch = {
            id: string,
            tenant: string,
            dpid: string,
            name: string,
            tswitch: string,
            protocols: list[string]
            vport: dict[{int: string}] (port_num: vport_id)
         }

    """

    def __init__(self, tenant, name, tswitch, dpid=None, protocols=None):
        self.id = str(rnd_id())
        self.tenant = tenant
        self.name = name
        self.tswitch = tswitch
        self.dpid = dpid
        self.protocols = protocols

    def __dict__(self):
        vswitch = dict()
        vswitch["id"] = self.id
        vswitch["tenant"] = self.tenant
        vswitch["name"] = self.name
        vswitch["tswitch"] = self.tswitch
        vswitch["dpid"] = self.dpid
        vswitch["protocols"] = self.protocols
        return vswitch.copy()


class VirtualPort(object):
    """
        vport = {
            id: string,
            port_num: int,
            real_port_num: int,
            bandwidth: long,
            reserved: bool,
            vswitch: string,
            type: string
            encap: string
        }

    """

    def __init__(self, port_num, real_port_num, vswitch, reserved=False, bandwidth=None, type="vlan", encap="eth"):
        self.id = str(rnd_id())
        self.port_num = port_num
        self.real_port_num = real_port_num
        self.vswitch = vswitch
        self.reserved = reserved
        self.bandwidth = bandwidth
        self.type = type
        self.encap = encap

    def __dict__(self):
        vport = dict()
        vport["id"] = self.id
        vport["port_num"] = self.port_num
        vport["real_port_num"] = self.real_port_num
        vport["vswitch"] = self.vswitch
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
            statistic: dict
        }

    """

    def __init__(self, ingress_port, egress_port, encap):
        self.id = str(rnd_id())
        self.ingress_port = ingress_port
        self.egress_port = egress_port
        self.encap = encap
        self.__statis = {}

    def set_statistics(self, st):
        self.__statis.update({str(datetime.now()): st})

    def __dict__(self):
        vlink = dict()
        vlink["id"] = self.id
        vlink["ingress_port"] = self.ingress_port
        vlink["egress_port"] = self.egress_port
        vlink["encap"] = self.encap

        return vlink.copy()


class TransportSwitch(object):
    """
        tswitch = {
            id: string,
            dpid: string,
            prefix: string,
            links: list
        }
    """

    def __init__(self, dpid, prefix=None):
        self.dpid = dpid
        self.prefix = prefix
        self.links = (prefix if prefix is not None else dict().copy())

    def __dict__(self):
        tswitch = dict()
        tswitch["dpid"] = self.dpid
        tswitch["prefix"] = self.prefix
        tswitch["links"] = self.links.copy()

        return tswitch.copy()

    def set_link(self, link):
        self.links.update({link["id"]: link})

    def del_link(self, link_id):
        del (self.links[link_id])

    def get_links(self):
        return self.links.keys()


class TransportLinks(object):
    """
        tlink = {
            id: string,
            ingress_port: int,
            egrees_port: int
            trans_switch: string
            peer_switch: string
            statistics: dict
        }
    """

    def __init__(self, ingress_port, egress_port, trans_switch, peer_switch):
        self.id = str(rnd_id())
        self.ingress_port = ingress_port
        self.egress_port = egress_port
        self.trans_switch = trans_switch
        self.peer_switch = peer_switch
        self.statistic = {}

    def __dict__(self):
        tlink = dict()
        tlink["id"] = self.id
        tlink["ingress_port"] = self.ingress_port
        tlink["egrees_port"] = self.egress_port
        tlink["trans_switch"] = self.trans_switch
        tlink["peer_switch"] = self.peer_switch
        tlink["statistic"] = self.statistic

        return tlink.copy()


class SliceManager(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super(SliceManager, self).__init__(*args, **kwargs)
        self.__networkslices = {}
        self.__virtualswitch = {}
        self.__virtualport = {}
        self.__vrituallink = {}
        self.__transport_switch = {}
    @inlineCallbacks
    def onJoin(self, details):
        resp = yield self.call("wamp.session.list")
        print(resp)

    @wamp.register(uri="{p}.create_slice".format(p=PREFIX))
    def create_slice(self, tenant, controller):
        slice = NetworkSlice(tenant, controller)
        self.__networkslices.update({tenant: slice})

    @wamp.register(uri="{p}.delete_slice".format(p=PREFIX))
    def delete_slice(self):
        pass

    @wamp.register(uri="{p}.add_vswitch".format(p=PREFIX))
    def add_vswitch(self):
        pass

    @wamp.register(uri="{p}.rem_vswitch".format(p=PREFIX))
    def rem_vswitch(self):
        pass

    @wamp.register(uri="{p}.add_vport".format(p=PREFIX))
    def add_vport(self):
        pass

    @wamp.register(uri="{p}.rem_vport".format(p=PREFIX))
    def rem_vport(self):
        pass

    @wamp.register(uri="{p}.start_slice".format(p=PREFIX))
    def start_slice(self):
        pass

    @wamp.register(uri="{p}.stop_slice".format(p=PREFIX))
    def stop_slice(self):
        pass
