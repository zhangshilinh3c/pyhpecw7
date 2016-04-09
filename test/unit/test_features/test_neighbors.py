import unittest
import mock

from pyhpecw7.features.neighbor import Neighbors
from base_feature_test import BaseFeatureCase


class NeighborTestCase(BaseFeatureCase):

    @mock.patch('pyhpecw7.comware.HPCOM7')
    def setUp(self, mock_device):
        self.device = mock_device
        self.neighbors = Neighbors(self.device)

    @mock.patch.object(Neighbors, '_get_interface_from_index')
    def test_neighbors_lldp(self, mock_index):
        mock_index.return_value = 'FortyGigE1/0/10'
        expected_get, get_reply = self.xml_get_and_reply('neighbors_lldp')
        self.device.get.return_value = get_reply

        expected = [
            {
                'local_intf': 'FortyGigE1/0/10',
                'neighbor': 'PERIMETER.cisco.com'
            }
        ]

        result = self.neighbors._get_neighbors()

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    @mock.patch.object(Neighbors, '_get_interface_from_index')
    def test_neighbors_cddp(self, mock_index):
        mock_index.return_value = 'FortyGigE1/0/10'
        expected_get, get_reply = self.xml_get_and_reply('neighbors_cdp')
        self.device.get.return_value = get_reply

        expected = []

        result = self.neighbors._get_neighbors(ntype='cdp')

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    @mock.patch.object(Neighbors, '_get_neighbors')
    def test_refresh(self, mock_get_neighbors):
        self.neighbors.refresh()

        mock_get_neighbors.assert_has_calls([mock.call(ntype='lldp'), mock.call(ntype='cdp')])
        self.assertEqual(self.neighbors.cdp, mock_get_neighbors.return_value)
        self.assertEqual(self.neighbors.lldp, mock_get_neighbors.return_value)


    def test_get_name_from_index(self):
        expected_get, get_reply = self.xml_get_and_reply('neighbors_iface')
        self.device.get.return_value = get_reply

        expected = 'FortyGigE1/0/3'

        iface = self.neighbors._get_interface_from_index('11')

        self.assertEqual(iface, expected)
        self.assert_get_request(expected_get)

if __name__ == '__main__':
    unittest.main()