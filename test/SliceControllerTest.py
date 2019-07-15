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
