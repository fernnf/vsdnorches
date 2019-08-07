#!/usr/bin/python3
from gevent import monkey

monkey.patch_all()

import click
import json
from wampy import Client
from pprint import pprint as p

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
    app = 'sliceservice.set_slice'
    try:
        err, msg = get_connection(app,
                                  tenant_id=tenant_id,
                                  label=label,
                                  controller=controller)

        if err:
            click.echo(err)
            raise click.UsageError(msg)

        click.echo(msg)
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
    app = 'sliceservice.del_slice'
    try:
        err, msg = get_connection(app, slice_id=slice_id)
        if err:
            raise click.UsageError(msg)
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
    app = 'topologyservice.get_topology'

    err, msg = get_connection(app)
    if err:
        raise click.UsageError(msg)
    # msg.pop('directed')
    # msg.pop('multigraph')
    print_info(msg)


@show.group("slice", invoke_without_command=True)
@click.option('--slice-id', '-s')
@click.pass_context
def show_slice(ctx, slice_id):
    app = ['sliceservice.get_slice', 'sliceservice.get_slices']
    if ctx.invoked_subcommand is None:
        try:
            if slice_id is None:
                err, msg = get_connection(app[1])
            else:
                err, msg = get_connection(app[0], slice_id=slice_id)

            if err:
                raise click.UsageError(msg)
            print_info(msg[0])

        except Exception as ex:
            raise click.UsageError(str(ex))


@show_slice.command('node')
@click.argument('slice-id', required=True)
@click.option('--node-id', '-n', required=False)
def show_slice_node(slice_id, node_id):
    app = ['sliceservice.get_slice_node', 'sliceservice.get_slice_nodes']
    try:
        if node_id is None:
            err, msg = get_connection(app[1], slice_id=slice_id)
        else:
            err, msg = get_connection(app[0], slice_id=slice_id, virtdev_id=node_id)

        if err:
            raise click.UsageError(msg)

        print_info(msg)

    except Exception as ex:
        raise click.UsageError(str(ex))


@show_slice.command('link')
@click.argument('slice-id', required=True)
@click.option('--link-id', '-l', required=False)
def show_slice_link(slice_id, link_id):
    app = ['sliceservice.get_slice_link', 'sliceservice.get_slice_links']

    try:
        if link_id is None:
            err, msg = get_connection(app[1], slice_id=slice_id)
        else:
            err, msg = get_connection(app[0], slice_id=slice_id, virtlink_id=link_id)

        if err:
            raise click.UsageError(msg)

        print_info(msg)

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
    app = ["sliceservice.deploy_slice"]
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
    app = 'sliceservice.set_slice_node'
    slice_id = obj.get('slice_id')
    try:
        err, msg = get_connection(app,
                                  slice_id=slice_id,
                                  device_id=device_id,
                                  datapath_id=datapath_id,
                                  label=label,
                                  protocols=protocols)

        if err:
            raise click.UsageError(msg)

        click.echo(msg)
    except Exception as ex:
        raise click.UsageError(str(ex))


@config_slice_add.command('link')
@click.argument('source-node-id', required=True)
@click.argument('target-node-id', required=True)
@click.option('--tunnel', '-t', required=False, help="tunnel type, e.g. ethernet or vxlan")
@click.option('--key', '-k', required=False, help="key identification, e.g. vlan-id, vxlan-id")
@click.pass_obj
def config_slice_add_link(obj, source_node_id, target_node_id, tunnel, key):
    app = 'sliceservice.set_slice_link'
    slice_id = obj.get('slice_id')
    try:
        err, msg = get_connection(app,
                                  slice_id=slice_id,
                                  src_virtdev_id=source_node_id,
                                  dst_virtdev_id=target_node_id,
                                  tunnel=tunnel,
                                  key=key)
        if err:
            raise click.UsageError(msg)
    except Exception as ex:
        raise click.UsageError(str(ex))


@config_slice.group("del")
def config_slice_del():
    pass


@config_slice.group("deploy", invoke_without_command=True)
@click.pass_obj
def config_slice_deploy(obj):
    app = "sliceservice.deploy_slice"
    slice_id = obj.get('slice_id')
    try:
        err, msg = get_connection(app, slice_id=slice_id)
        click.echo(msg)
        if err:
            raise click.UsageError(msg)
    except Exception as ex:
        raise click.UsageError(str(ex))

    # click.echo("deploy " + slice_id)


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
    app = 'sliceservice.del_slice_node'
    slice_id = obj.get('slice_id')

    try:
        err, msg = get_connection(app, slice_id=slice_id, virtdev_id=virtdev_id)
        if err:
            raise click.UsageError(msg)

    except Exception as ex:
        raise click.UsageError(str(ex))


@config_slice_del.command('link')
@click.argument('link-id', required=True)
@click.pass_obj
def config_slice_del_link(obj, link_id):
    app = 'sliceservice.del_slice_link'
    slice_id = obj.get('slice_id')
    try:
        err, msg = get_connection(app, slice_id=slice_id, virtlink_id=link_id)
        if err:
            raise click.UsageError(msg)
    except Exception as ex:
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
    app = 'topologyservice.set_link'

    try:
        err, msg = get_connection(app,
                                  source_id=source_id,
                                  target_id=target_id,
                                  source_portnum=source_portnum,
                                  target_portnum=target_portnum,
                                  tunnel=tunnel,
                                  key=key)
        if err:
            raise click.UsageError(msg)
        click.echo(msg)
    except Exception as ex:
        raise click.UsageError(str(ex))


@config_topo.group('del')
def config_topo_del():
    pass


@config_topo_del.command("link")
@click.argument("link-id", required=True)
def config_topo_del_link(link_id):
    app = 'topologyservice.del_link'
    try:
        err, msg = get_connection(app, link_id=link_id)
        if err:
            raise click.UsageError(msg)
    except Exception as ex:
        raise click.UsageError(str(ex))


"""
END
"""

if __name__ == '__main__':
    main()
