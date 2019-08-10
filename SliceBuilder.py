from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession
from twisted.internet.defer import inlineCallbacks


class SliceBuilderService(ApplicationSession):

    def __init__(self, config=None):
        super().__init__(config=config)
        self._slices_registred = {}

    @inlineCallbacks
    def onJoin(self, details):
        self.log.info('Slice Builder Service Starting ...')
        yield self.register(self)
        self.log.info('Slice Builder Service Started ...')

    @inlineCallbacks
    def update_status(self, i, s):
        app = "sliceservice.update_slice_status"
        err, msg = yield self.call(app, slice_id=i, code=s)
        if err:
            raise ValueError(msg)

    @inlineCallbacks
    def deploy_node(self, n):
        lbl = n['id'][:8]
        dpid = n['datapath_id']
        prtl = n['protocols']
        dev = n['device_id']

        app = "topologyservice.get_node"
        err, gn = yield self.call(app, dev)
        if err:
            raise ValueError(gn)
        _, sw = gn

        uri = "{u}.add_instance".format(u=sw["prefix_uri"])
        print(uri)
        err, ret = yield self.call(uri, label=lbl, datapath_id=dpid, protocols=prtl)
        if err:
            raise ValueError(ret)

    @wamp.register(uri='slicebuilderservice.deploy')
    def deploy(self, slice):

        def register_slice(i, s):
            self._slices_registred.update({i: s})

        nodes = slice['nodes']
        links = slice['links']
        slice_id = slice['graph']['slice_id']

        if len(nodes) == 0:
            self.log.info("No nodes to deploy")
            return False, None

        try:
            self.update_status(slice_id, 2)
            for n in nodes:
                self.deploy_node(n)
            register_slice(slice_id, slice)
            self.update_status(slice_id, 6)
            self.log.info("the slice <{i}> was deployed".format(i=slice_id))
            return False, None
        except Exception as ex:
            return True, str(ex)

    @wamp.register(uri='slicebuilderservice.start')
    def start(self):
        pass

    @wamp.register(uri='slicebuilderservice.stop')
    def stop(self):
        pass

    @wamp.register(uri='slicebuilderservice.remove')
    def remove(self):
        pass
