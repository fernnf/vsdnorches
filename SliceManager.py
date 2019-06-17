from uuid import uuid4 as rnd_id
from autobahn.twisted.wamp import ApplicationSession
from autobahn import wamp

from SliceModels import NetworkSlice
from SliceModels import VirtualPort, VirtualLink, VirtualSwitch
from SliceModels import TransportSwitch, TransportPort, TransportLinks

from twisted.internet.defer import inlineCallbacks

PREFIX = "vsdnorches.slicemanager"


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
            self.log.info("new slice {i} has created ".format(i=s.id))
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
            self.log.info("new virtual switch {i} has created".format(i=vsw.id))
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
            self.log.info("the virtual switch {i} has removed".format(i=vsw.id))
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
            return False, None
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
