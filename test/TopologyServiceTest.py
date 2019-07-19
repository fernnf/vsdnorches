import unittest

from autobahn.twisted.wamp import ApplicationSession
from twisted.internet.defer import inlineCallbacks
from SliceTopology import TopologyService


class TopologyServiceTest(unittest.TestCase, ApplicationSession):

    def setUp(self) -> None:
        self.top = TopologyService()

    def tearDown(self) -> None:
        self.top = None

    def test_set_phy_node(self):
        datapath_id = "1000000000000001"
        uri = "agent.1000000000000001"
        label = "MX"
        resp = self.top.set_node(datapath_id, uri, label)
        self.assertIsNotNone(resp)
        print(resp)

    def test_del_phy_node(self):
        datapath_id = "1000000000000001"
        uri = "agent.1000000000000001"
        label = "MX"
        resp = self.top.set_node(datapath_id, uri, label)
        self.assertIsNotNone(resp)

        err, id = resp

        import uuid
        id2 = str(uuid.uuid4())

        resp = self.top.del_node(id2)

        print(resp)

    def test_get_top_node(self):

        node1 = self.top.set_node("1000000000000001", "agent.1000000000000001", "MX")
        self.assertIsNotNone(node1)

        print("test_set_top_link => {l}".format(l=self.top.get_node(node1[1])))

    def test_get_top_nodes(self):
        node1 = self.top.set_node("1000000000000001", "agent.1000000000000001", "MX")
        node2 = self.top.set_node("1000000000000002", "agent.1000000000000001", "BR")



        print("test_set_top_link => {l}".format(l=self.top.get_nodes()))

    def test_set_top_link(self):
        node1 = self.top.set_node("1000000000000001", "agent.1000000000000001", "MX")
        node2 = self.top.set_node("1000000000000002", "agent.1000000000000001", "BR")

        link1 = self.top.set_link(node1, node2, "1", "1", tunnel=None, key=None)

        print("test_set_top_link => {l}".format(l=link1))

    def test_get_shortest_path(self):
        _, node1 = self.top.set_node("1000000000000001", "agent.1000000000000001", "MX")
        _, node2 = self.top.set_node("1000000000000002", "agent.1000000000000001", "BR")

        print("test_get_shortest_path => {l}".format(l=self.top.get_nodes()))
        #_,link1 = self.top.set_link(node1, node2, "1", "1", tunnel=None, key=None)
        #print("test_get_shortest_path => {l}".format(l=self.top.get_nodes()))
        #print("test_get_shortest_path => {l}".format(l=link1))

        #print("test_get_shortest_path => {l}".format(l=self.top.get_nodes()))
        print("test_get_shortest_path => {l}".format(l=self.top.get_links()))

        path = self.top.get_shortest_path(node1, node2)

        print("test_get_shortest_path => {l}".format(l=path))