from gevent import monkey

monkey.patch_all()

import click

from wampy import Client
from pprint import pprint as p

config = {
    'url': 'ws://127.0.0.1:8080/ws',
    'realm': 'realm1'
}


def print_slice(n):
    n.pop('directed')
    n.pop('multigraph')
    click.echo(p(n))


def is_exist_node(ctx, parm, value):
    node_svr = "topologyservice.has_node"
    # link_svr="topologyservice.has_link"

    client = config.get('client')
    if client is None:
        raise click.Abort("client was not configurated")

def check_dpid(ctx, param, value):
    if len(value) != 16:
        raise click.BadOptionUsage(option_name=param, message="the datapath id must have 16 digits")
    import string
    if all(c in string.hexdigits for c in value.split()):
        raise click.BadOptionUsage(option_name=param, message="this datapath id is not valid")


def check_ctl_addr(ctx, param, value):
    addr = value.split(':')

    if len(addr) != 3:
        raise click.BadOptionUsage(option_name=param, message="the controller address is not valid")

    if addr[0] != 'tcp':
        raise click.BadOptionUsage(option_name=param, message="just tcp protocol is supported only")

    import socket
    try:
        socket.inet_aton(addr[1])
    except Exception:
        raise click.BadOptionUsage(option_name=param, message="the ip address is not valid")


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


@main.group()
def show():
    pass

# Show sub-commands
@show.command("node")
def show_node():
    pass


@show.command("slice")
@click.option('--slice-id', 'slice')
def show_slice(slice):
    app = ('sliceservice.get_slice', 'sliceservice.get_slices')
    with Client(url=config.get('url'), realm=config.get('realm')) as client:
        if slice is None:
            err, msg = client.call(app[1])

            if err:
                raise click.UsageError(msg)

            for i in msg:
                print_slice(i)
        else:
            err, msg = client.call(app[0], slice)
            if err:
                raise click.UsageError(msg)
            print_slice(msg)


@show.command("link")
def show_link():
    pass

##
@main.group()
def configure():
    pass




#@create.group()
#def slice():

"""
@slice.command()
@click.option('--tenant-id', 'tenant', required=True)
@click.option('--controller', required=True, callback=check_ctl_addr)
@click.option('--label', required=True)
def create(tenant, controller, label):
    svr = "sliceservice.set_slice"
    with Client(url=config.get('url'), realm=config.get('realm')) as client:
        err, msg = client.call(svr, tenant, label, controller)
        if err:
            raise click.UsageError(msg)
        click.echo(msg)


@slice.command()
@click.option('--slice-id', 'slice', required=True)
def delete(slice):
    svr = "sliceservice.del_slice"
    with Client(url=config.get('url'), realm=config.get('realm')) as client:
        err, msg = client.call(svr, slice)
        if err:
            raise click.UsageError(msg)


@slice.group()
def show():
    pass


@show.command()
@click.option('--slice-id', 'slice')
def slice(node):

    app = ('sliceservice.get_slice', 'sliceservice.get_slices')
    with Client(url=config.get('url'), realm=config.get('realm')) as client:
        if node is None:
            err, msg = client.call(app[1])

            if err:
                raise click.UsageError(msg)

            for i in msg:
                print_slice(i)
        else:
            err, msg = client.call(app[0], slice)
            if err:
                raise click.UsageError(msg)
            print_slice(msg)

@show.command()
@click.option('--node-id', 'node')
def node():
    pass

@slice.group()
def add():
    pass


@add.command()
@click.option('--datapath-id', callback=check_dpid, required=True)
def node():
    pass

@add.group()
def link():
    pass


@slice.group()
def rem():
    pass

# End
"""

if __name__ == '__main__':
    main()
