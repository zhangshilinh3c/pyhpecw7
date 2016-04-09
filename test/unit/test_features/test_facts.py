import unittest
import mock
import collections

from ncclient.operations.retrieve import GetReply
from pyhpecw7.features.facts import Facts

from base_feature_test import BaseFeatureCase

class FactsTestCase(BaseFeatureCase):

    @mock.patch('pyhpecw7.comware.HPCOM7')
    def setUp(self, mock_device):
        self.device = mock_device
        self.facts = Facts(self.device)

    def test_get_interface_list(self):
        expected_get, get_reply = self.xml_get_and_reply('interface_list')
        self.device.get.return_value = get_reply

        iface_list = self.facts._get_interface_list()

        self.assertIn('interface_list', iface_list)
        self.assertIn('FortyGigE1/0/3', iface_list['interface_list'])

        self.assert_get_request(expected_get)

    def test_get_inventory(self):
        expected_get, get_reply = self.xml_get_and_reply('inventory')
        self.device.get.return_value = get_reply

        expected = {
            'vendor': 'hp',
            'serial_number': 'CN43G9800T',
            'model': 'HP FF 5930-32QSFP+ Switch',
            'os': '7.1.045 ESS 2415'
        }

        inventory = self.facts._get_inventory()

        self.assertEqual(inventory, expected)
        self.assert_get_request(expected_get)

    def test_get_base(self):
        expected_get, get_reply = self.xml_get_and_reply('facts_base')
        self.device.get.return_value = get_reply

        expected = {
            'uptime': '2d 3hr 51min 45sec',
            'hostname': 'HP1',
            'localtime': '2011-01-03T03:50:39'
        }

        facts_base = self.facts._get_base()

        self.assertEqual(facts_base, expected)
        self.assert_get_request(expected_get)

    def test_get_uptime(self):
        a = self.facts._get_uptime(0)
        self.assertEqual(a, '0d 0hr 0min 0sec')

        b = self.facts._get_uptime(1)
        self.assertEqual(b, '0d 0hr 0min 1sec')

        c = self.facts._get_uptime(60)
        self.assertEqual(c, '0d 0hr 1min 0sec')

        d = self.facts._get_uptime(61)
        self.assertEqual(d, '0d 0hr 1min 1sec')

        e = self.facts._get_uptime(3928)
        self.assertEqual(e, '0d 1hr 5min 28sec')

        f = self.facts._get_uptime(355928)
        self.assertEqual(f, '4d 2hr 52min 8sec')


    @mock.patch.object(Facts, '_get_interface_list')
    @mock.patch.object(Facts, '_get_inventory')
    @mock.patch.object(Facts, '_get_base')
    def test_facts(self, mock_base, mock_inventory, mock_iface_list):
        mock_base.return_value = {'uptime': '2d 4hr 22min 28sec', 'hostname': 'HP1', 'localtime': '2011-01-03T04:21:22'}
        mock_inventory.return_value = {'vendor': 'hp', 'serial_number': 'CN43G9800T', 'model': 'HP FF 5930-32QSFP+ Switch', 'os': '7.1.045 ESS 2415'}
        mock_iface_list.return_value = {'interface_list': ['FortyGigE1/0/1', 'FortyGigE1/0/2', 'FortyGigE1/0/3', 'FortyGigE1/0/4', 'FortyGigE1/0/5', 'FortyGigE1/0/6', 'FortyGigE1/0/7', 'FortyGigE1/0/8', 'FortyGigE1/0/9', 'FortyGigE1/0/10', 'FortyGigE1/0/11', 'FortyGigE1/0/12', 'FortyGigE1/0/13', 'FortyGigE1/0/14', 'FortyGigE1/0/15', 'FortyGigE1/0/16', 'FortyGigE1/0/17', 'FortyGigE1/0/18', 'FortyGigE1/0/19', 'FortyGigE1/0/20', 'FortyGigE1/0/21', 'FortyGigE1/0/22', 'FortyGigE1/0/23', 'FortyGigE1/0/24', 'FortyGigE1/0/25', 'FortyGigE1/0/26', 'FortyGigE1/0/27', 'FortyGigE1/0/28', 'FortyGigE1/0/29', 'FortyGigE1/0/30', 'FortyGigE1/0/31', 'FortyGigE1/0/32', 'M-GigabitEthernet0/0/0', 'NULL0', 'InLoopBack0', 'Register-Tunnel0', 'LoopBack29', 'Bridge-Aggregation100']}

        expected = collections.OrderedDict(
            [
                ('vendor', 'hp'),
                ('serial_number', 'CN43G9800T'),
                ('model', 'HP FF 5930-32QSFP+ Switch'),
                ('os', '7.1.045 ESS 2415'),
                ('uptime', '2d 4hr 22min 28sec'),
                ('hostname', 'HP1'),
                ('localtime', '2011-01-03T04:21:22'),
                ('interface_list', [ 'FortyGigE1/0/1',
                                     'FortyGigE1/0/2',
                                     'FortyGigE1/0/3',
                                     'FortyGigE1/0/4',
                                     'FortyGigE1/0/5',
                                     'FortyGigE1/0/6',
                                     'FortyGigE1/0/7',
                                     'FortyGigE1/0/8',
                                     'FortyGigE1/0/9',
                                     'FortyGigE1/0/10',
                                     'FortyGigE1/0/11',
                                     'FortyGigE1/0/12',
                                     'FortyGigE1/0/13',
                                     'FortyGigE1/0/14',
                                     'FortyGigE1/0/15',
                                     'FortyGigE1/0/16',
                                     'FortyGigE1/0/17',
                                     'FortyGigE1/0/18',
                                     'FortyGigE1/0/19',
                                     'FortyGigE1/0/20',
                                     'FortyGigE1/0/21',
                                     'FortyGigE1/0/22',
                                     'FortyGigE1/0/23',
                                     'FortyGigE1/0/24',
                                     'FortyGigE1/0/25',
                                     'FortyGigE1/0/26',
                                     'FortyGigE1/0/27',
                                     'FortyGigE1/0/28',
                                     'FortyGigE1/0/29',
                                     'FortyGigE1/0/30',
                                     'FortyGigE1/0/31',
                                     'FortyGigE1/0/32',
                                     'M-GigabitEthernet0/0/0',
                                     'NULL0',
                                     'InLoopBack0',
                                     'Register-Tunnel0',
                                     'LoopBack29',
                                     'Bridge-Aggregation100'])
            ])

        self.assertEqual(dict(self.facts.facts), dict(expected))


if __name__ == '__main__':
    unittest.main()