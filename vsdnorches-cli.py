#!/usr/bin/python3
from gevent import monkey

monkey.patch_all()

import click

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


# Topology Sub-commands
#

@main.group()
def create():
    pass


@main.group()
def delete():
    pass


# Show sub-commands
@main.group()
def show():
    pass


@show.command("topology")
def show_topology():
    app = 'topologyservice.get_topology'

    err, msg = get_connection(app)
    if err:
        raise click.UsageError(msg)
    msg.pop('directed')
    msg.pop('multigraph')
    click.echo(p(msg, indent=4))


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

            print_slice(msg)
        except Exception as ex:
            raise click.UsageError(str(ex))


@show_slice.command('node')
@click.argument('slice-id', required=True)
@click.argument('node-id', required=False)
def show_slice_node(ctx, slice_id, node_id):
    app = ['sliceservice.get_slice_node', 'sliceservice.get_slice_nodes']
    try:
        if node_id is None:
            err, msg = get_connection(app[1], slice_id=slice_id)
        else:
            err, msg = get_connection(app[0], slice_id=slice_id, virtdev_id=node_id)

        if err:
            raise click.UsageError(msg)

        print_node(msg)
    except Exception as ex:
        raise click.UsageError(str(ex))


@show_slice.command('link')
@click.argument('slice-id', required=True)
@click.argument('link-id', required=False)
def show_slice_link(slice_id, link_id):
    app = ['sliceservice.get_slice_link', 'sliceservice.get_slice_links']

    try:
        if link_id is None:
            err, msg = get_connection(app[1], slice_id=slice_id)
        else:
            err, msg = get_connection(app[0], slice_id=slice_id, virtlink_id=link_id)

        if err:
            raise click.UsageError(msg)

        print_link(msg)
    except Exception as ex:
        raise click.UsageError(str(ex))


##
@main.group()
def configure():
    pass


@configure.group("slice", invoke_without_command=True)
@click.option('--slice-id', required=True)
@click.pass_context
def config_slice(ctx, slice_id):
    if ctx.invoked_subcommand is not None:
        ctx.obj = {'slice_id': slice_id}
    else:
        click.echo(ctx.get_help())


@config_slice.group("node")
def config_node():
    pass


@config_node.command('add')
@click.argument('device-id', required=True)
@click.argument('datapath_id', required=False)
@click.argument('label', required=False)
@click.argument('protocols', required=False)
@click.pass_obj
def config_node_add(obj, device_id, datapath_id, label, protocols):
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


@config_node.command('remove')
@click.argument('node-id', required=True)
@click.pass_obj
def config_node_remove(obj, node_id):
    app = 'sliceservice.del_slice_node'
    slice_id = obj.get('slice_id')
    try:
        err, msg = get_connection(app, slice_id=slice_id, node_id=node_id)
        if err:
            raise click.UsageError(msg)
    except Exception as ex:
        raise click.UsageError(str(ex))



if __name__ == '__main__':
    main()
