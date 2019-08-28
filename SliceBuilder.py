from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError
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

    def onUserError(self, fail, msg):
        pass

    @wamp.register(uri='slicebuilderservice.deploy')
    def deploy(self, slice):

        def register_slice(i,s):
            self._slices_registred.update({i: s})


        @inlineCallbacks
        def update_status(id, code):
            app = "sliceservice.update_slice_status"
            yield self.call(app, slice_id=id, code=code)

        @inlineCallbacks
        def deploy_vswitch(n):
            switch_id = n["device_id"]
            name = n['id'][:8]
            datapath_id = n['datapath_id']
            protocols = n['protocols']

            res = yield self.call("topologyservice.get_node", device_id=switch_id)
            switch = res[1]
            action = "{}.add_vswitch".format(switch['prefix_uri'])
            yield self.call(action,
                            name=name,
                            datapath_id=datapath_id,
                            protocols=protocols)

            hosts = n['hosts']

            if len(hosts) > 0:
                for h in hosts.values():
                    vlan_id = h['vlan_id']
                    phy_portnum = h['phy_portnum']
                    virt_portnum = h['virt_portnum']
                    cmd = '{}.add_vport'.format(switch['prefix_uri'])

                    yield self.call(cmd,
                                    vswitch=name,
                                    vlan_id=vlan_id,
                                    source_portnum=virt_portnum,
                                    phy_portnum=phy_portnum)

        @inlineCallbacks
        def deploy_link(s, l):

            vlan_id = l['key']

            source_portnum = l['ingress']
            source_vswitch_name = l['source'][:8]
            target_portnum = l['egress']
            target_vswitch_name = l['target'][:8]

            src_vsw_id, src_vsw = yield self.call("sliceservice.get_slice_node", slice_id=s, virtdev_id=l['source'])
            tgt_vsw_id, tgt_vsw = yield self.call("sliceservice.get_slice_node", slice_id=s, virtdev_id=l['target'])

            src_sw_id, src_sw = yield self.call("topologyservice.get_node", device_id=src_vsw['device_id'])
            tgt_sw_id, tgt_sw = yield self.call("topologyservice.get_node", device_id=tgt_vsw['device_id'])

            ret = yield self.call("topologyservice.has_link", source_id=src_vsw['device_id'],
                                  target_id=tgt_vsw['device_id'])
            print(ret)
            if ret:
                phy_link = yield self.call("topologyservice.get_link", source=src_sw_id, target=tgt_sw_id)
                source_phy_portnum = phy_link['ingress']
                target_phy_portnum = phy_link['egress']

                act_ingress = "{}.add_vport".format(src_sw['prefix_uri'])
                print(act_ingress)
                yield self.call(act_ingress,
                                vswitch=source_vswitch_name,
                                vlan_id=vlan_id,
                                source_portnum=source_portnum,
                                phy_portnum=source_phy_portnum)
                act_egress = "{}.add_vport".format(tgt_sw['prefix_uri'])
                print(act_egress)
                yield self.call(act_egress,
                                vswitch=target_vswitch_name,
                                vlan_id=vlan_id,
                                source_portnum=target_portnum,
                                phy_portnum=target_phy_portnum)

        nodes = slice['nodes']
        links = slice['links']
        slice_id = slice['graph']['slice_id']

        try:
            update_status(slice_id, 2)
            for n in nodes:
                deploy_vswitch(n)
            for l in links:
                deploy_link(slice_id, l)
            register_slice(slice_id, slice)
            update_status(slice_id, 6)

        except Exception as ex:
            error = 'slicebuilderservice.error.deploy'
            raise ApplicationError(error, msg=str(ex))

    @wamp.register(uri='slicebuilderservice.start')
    def start(self):
        pass

    @wamp.register(uri='slicebuilderservice.stop')
    def stop(self):
        pass

    @wamp.register(uri='slicebuilderservice.remove')
    def remove(self, slice_id):
        pass
