from autobahn.twisted.wamp import ApplicationSession
from autobahn import wamp

import time

from twisted.internet.defer import inlineCallbacks


PREFIX="vsdnorches.slicebuilder"

""""
slice_status = {
    "STOPPED": 0,
    "RUNNING": 1,
    "ERROR": 2,
    "DEPLOYING": 3
}
"""

class SliceInfo(object):
    def __init__(self, slice):
        self.__status = "DEPLOYING"
        self.__date = time.asctime(time.localtime(time.time()))
        self.__slice = slice

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = {

        }

    def get_status(self):
        return self.status

    def set_status(self, s):
        self.status = s

    def get_deploy_time(self):
        return self.date

    def get_slice_id(self):
        return self.slice.id

class SliceBuilder(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super(SliceManager, self).__init__(*args, **kwargs)
        self.__slices = {}

    @inlineCallbacks
    def onJoin(self, details):
        pass

