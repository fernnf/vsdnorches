#!/usr/bin/python3
from gevent import monkey

monkey.patch_all()

import click
import json
from wampy import Client
from pprint import pprint as p

from SliceClients import SliceManagerClient, TopologyServiceClient

config = {
    'url': 'ws://127.0.0.1:8080/ws',
    'realm': 'realm1'
}


def get_connection(app, **kwargs):
    with Client(url=config.get('url'), realm=config.get('realm')) as client:
        err, msg = client.call(app, **kwargs)
    return err, msg


def print_info(msg):
    click.echo(print(json.dumps(msg, indent=4, sort_keys=True)))


def print_slice(s):
    if isinstance(s, list):
        for i in s:
            click.echo(p(i))
    else:
        click.echo(p(s))


def print_node(n):
    if isinstance(n, list):
        for i in n:
            click.echo(p(i))
    else:
        click.echo(p(n))


def print_link(l):
    if isinstance(l, list):
        for i in l:
            click.echo(p(i))
    else:
        click.echo(p(l))


def is_exist_node(ctx, parm, value):
    node_svr = "topologyservice.has_node"
    # link_svr="topologyservice.has_link"

    client = config.get('client')
    if client is None:
        raise click.Abort("client was not configurated")


def check_dpid(ctx, param, value):
    if len(value) != 16:
        raise click.BadOptionUsage(option_name=param,
                                   message="the datapath id must have 16 digits")
    import string
    if all(c in string.hexdigits for c in value.split()):
        raise click.BadOptionUsage(option_name=param,
                                   message="this datapath id is not valid")


def check_ctl_addr(ctx, param, value):
    addr = value.split(':')

    if len(addr) != 3:
        raise click.BadOptionUsage(option_name=param,
                                   message="the controller address is not valid")

    if addr[0] != 'tcp':
        raise click.BadOptionUsage(option_name=param,
                                   message="just tcp protocol is supported only")

    import socket
    try:
        socket.inet_aton(addr[1])
    except Exception:
        raise click.BadOptionUsage(option_name=param,
                                   message="the ip address is not valid")


@click.group()
@click.option('--url', '-u', default=config.get('url'), help='Orquestrator address config',
              show_default=config.get('url'))
@click.option('--realm', '-r', default=config.get('realm'), help='Orquestrator realm config',
              show_default=config.get('realm'))
def main(url, realm):
    if not url == config.get('url'):
        config.update({'url': url})

    if not realm == config.get('realm'):
        config.update({'realm': realm})


"""
Subcommand Create
"""


@main.group()
def create():
    pass


@create.command('slice')
@click.argument('tenant-id', required=True)
@click.option('--label', '-l', required=False)
@click.option('--controller', '-c', required=False)
def create_slice(tenant_id, label, controller):
    smc = SliceManagerClient(url = config['url'], realm = config['realm'])
    try:
        ret = smc.set_slice(tenant_id, label, controller)
        click.echo(ret)
    except Exception as ex:
        raise click.UsageError(str(ex))

"""
END
"""

"""
Subcommand Delete
"""


@main.group()
def delete():
    pass


@delete.command('slice')
@click.argument('slice-id')
def delete_slice(slice_id):
    smc = SliceManagerClient(url = config['url'], realm = config['realm'])
    try:
        ret = smc.del_slice(slice_id)
        click.echo(ret)
    except Exception as ex:
        raise click.UsageError(str(ex))

"""
END
"""
"""
Subcommand Show
"""


@main.group()
def show():
    pass


@show.command("topology")
def show_topology():
    tsc = TopologyServiceClient(url = config['url'], realm = config['realm'])
    try:
        ret = tsc.get_topology()
        print_info(ret)
    except Exception as ex:
        raise click.UsageError(str(ex))

@show.group("slice", invoke_without_command=True)
@click.option('--slice-id', '-s')
@click.pass_context
def show_slice(ctx, slice_id):
    smc = SliceManagerClient(url = config['url'], realm = config['realm'])
    try:
        if slice_id is None:
            ret = smc.get_slices()
        else:
            ret = smc.get_slice(slice_id)

        print_info(ret[0])
    except Exception as ex:
        raise click.UsageError(str(ex))

@show_slice.command('node')
@click.argument('slice-id', required=True)
@click.option('--virtdev-id', '-v', required = False)
def show_slice_node(slice_id, virtdev_id):
    smc = SliceManagerClient(url = config['url'], realm = config['realm'])
    try:
        if virtdev_id is None:
            ret = smc.get_slice_nodes(slice_id)
        else:
            ret = smc.get_slice_node(slice_id, virtdev_id)
        print_info(ret)
    except Exception as ex:
        raise click.UsageError(str(ex))

@show_slice.command('link')
@click.argument('slice-id', required=True)
@click.option('--virtlink-id', '-l', required = False)
def show_slice_link(slice_id, virtlink_id):
    smc = SliceManagerClient(url = config['url'], realm = config['realm'])
    try:
        if virtlink_id is None:
            ret = smc.get_slice_links(slice_id)
        else:
            ret = smc.get_slice_link(slice_id, virtlink_id)

        print_info(ret)

    except Exception as ex:
        raise click.UsageError(str(ex))

"""
END
"""
"""
Subcommand Configure
"""


@main.group()
def configure():
    pass


@configure.group("slice", invoke_without_command=True)
@click.argument('slice-id', required=True)
@click.pass_context
def config_slice(ctx, slice_id):
    if ctx.invoked_subcommand is not None:
        ctx.obj = {'slice_id': slice_id}
    else:
        click.echo(ctx.get_help())


@config_slice.group("add")
def config_slice_add():
    pass


@config_slice_add.command('node')
@click.argument('device-id', required=True)
@click.argument('label', required=True)
@click.option('--datapath_id', '-d', required=False)
@click.option('--protocols', '-p', required=False)
@click.pass_obj
def config_slice_add_node(obj, device_id, datapath_id, label, protocols):
    smc = SliceManagerClient(url = config['url'], realm = config['realm'])
    slice_id = obj.get('slice_id')
    try:
        ret = smc.set_slice_node(slice_id, device_id, datapath_id, label, protocols)
        click.echo(ret)
    except Exception as ex:
        raise click.UsageError(str(ex))


@config_slice_add.command('link')
@click.argument('source-node-id', required=True)
@click.argument('target-node-id', required=True)
@click.option('--tunnel', '-t', required=False, help="tunnel type, e.g. ethernet or vxlan")
@click.option('--key', '-k', required=False, help="key identification, e.g. vlan-id, vxlan-id")
@click.pass_obj
def config_slice_add_link(obj, source_node_id, target_node_id, tunnel, key):
    smc = SliceManagerClient(url = config['url'], realm = config['realm'])
    slice_id = obj.get('slice_id')
    try:
        ret = smc.set_slice_link(slice_id, source_node_id, target_node_id, tunnel, key)
        click.echo(ret)
    except Exception as ex:
        raise click.UsageError(str(ex))


@config_slice.group("del")
def config_slice_del():
    pass


@config_slice.group("deploy", invoke_without_command=True)
@click.pass_obj
def config_slice_deploy(obj):
    smc = SliceManagerClient(url = config['url'], realm = config['realm'])
    slice_id = obj.get('slice_id')
    try:
        ret = smc.deploy_slice(slice_id)
        click.echo(ret)
    except Exception as ex:
        raise click.UsageError(str(ex))

@config_slice.group("start")
def config_slice_start():
    pass


@config_slice.group("stop")
def config_slice_start():
    pass


@config_slice_del.command('node')
@click.argument('virtdev-id', required=True)
@click.pass_obj
def config_slice_del_node(obj, virtdev_id):
    smc = SliceManagerClient(url = config['url'], realm = config['realm'])
    slice_id = obj.get('slice_id')
    try:
        ret = smc.del_slice_node(slice_id, virtdev_id)
        click.echo(ret)
    except Exception as ex:
        raise click.UsageError(str(ex))

@config_slice_del.command('link')
@click.argument('virtlink-id', required = True)
@click.pass_obj
def config_slice_del_link(obj, virtlink_id):
    smc = SliceManagerClient(url = config['url'], realm = config['realm'])
    slice_id = obj.get('slice_id')
    try:
        ret = smc.del_slice_link(slice_id, virtlink_id)
        click.echo(ret)
    except  Exception as ex:
        raise click.UsageError(str(ex))

@configure.group("topology")
def config_topo():
    pass


@config_topo.group('add')
def config_topo_add():
    pass


@config_topo_add.command("link")
@click.argument("source-id", required=True)
@click.argument("target-id", required=True)
@click.argument("source-portnum", required=True)
@click.argument("target-portnum", required=True)
@click.option('--tunnel', '-t', required=False)
@click.option('--key', '-k', required=False)
def config_topo_add_link(source_id, target_id, source_portnum, target_portnum, tunnel, key):
    tsc = TopologyServiceClient(url = config['url'], realm = config['realm'])
    try:
        ret = tsc.set_link(source_id, target_id, source_portnum, target_portnum, tunnel, key)
        click.echo(ret)
    except Exception as ex:
        raise click.UsageError(str(ex))

@config_topo.group('del')
def config_topo_del():
    pass


@config_topo_del.command("link")
@click.argument("link-id", required=True)
def config_topo_del_link(link_id):
    tsc = TopologyServiceClient(url = config['url'], realm = config['realm'])
    try:
        ret = tsc.del_link(link_id)
        click.echo(ret)
    except Exception as ex:
        raise click.UsageError(str(ex))

"""
END
"""

if __name__ == '__main__':
    main()
