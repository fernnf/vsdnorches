from autobahn.twisted.wamp import ApplicationSession
from autobahn import wamp
from SliceManager import NetworkSlice, VirtualLink, VirtualSwitch

from SliceModels import SliceInfo

from twisted.internet.defer import inlineCallbacks


PREFIX = "vsdnorches.slicebuilder"


"""
slice_status = {
    "STOPPED": 0,
    "RUNNING": 1,
    "ERROR": 2,
    "DEPLOYING": 3
}
"""






class SliceBuilder(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super(SliceBuilder, self).__init__(*args, **kwargs)
        self.__slices = {}
        self.log.info("Starting Slice Builer...")

    def onJoin(self, details):
        pass

    def register_vswitch(self, vswitches):



    @wamp.register(uri="{p}.get_status".format(p=PREFIX))
    def get_status(self, slice_id):
        ret = self.__slices.get(slice_id, None)

        if ret is None:
            return True, "slice was not found"
        return False, ret.status

    @wamp.register(uri="{p}.deploy".format(p=PREFIX))
    def deploy(self, slice):

        ns = NetworkSlice.parser(slice)
        si = SliceInfo(ns)

        def register():
            id = si.slice_id
            self.__slices.update({id: si})
            self.log.info("new slice registered to deploy")

        def deploy_vswitches():
            pass

        def deploy_links():
            pass

        def send_notification():
            pass

        def deploy():
            pass

        try:
            register()
            deploy()
            send_notification()
        except Exception as ex:
            pass

    @wamp.register(uri="{p}.stop".format(p=PREFIX))
    def stop(self, slice_id):
        info = self.__slices.get(slice_id, None)

        if info is None:
            return None, "slice was not found"

        slice = info.slice

        pass

    @wamp.register(uri="{p}.remove".format(p=PREFIX))
    def remove(self, slice_id):
        pass
