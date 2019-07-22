# -*- coding: utf-8 -*-
"""
* example for expand question type
* run example by typing `python example/checkbox.py` in your console
"""
from __future__ import print_function, unicode_literals
from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.wamp import Application, ApplicationSession, ApplicationRunner

import sys

from PyInquirer import style_from_dict, Token, prompt, print_json, Separator

from examples import custom_style_3
import pprint


config = {
    "orch_addr": "ws://127.0.0.1:8080/ws",
    "orch_realm": "realm1"
}

topology_service = {
    'set_node': 'topologyservice.set_node',
    'del_node': 'topologyservice.del_node',
    'get_node': 'topologyservice.get_node',
    'get_nodes': 'topologyservice.get_nodes',
    'has_node': 'topologyservice.has_node',
    'set_link': 'topologyservice.set_link',
    'del_link': 'topologyservice.del_link',
    'get_link': 'topologyservice.get_link',
    'get_links': 'topologyservice.get_links',
    'has_link': 'topologyservice.has_link',
    'set_instance': 'topologyservice.set_instance',
    'del_instance': 'topologyservice.del_instance',
    'get_instances': 'topologyservice.get_instances',
    'get_shortest_path': 'topologyservice.get_shortest_path',
    'get_topology': 'topologyservice.get_topology'
}

"""
def set_node():
    session =  ApplicationSession()


def do_topology():

    def set_node():
        questions = [
            {
                'type': 'input',
                'message': 'set datapath-id:',
                'name': 'datapath_id',
            },
            {
                'type': 'input',
                'message': ' set prefix-uri:',
                'name': 'prefix_uri',
            },
            {
                'type': 'input',
                'message': ' set label:',
                'name': 'datapath_id',
            }
        ]
        resp = prompt(questions, style=custom_style_3)
        app.session.


def do_config():
    def set_orch():
        questions = [
            {
                'type': 'input',
                'message': 'new address:',
                'name': 'address',
            }
        ]
        resp = prompt(questions, style=custom_style_3)
        config.update({"orch_addr": resp['address']})
        do_config()

    questions = [
        {
            'type': 'list',
            'message': 'choice a action:',
            'name': 'action',
            'choices': [
                '1: Change Orquestrator Address ({a})'.format(a=config.get("orch_addr")),
                '2: Exit'
            ]
        }
    ]
    answers = prompt(questions, style=custom_style_3)
    action = str(answers['action']).split(":")
    if action[0] == "1":
        set_orch()
    elif action[0] == "2":
        main()


def do_exit():
    exit(0)


def main():
    questions = [
        {
            'type': 'list',
            'message': 'choice a action:',
            'name': 'action',
            'choices': [
                'Slice',
                'Topology',
                'Configuration',
                'Exit'
            ]
        }
    ]
    try:
        answers = prompt(questions, style=custom_style_3)
        if answers["action"] == "Exit":
            do_exit()
        elif answers["action"] == "Topology":
            pass
        elif answers["action"] == "Slice":
            pass
        elif answers["action"] == "Configuration":
            config()
    except KeyboardInterrupt:
        exit(1)

"""


class SliceCli(ApplicationSession):

    def _main(self):
        questions = [
            {
                'type': 'list',
                'message': 'choice a action:',
                'name': 'action',
                'choices': [
                    'Slice',
                    'Topology',
                    'Configuration',
                    'Exit'
                ]
            }
        ]
        try:
            answers = prompt(questions, style=custom_style_3)
            if answers["action"] == "Exit":
                pass
            elif answers["action"] == "Topology":
                pass
            elif answers["action"] == "Slice":
                pass
            elif answers["action"] == "Configuration":
                pass
        except KeyboardInterrupt:
            exit(1)

    @inlineCallbacks
    def onJoin(self, details):
        print("Welcome vSDNOrches CLI")
        a = yield self.call(topology_service.get("get_nodes"))
        print(a)

        self._main()


if __name__ == '__main__':
    from twisted.python import log


    runner = ApplicationRunner(url=config.get("orch_addr"),
                               realm=config.get("orch_realm"))
    runner.run(SliceCli,start_reactor=False)
