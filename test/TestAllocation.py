import logging

import coloredlogs as coloredlogs

from SliceClients import SliceManagerClient, TopologyServiceClient


def create_slice():
    smc = SliceManagerClient()

    def create():
        slice = smc.set_slice("1", "script_alloc", "")
        logger.info("Slice created {i}".format(i=slice))
        return slice

    def add_nodes(s):
        switch1 = get_id_node("0000000000000001")
        switch2 = get_id_node("0000000000000002")

        vswitch1 = smc.set_slice_node(slice_id=s, device_id=switch1, datapath_id=None, protocols=None, label="switch1")
        vswitch2 = smc.set_slice_node(slice_id=s, device_id=switch2, datapath_id=None, protocols=None, label="switch2")

        logger.info("added vswitch1 {i}".format(i=vswitch1))
        logger.info("added vswithc2 {i}".format(i=vswitch2))

        return vswitch1, vswitch2

    def add_vlink(s, src, dst):
        vlink = smc.set_slice_link(slice_id=s, src_virtdev_id=src, dst_virtdev_id=dst, tunnel="vlan", key="1")
        logger.info("added virtual link <{i},{j}>".format(i=src, j=dst))
        return vlink

    slice = create()
    vsw1, vsw2 = add_nodes(slice)
    vlink = add_vlink(slice, vsw1, vsw2)
    return slice, vsw1, vsw2, vlink


def deploy_slice(s):
    print(s)
    smc = SliceManagerClient()
    smc.deploy_slice(s)


def del_slice(s, n1, n2):
    smc = SliceManagerClient()

    def del_nodes():
        smc.del_slice_node(slice_id=s, virtdev_id=n1)
        smc.del_slice_node(slice_id=s, virtdev_id=n2)

    def del_slice():
        smc.del_slice(slice_id=s)

    del_nodes()
    del_slice()
    logger.info("deleted slice <{i}>".format(i=s))


def get_id_node(dpid):
    tsc = TopologyServiceClient()
    nodes = tsc.get_nodes()
    for n in nodes:
        id, data = n
        if data['datapath_id'] == dpid:
            return id
    return None


def config_links(src, dst):
    tsc = TopologyServiceClient()
    src_node = get_id_node(src)
    dst_node = get_id_node(dst)
    tsc.set_link(src_node, dst_node, "2", "2", tunnel="Ethernet", key=None)

def update_status(slice_id, code):
    smc = SliceManagerClient()
    smc.update_slice_status(slice_id, code)

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    coloredlogs.install(logger=logger)
    config_links("0000000000000001", "0000000000000002")
    slice = create_slice()
    print(slice)
    slice_id, _, _, _ = slice
    update_status(slice_id, code=2)
    #deploy_slice(slice_id)

