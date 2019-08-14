from gevent import monkey

monkey.patch_all()

import json
from wampy import Client


class SliceManagerClient(object):
    def __init__(self, url='ws://127.0.0.1:8080/ws', realm='realm1'):
        self.url = url
        self.realm = realm

    def _call_connection(self, app, **kwargs):
        with Client(url=self.url, realm=self.realm) as client:
            ret = json.loads(client.call(app, **kwargs))
            if ret['error']:
                raise ValueError(ret['result'])
        return ret['result']

    def deploy_slice(self, slice_id):
        app = "sliceservice.deploy_slice"
        return self._call_connection(app=app, slice_id=slice_id)

    def set_slice(self, tenant_id, label, controller):
        app = "sliceservice.set_slice"
        return self._call_connection(app, tenant_id=tenant_id, label=label, controller=controller)

    def del_slice(self, slice_id):
        app = "sliceservice.del_slice"
        return self._call_connection(app, slice_id=slice_id)

    def get_slice(self, slice_id):
        app = "sliceservice.get_slice"
        return self._call_connection(app, slice_id=slice_id)

    def get_slices(self):
        app = "sliceservice.get_slices"
        return self._call_connection(app)

    def set_slice_node(self, slice_id, device_id, datapath_id, label, protocols):
        app = "sliceservice.set_slice_node"
        return self._call_connection(app,
                                     slice_id=slice_id,
                                     device_id=device_id,
                                     datapath_id=datapath_id,
                                     label=label,
                                     protocols=protocols)

    def del_slice_node(self, slice_id, virtdev_id):
        app = "sliceservice.del_slice_node"
        return self._call_connection(app, slice_id=slice_id, virtdev_id=virtdev_id)

    def get_slice_node(self, slice_id, virtdev_id):
        app = "sliceservice.get_slice_node"
        return self._call_connection(app, slice_id=slice_id, virtdev_id=virtdev_id)

    def get_slice_nodes(self, slice_id):
        app = "sliceservice.get_slice_nodes"
        return self._call_connection(app, slice_id=slice_id)

    def set_slice_link(self, slice_id, src_virtdev_id, dst_virtdev_id, tunnel, key):
        app = "sliceservice.set_slice_link"
        return self._call_connection(app,
                                     slice_id=slice_id,
                                     src_virtdev_id=src_virtdev_id,
                                     dst_virtdev_id=dst_virtdev_id,
                                     tunnel=tunnel,
                                     key=key)

    def del_slice_link(self, slice_id, virtlink_id):
        app = "sliceservice.del_slice_link"
        return self._call_connection(app, slice_id=slice_id, virtlink_id=virtlink_id)

    def get_slice_link(self, slice_id, virtlink_id):
        app = "sliceservice.get_slice_link"
        return self._call_connection(app, slice_id=slice_id, virtlink_id=virtlink_id)

    def get_slice_links(self, slice_id):
        app = "sliceservice.get_slice_links"
        return self._call_connection(app, slice_id=slice_id)

    def get_slice_status(self, slice_id):
        app = "sliceservice.get_slice_status"
        return self._call_connection(app, slice_id=slice_id)

    def update_slice_status(self,slice_id, code):
        app = 'sliceservice.update_slice_status'
        return self._call_connection(app, slice_id=slice_id, code=code)

class TopologyServiceClient(object):
    def __init__(self, url='ws://127.0.0.1:8080/ws', realm='realm1'):
        self.url = url
        self.realm = realm

    def _call_connection(self, app, **kwargs):
        with Client(url=self.url, realm=self.realm) as client:
            err, msg = client.call(app, **kwargs)
            if err:
                raise ValueError(msg)
        return msg

    def _publish_connection(self, topic, **kwargs):
        with Client(url=self.url, realm=self.realm) as client:
            err, msg = client.publish(topic=topic, **kwargs)
            if err:
                raise ValueError(msg)
        return err, msg

    def set_node(self, datapath_id, prefix_uri, label):
        app = 'topologyservice.set_node'
        return self._call_connection(app, datapath_id=datapath_id, prefix_uri=prefix_uri, label=label)

    def del_node(self, device_id):
        app = 'topologyservice.del_node'
        return self._call_connection(app, device_id=device_id)

    def get_node(self, device_id):
        app = 'topologyservice.get_node'
        return self._call_connection(app, device_id=device_id)

    def get_nodes(self):
        app = 'topologyservice.get_nodes'
        return self._call_connection(app)

    def has_node(self, device_id):
        app = 'topologyservice.has_node'
        return self._call_connection(app, device_id=device_id)

    def set_link(self, source_id, target_id, source_portnum, target_portnum, tunnel, key):
        app = 'topologyservice.set_link'
        return self._call_connection(app,
                                     source_id=source_id,
                                     target_id=target_id,
                                     source_portnum=source_portnum,
                                     target_portnum=target_portnum,
                                     tunnel=tunnel,
                                     key=key)

    def del_link(self, link_id):
        app = 'topologyservice.del_link'
        return self._call_connection(app, link_id=link_id)

    def get_link(self, link_id):
        app = 'topologyservice.get_link'
        return self._call_connection(app, link_id=link_id)

    def get_links(self):
        app = 'topologyservice.get_links'
        return self._call_connection(app)

    def has_link(self, source_id, target_id):
        app = "topologyservice.has_link"
        return self._call_connection(app, source_id=source_id, target_id=target_id)

    def set_instance(self, device_id, virtdev_id):
        app = "topologyservice.set_instance"
        return self._call_connection(app, device_id=device_id, virtdev_id=virtdev_id)

    def del_instance(self, device_id, virtdev_id):
        app = "topologyservice.del_instance"
        return self._call_connection(app, device_id=device_id, virtdev_id=virtdev_id)

    def get_shortest_path(self, source_id, target_id):
        app = "topologyservice.get_shortest_path"
        return self._call_connection(app, source_id=source_id, target_id=target_id)

    def get_topology(self):
        app = "topologyservice.get_topology"
        return self._call_connection(app)


class SliceBuilderClient(object):
    def __init__(self, url='ws://127.0.0.1:8080/ws', realm='realm1'):
        self.url = url
        self.realm = realm

    def _call_connection(self, app, **kwargs):
        with Client(url=self.url, realm=self.realm) as client:
            err, msg = client.call(app, **kwargs)
            if err:
                raise ValueError(err)
        return msg

    def deploy(self, slice):
        app = 'slicebuilderservice.deploy'
        return self._call_connection(app, slice=slice)
