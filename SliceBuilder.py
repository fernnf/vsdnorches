from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession
from twisted.internet.defer import inlineCallbacks


class SliceBuilderService(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super(SliceBuilderService, self).__init__(*args, **kwargs)

    @inlineCallbacks
    def onJoin(self, details):
        self.log.info('Slice Builder Service Starting ...')
        yield self.register(self)
        self.log.info('Slice Builder Service Started ...')

    @wamp.register(uri = 'slicebuilderservice.deploy')
    def deploy(self):
        pass

    @wamp.register(uri = 'slicebuilderservice.start')
    def start(self):
        pass

    @wamp.register(uri = 'slicebuilderservice.stop')
    def stop(self):
        pass

    @wamp.register(uri = 'slicebuilderservice.remove')
    def remove(self):
        pass
