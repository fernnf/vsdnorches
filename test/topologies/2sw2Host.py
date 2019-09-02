import logging

from SliceClients import SliceManagerClient, TopologyServiceClient


def get_id_node(dpid):
    tsc = TopologyServiceClient()
    nodes = tsc.get_nodes()
    for n in nodes:
        id, data = n
        if data['datapath_id'] == dpid:
            return id
    return None


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
        vlink = smc.set_slice_link(slice_id=s, src_virtdev_id=src, dst_virtdev_id=dst, tunnel="vlan")
        logger.info("added virtual link <{i},{j}>".format(i=src, j=dst))
        return vlink

    slice = create()
    vsw1, vsw2 = add_nodes(slice)
    vlink = add_vlink(slice, vsw1, vsw2)
    return slice, vsw1, vsw2, vlink


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
