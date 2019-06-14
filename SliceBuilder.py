from autobahn.twisted.wamp import ApplicationSession
from autobahn import wamp
from SliceManager import NetworkSlice

import time

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


def _get_deploy_time():
    return time.asctime(time.localtime(time.time()))


class SliceInfo(object):
    def __init__(self, slice):
        self.status = 0
        self.date = _get_deploy_time()
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


class SliceBuilder(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super(SliceBuilder, self).__init__(*args, **kwargs)
        self.__slices = {}

    @inlineCallbacks
    def onJoin(self, details):
        pass

    @wamp.register(uri="{p}.get_status".format(p=PREFIX))
    def get_status(self, slice_id):
        ret = self.__slices.get(slice_id, None)

        if ret is None:
            return True, "slice was not found"
        return False, ret.status

    @wamp.register(uri="{p}.deploy".format(p=PREFIX))
    def deploy(self, slice):

        s = NetworkSlice.parser(slice)

        def register():
            sid = s.id
            info = SliceInfo(s)
            self.__slices.update({sid: info})
            self.log.info("new slice registed to deploy")

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
