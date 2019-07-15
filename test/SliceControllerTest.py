import unittest
from SliceTopology import SliceTopologyController

class SliceControllerTest(unittest.TestCase):

    def setUp(self):
        self.st = SliceTopologyController(tenant_id = "1", label = "slice home", controller = "tcp:127.0.0.1:6654")

    def tearDown(self) -> None:
        self.st = None

    def test_get_slice_id(self):
        ret = self.st.get_slice_id()
        print(ret)
        self.assertIsNotNone(ret)

    def test_get_slice_status(self):
        ret = self.st.get_slice_status()
        print(ret)

    def test_set_slice_status(self):
        self.assertEqual(self.st.get_slice_status(), "CREATED")
        self.st.set_slice_status(2)
        print(self.st.get_slice_status())
        self.assertEqual(self.st.get_slice_status(), "RUNNING")

    def test_get_slice_tenant_id(self):
        self.assertEqual(self.st.get_slice_tenant_id(), "1")

    def test_set_slice_tenant_id(self):
        self.assertEqual(self.st.get_slice_tenant_id(), "1")
        self.st.set_slice_tenant_id("2")
        self.assertEqual(self.st.get_slice_tenant_id(), "2")

    def test_get_slice_label(self):
        self.assertEqual(self.st.get_slice_label(), "slice home")

    def test_set_slice_label(self):
        self.assertEqual(self.st.get_slice_label(), "slice home")
        self.st.set_slice_label("slice corporation")
        self.assertEqual(self.st.get_slice_label(), "slice corporation")

    def test_get_slice_controller(self):
        self.assertEqual(self.st.get_slice_controller(), "tcp:127.0.0.1:6654")

    def test_set_slice_controller(self):
        self.assertEqual(self.st.get_slice_controller(), "tcp:127.0.0.1:6654")
        self.st.set_slice_controller("tcp:127.0.0.1:6633")
        self.assertEqual(self.st.get_slice_controller(), "tcp:127.0.0.1:6633")

    def test_set_slice_node(self):
        import uuid
        physical_id=str(uuid.uuid4())
        virtual_id = self.st.set_slice_node(physical_id)
        self.assertIsNotNone(virtual_id)
        print(virtual_id)

    def test_get_slice_node(self):
        import uuid
        physical_id = str(uuid.uuid4())
        virtual_id = self.st.set_slice_node(physical_id)

        node = self.st.get_slice_node(virtual_id)

        self.assertIsNotNone(node)
        import pprint
        pprint.pprint(node)

    def test_del_slice_node(self):
        import uuid
        physical_id = str(uuid.uuid4())
        virtual_id = self.st.set_slice_node(physical_id)

        node = self.st.get_slice_node(virtual_id)

        import pprint
        pprint.pprint(node)

        self.st.del_slice_node(virtual_id)
