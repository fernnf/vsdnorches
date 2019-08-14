import json
from autobahn.wamp.exception import ApplicationError
from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession
from twisted.internet.defer import inlineCallbacks, returnValue


class SliceBuilderService(ApplicationSession):

    def __init__(self, config=None):
        super().__init__(config=config)
        self._slices_registred = {}

    @inlineCallbacks
    def _send_call(self, uri, *args, **kwargs):
        ret = yield self.call(uri, *args, **kwargs)
        if ret['error']:
            raise ValueError(ret['result'])
        returnValue(json.loads(ret))

    @inlineCallbacks
    def _add_vnode(self, prefix, label, datapath_id, protocols):
        uri = "{p}.add_instance".format(p=prefix)
        yield self._send_call(uri, label=label, datapath_id=datapath_id, protocols=protocols)

    @inlineCallbacks
    def _rem_vnode(self, prefix, label):
        uri = "{p}.rem_instance".format(p=prefix)
        yield self._send_call(uri, label=label)

    @inlineCallbacks
    def _add_vport(self, prefix, label, portnum, realport, vlan_id):
        uri = "{p}.add_vport".format(p=prefix)
        yield self._send_call(uri, label=label, portnum=portnum, realport=realport, vlan_id=vlan_id)

    @inlineCallbacks
    def _rem_vport(self, prefix, portnum):
        uri = "{p}.rem_vport".format(p=prefix)
        yield self._send_call(uri, portnum=portnum)

    @inlineCallbacks
    def _add_bypass(self, prefix, in_realport, out_realport, vlan_id):
        uri = "{p}.add_by_pass".format(p=prefix)
        yield self._send_call(uri, in_realport=in_realport, out_realport=out_realport, vlan_id=vlan_id)

    @inlineCallbacks
    def _rem_bypass(self, prefix, in_realport, out_realport, vlan_id):
        uri = "{p}.rem_by_pass".format(p=prefix)
        yield self._send_call(uri, in_realport=in_realport, out_realport=out_realport, vlan_id=vlan_id)

    @inlineCallbacks
    def _set_controller(self, prefix, label, controller):
        uri = "{p}.set_controller".format(p=prefix)
        yield self._send_call(uri, label=label, controller=controller)

    @inlineCallbacks
    def _del_controller(self, prefix, label):
        uri = "{p}.del_controller".format(p=prefix)
        yield self._send_call(uri, label=label)

    @inlineCallbacks
    def _update_slice_status(self, slice_id, status):
        uri = "sliceservice.update_slice_status"
        try:
            yield self.call(uri, slice_id=slice_id, code=status)
        except ApplicationError as ex:
            self.log.error("Error:{}".format(ex.error))


    @inlineCallbacks
    def _get_prefix_node(self, device_id):
        uri = "topologyservice.get_node"
        err, phy_node = yield self.call(uri, device_id=device_id)
        if err:
            raise ValueError(phy_node)
        p = phy_node[1]['prefix_uri']
        returnValue(p)

    def _get_label(self, vid):
        return vid[:8]

    @inlineCallbacks
    def _deploy_node(self, n):

        label = self._get_label(n['id'])
        datapath_id = n['datapath_id']
        device_id = n['device_id']
        protocols = n['protocols']
        prefix = yield self._get_prefix_node(device_id)

        yield self._add_vnode(prefix=prefix,
                              label=label,
                              datapath_id=datapath_id,
                              protocols=protocols)

    @inlineCallbacks
    def _withdrawn_node(self, n):
        label = self._get_label(n['id'])
        device_id = n['device_id']

        prefix = yield self._get_prefix_node(device_id)
        self._rem_vnode(prefix, label=label)

    @inlineCallbacks
    def _deploy_link(self, s, l):

        @inlineCallbacks
        def get_slice_node(sid, vdid):
            uri = "sliceservice.get_slice_node"
            ret = yield self._send_call(uri, slice_id=sid, virtdev_id=vdid)
            returnValue(ret[1])

        @inlineCallbacks
        def get_phy_link(u, v):
            uri = "topologyservice.get_link"
            ret = yield self._send_call(uri, source=u, target=v)
            returnValue(ret)

        @inlineCallbacks
        def has_phy_link(u, v):
            uri = "topologyservice.has_link"
            ret = yield self._send_call(uri, source_id=u, target_id=v)
            returnValue(ret)

        @inlineCallbacks
        def add_p2p_link(virt_src, virt_dst):
            phy_src_id = virt_dst['device_id']
            phy_dst_id = virt_src['device_id']

            phy_link = yield get_phy_link(phy_src_id, phy_dst_id)
            print(phy_link)
            key = l['key']

            virt_label_src = self._get_label(l['source'])
            virt_port_ingress = l['ingress']
            real_port_ingress = phy_link['ingress']
            prefix_ingress = yield self._get_prefix_node(phy_src_id)

            yield self._add_vport(prefix_ingress, virt_label_src, virt_port_ingress, real_port_ingress, key)

            virt_label_tgt = self._get_label(l['target'])
            virt_port_egress = l['egress']
            real_port_egress = phy_link['egress']
            prefix_egress = yield self._get_prefix_node(phy_dst_id)

            yield self._add_vport(prefix_egress, virt_label_tgt, virt_port_egress, real_port_egress, key)

        def add_bypass(virt_src, virt_dst):
            pass

        virt_src = yield get_slice_node(s, l['source'])
        virt_dst = yield get_slice_node(s, l['target'])

        phy_src_id = virt_dst['device_id']
        phy_dst_id = virt_src['device_id']
        print("before if")

        if has_phy_link(phy_src_id, phy_dst_id):
            yield add_p2p_link(virt_src, virt_dst)
        else:
            yield add_bypass(virt_src, virt_dst)

    def _register_slice(self, sid, slice):
        self._slices_registred.update({sid: slice})

    def _unregister_slice(self, sid):
        self._slices_registred.pop(sid)

    @inlineCallbacks
    def onJoin(self, details):
        self.log.info('Slice Builder Service Starting ...')
        yield self.register(self)
        self.log.info('Slice Builder Service Started ...')
        print()

    def onUserError(self, fail, msg):
        pass

    @wamp.register(uri='slicebuilderservice.deploy')
    def deploy(self, slice):
        nodes = slice['nodes']
        links = slice['links']
        slice_id = slice['graph']['slice_id']

        if len(nodes) == 0:
            self.log.info("No nodes to deploy")
            return False, None
        try:
            self._update_slice_status(slice_id, 9)
            #for n in nodes:
            #    self._deploy_node(n)
            #for l in links:
            #    self._deploy_link(slice_id, l)
            self._register_slice(slice_id, slice)
            self._update_slice_status(slice_id, 6)
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
