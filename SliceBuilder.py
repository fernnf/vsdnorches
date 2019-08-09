from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession
from twisted.internet.defer import inlineCallbacks

class SliceBuilderService(ApplicationSession):

    def __init__(self, config=None):
        super().__init__(config=config)
        self._slices_registred = {}

    @inlineCallbacks
    def _update_status(self, slice_id, code):
        err, msg = yield self.call("sliceservice.update_slice_status", slice_id=slice_id, code=code)
        if err:
            self.log.error(msg)

    def _slice_register(self, slice):
        slice_id = slice['graph']['slice_id']
        self._slices_registred.update({slice_id: slice})

    @inlineCallbacks
    def _instance_register(self, device_id, virtdev_id):
        err, ret = yield self.call("topologyservice.set_instance", device_id, virtdev_id)
        if err:
            raise ValueError(ret)

    @inlineCallbacks
    def _node_register(self, node):
        def get_device(id):
            err, data = yield self.call("topologyservice.get_node", id)
            if err:
                raise ValueError(data)
            return data

        def add_instance(a, l, d, p):
            err, data = yield self.call(a, label = l, datapath_id = d, protocols = p)
            if err:
                raise ValueError(data)
            return data

        device_id, device = get_device(node['device_id'])
        app = "{p}.add_instance".format(p = device['prefix_uri'])

        label = node['id'][:8]
        protocols = node['protocols']
        datapath_id = node['datapath_id']

        add_instance(app, label, datapath_id, protocols)
        self._instance_register(device_id, node['id'])

    @inlineCallbacks
    def onJoin(self, details):
        self.log.info('Slice Builder Service Starting ...')
        yield self.register(self)
        self.log.info('Slice Builder Service Started ...')

    @wamp.register(uri='slicebuilderservice.deploy')
    def deploy(self, slice):

        nodes = slice['nodes']
        slice_id = slice['graph']['slice_id']

        if len(nodes) == 0:
            self.log.info("No nodes to deploy")
            return False, None
        try:
            self._update_status(slice_id, 2)
            for n in nodes:
                self._node_register(n)
            self._slice_register(slice)
            self.log.info("the slice <{i}> was deployed".format(i=slice_id))
            self._update_status(slice_id, 6)
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
