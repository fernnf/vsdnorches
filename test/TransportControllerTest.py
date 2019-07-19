import unittest
from SliceTopology import TopologyDAO
import uuid


class TransportControllerTest(unittest.TestCase):

    def setUp(self):
        self.tt = TopologyDAO(label ="transport")

        self.nid1 = self.tt.set_node(datapath_id = "0123456789abcdef",
                                     label = "MX",
                                     prefix_uri = "vsdnagent.0123456789abcdef")

        self.nid2 = self.tt.set_node(datapath_id = "abcdef0123456789",
                                     label = "BR",
                                     prefix_uri = "vsdnagent.abcdef0123456789")

        self.lid1 = self.tt.set_link(self.nid1, self.nid2, 1, 1)

    def tearDown(self):
        self.tt = None

    def test_get_label(self):
        self.assertEqual(self.tt.get_label(), "transport")

    def test_set_label(self):
        self.tt.set_label("Transport2")
        self.assertEqual(self.tt.get_label(), "Transport2")

    def test_set_node(self):
        # self.assertIsNotNone(ret, msg = "{i}".format(i = ret))
        pass

    def test_get_nodes(self):
        nodes = self.tt.get_nodes()
        print(len(nodes))
        self.assertGreater(len(nodes), 0)

    def test_get_node(self):
        nodes = self.tt.get_nodes()
        id, _ = nodes[0]
        ret = self.tt.get_node(id)

        self.assertIsNotNone(ret)

    def test_get_virt_nodes(self):
        node = self.tt.get_node(self.nid1)
        #print(node)

        node[1]["virt_nodes"].append(str(uuid.uuid4()))

        #print(node)

       # print(self.tt.get_virt_nodes(self.nid1))

    def test_get_topology(self):
        json = self.tt.get_topology()

        import pprint

        pprint.pprint(json)

    def test_get_link(self):
        #print(self.tt.get_links())
        pass

    def test_del_link(self):

        print(self.tt.get_links())
        self.tt.del_link(self.lid1)
        print(self.tt.get_links())
