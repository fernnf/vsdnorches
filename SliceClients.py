from gevent import monkey

monkey.patch_all()

import json
from wampy import Client

from wampy.messages.error import Error as error


def check_error(ret):
    if isinstance(ret, error):
        raise Exception("ERROR: {}:{}".format(ret.error, ret.message))


class SliceManagerClient(object):
    def __init__(self, url='ws://127.0.0.1:8080/ws', realm='realm1'):
        self.url = url
        self.realm = realm

    def deploy_slice(self, slice_id):
        app = "sliceservice.deploy_slice"
        with Client(url=self.url, realm=self.realm) as client:
            client.call(app, slice_id=slice_id)

    def set_slice(self, tenant_id, label, controller):
        app = "sliceservice.set_slice"
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app, tenant_id=tenant_id, label=label, controller=controller)
            check_error(ret)
            return ret

    def del_slice(self, slice_id):
        app = "sliceservice.del_slice"
        with Client(url=self.url, realm=self.realm) as client:
            client.call(app, slice_id=slice_id)

    def get_slice(self, slice_id):
        app = "sliceservice.get_slice"
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app, slice_id=slice_id)
            check_error(ret)
            return ret

    def get_slices(self):
        app = "sliceservice.get_slices"
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app)
            check_error(ret)
            return ret

    def set_slice_node(self, slice_id, device_id, datapath_id, label, protocols):
        app = "sliceservice.set_slice_node"
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app,
                              slice_id=slice_id,
                              device_id=device_id,
                              datapath_id=datapath_id,
                              label=label,
                              protocols=protocols)
            check_error(ret)
            return ret

    def del_slice_node(self, slice_id, virtdev_id):
        app = "sliceservice.del_slice_node"
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app, slice_id=slice_id, virtdev_id=virtdev_id)
            check_error(ret)

    def get_slice_node(self, slice_id, virtdev_id):
        app = "sliceservice.get_slice_node"
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app, slice_id=slice_id, virtdev_id=virtdev_id)
            check_error(ret)
            return ret

    def get_slice_nodes(self, slice_id):
        app = "sliceservice.get_slice_nodes"
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app, slice_id=slice_id)
            check_error(ret)
            return ret

    def set_slice_host(self, slice_id, virtdev_id, vlan_id, phy_portnum):
        app = 'sliceservice.set_slice_host'
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app, slice_id=slice_id, virtdev_id=virtdev_id, vlan_id=vlan_id, phy_portnum=phy_portnum)
            check_error(ret)

    def del_slice_host(self, slice_id, virtdev_id, virt_portnum):
        app = 'sliceservice.del_slice_host'
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app, slice_id=slice_id, virtdev_id=virtdev_id, virt_portnum=virt_portnum)
            check_error(ret)

    def get_slice_hosts(self, slice_id, virtdev_id):
        app = 'sliceservice.get_slice_hosts'
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app, slice_id=slice_id, virtdev_id=virtdev_id)
            check_error(ret)

    def set_slice_link(self, slice_id, src_virtdev_id, dst_virtdev_id, tunnel):
        app = "sliceservice.set_slice_link"
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app,
                              slice_id=slice_id,
                              src_virtdev_id=src_virtdev_id,
                              dst_virtdev_id=dst_virtdev_id,
                              tunnel=tunnel)
            check_error(ret)
            return ret

    def del_slice_link(self, slice_id, virtlink_id):
        app = "sliceservice.del_slice_link"
        with Client(url=self.url, realm=self.realm) as client:
            client.call(app, slice_id=slice_id, virtlink_id=virtlink_id)

    def get_slice_link(self, slice_id, virtlink_id):
        app = "sliceservice.get_slice_link"
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app, slice_id=slice_id, virtlink_id=virtlink_id)
            check_error(ret)
            return ret

    def get_slice_links(self, slice_id):
        app = "sliceservice.get_slice_links"
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app, slice_id=slice_id)
            check_error(ret)
            return ret

    def get_slice_status(self, slice_id):
        app = "sliceservice.get_slice_status"
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app, slice_id=slice_id)
            check_error(ret)
            return ret

    def update_slice_status(self, slice_id, code):
        app = 'sliceservice.update_slice_status'
        with Client(url=self.url, realm=self.realm) as client:
            client.call(app, slice_id=slice_id, code=code)


class TopologyServiceClient(object):
    def __init__(self, url='ws://127.0.0.1:8080/ws', realm='realm1'):
        self.url = url
        self.realm = realm

    def _call_connection(self, app, **kwargs):
        with Client(url=self.url, realm=self.realm) as client:
            ret = json.loads(client.call(app, **kwargs))
        return ret['result']

    def _publish_connection(self, topic, **kwargs):
        with Client(url=self.url, realm=self.realm) as client:
            client.publish(topic=topic, **kwargs)

    def set_node(self, datapath_id, prefix_uri, label):
        app = 'topologyservice.set_node'
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app, datapath_id=datapath_id, prefix_uri=prefix_uri, label=label)
            check_error(ret)
            return ret

    def del_node(self, device_id):
        app = 'topologyservice.del_node'
        with Client(url=self.url, realm=self.realm) as client:
            client.call(app, device_id=device_id)

    def get_node(self, device_id):
        app = 'topologyservice.get_node'
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app, device_id=device_id)
            check_error(ret)
            return ret

    def get_nodes(self):
        app = 'topologyservice.get_nodes'
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app)
            check_error(ret)
            return ret

    def has_node(self, device_id):
        app = 'topologyservice.has_node'
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app, device_id=device_id)
            check_error(ret)
            return ret

    def set_link(self, source_id, target_id, source_portnum, target_portnum, tunnel, key):
        app = 'topologyservice.set_link'
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app,
                              source_id=source_id,
                              target_id=target_id,
                              source_portnum=source_portnum,
                              target_portnum=target_portnum,
                              tunnel=tunnel,
                              key=key)

            check_error(ret)
            return ret

    def del_link(self, link_id):
        app = 'topologyservice.del_link'
        with Client(url=self.url, realm=self.realm) as client:
            client.call(app, link_id=link_id)

    def get_link(self, link_id):
        app = 'topologyservice.get_link'
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app, link_id=link_id)
            check_error(ret)
            return ret

    def get_links(self):
        app = 'topologyservice.get_links'
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app)
            check_error(ret)
            return ret

    def has_link(self, source_id, target_id):
        app = "topologyservice.has_link"
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app, source_id=source_id, target_id=target_id)
            check_error(ret)
            return ret

    def set_instance(self, device_id, virtdev_id):
        app = "topologyservice.set_instance"
        with Client(url=self.url, realm=self.realm) as client:
            client.call(app, device_id=device_id, virtdev_id=virtdev_id)

    def del_instance(self, device_id, virtdev_id):
        app = "topologyservice.del_instance"
        with Client(url=self.url, realm=self.realm) as client:
            client.call(app, device_id=device_id, virtdev_id=virtdev_id)

    def get_shortest_path(self, source_id, target_id):
        app = "topologyservice.get_shortest_path"
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app, source_id=source_id, target_id=target_id)
            check_error(ret)
            return ret

    def get_topology(self):
        app = "topologyservice.get_topology"
        with Client(url=self.url, realm=self.realm) as client:
            ret = client.call(app)
            check_error(ret)
            return ret


class SliceBuilderClient(object):
    def __init__(self, url='ws://127.0.0.1:8080/ws', realm='realm1'):
        self.url = url
        self.realm = realm

    def deploy(self, slice):
        app = 'slicebuilderservice.deploy'
        with Client(url=self.url, realm=self.realm) as client:
            client.call(app, slice=slice)
