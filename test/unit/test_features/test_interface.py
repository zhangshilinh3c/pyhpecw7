import unittest
import mock

from pyhpecw7.features.interface import Interface
from pyhpecw7.features.errors import InterfaceParamsError, InterfaceAbsentError, InterfaceTypeError

from base_feature_test import BaseFeatureCase

IFACE_INDEX = '11'
LOGICAL_IFACE = 'LoopBack30'
ETH_IFACE = 'FortyGigE1/0/3'


class InterfaceTestCase(BaseFeatureCase):

    @mock.patch('pyhpecw7.comware.HPCOM7')
    @mock.patch.object(Interface, '_get_iface_index')
    @mock.patch.object(Interface, '_is_ethernet_is_routed')
    def setUp(self, mock_is_eth, mock_get_index, mock_device):
        self.device = mock_device

        mock_get_index.return_value = IFACE_INDEX

        mock_is_eth.return_value = True, False
        self.eth_iface = Interface(self.device, ETH_IFACE)

        mock_is_eth.return_value = False, True
        self.lo_iface = Interface(self.device, LOGICAL_IFACE)

    def test_init(self):
        self.assertTrue(self.eth_iface.is_ethernet)
        self.assertFalse(self.eth_iface.is_routed)

        self.assertFalse(self.lo_iface.is_ethernet)
        self.assertTrue(self.lo_iface.is_routed)

        self.assertEqual(self.eth_iface.iface_index, IFACE_INDEX)
        self.assertEqual(self.lo_iface.iface_index, IFACE_INDEX)

        self.assertEqual(self.eth_iface.iface_type, 'FortyGigE')
        self.assertEqual(self.lo_iface.iface_type, 'LoopBack')

    def test_get_index(self):
        expected_get, get_reply = self.xml_get_and_reply('interface_index')
        self.device.get.return_value = get_reply

        expected = '9'
        result = self.eth_iface._get_iface_index()

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    def test_is_eth_is_routed(self):
        expected_get, get_reply = self.xml_get_and_reply('interface_is_eth')
        self.device.get.return_value = get_reply

        expected = True, True
        result = self.eth_iface._is_ethernet_is_routed()

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    def test_get_defaults(self):
        eth_defaults = self.eth_iface.get_default_config()
        lo_defaults = self.lo_iface.get_default_config()

        eth_expected = dict(description=ETH_IFACE + ' Interface', admin='up', speed='auto', duplex='auto', type='bridged')
        lo_expected = dict(description=LOGICAL_IFACE + ' Interface', admin='up', type='routed')

        self.assertEqual(eth_defaults, eth_expected)
        self.assertEqual(lo_defaults, lo_expected)

    def test_param_check(self):
        with self.assertRaises(InterfaceParamsError):
            self.lo_iface.param_check(speed='1000')

        self.eth_iface.iface_exists = False
        with self.assertRaises(InterfaceAbsentError):
            self.eth_iface.param_check(admin='up')

        self.eth_iface.iface_type = None
        with self.assertRaises(InterfaceTypeError):
            self.eth_iface.param_check(admin='up')

    def test_get_config(self):
        expected_get, get_reply = self.xml_get_and_reply('interface')
        self.device.get.return_value = get_reply

        expected = {'admin': 'up', 'duplex': 'auto', 'speed': 'auto', 'description': 'FortyGigE1/0/3 Interface', 'type': 'routed'}

        iface = self.eth_iface.get_config()

        self.assertEqual(iface, expected)
        self.assert_get_request(expected_get)

    def test_logical_iface(self):
        expected = self.read_action_xml('interface_logical')

        self.lo_iface._logical_iface()
        self.assert_action_request(expected)

        self.lo_iface._logical_iface(stage=True)
        self.assert_stage_request(expected, 'action')

    def test_logical_iface_remove(self):
        expected = self.read_action_xml('interface_logical_remove')
        self.lo_iface._logical_iface(remove=True)
        self.assert_action_request(expected)

    def test_build_config_default(self):
        expected = self.read_action_xml('interface_default')

        self.eth_iface._build_config('default', admin='up', duplex='half')
        self.assert_action_request(expected)

        self.eth_iface._build_config('default', stage=True, admin='up', duplex='half')
        self.assert_stage_request(expected, 'action')

    def test_build_config_present(self):
        expected = self.read_config_xml('interface')

        self.eth_iface._build_config('present', admin='up', duplex='half')
        self.assert_config_request(expected)

        self.eth_iface._build_config('present', stage=True, admin='up', duplex='half')
        self.assert_stage_request(expected, 'edit_config')

    def test_build_config_remove(self):
        expected = self.read_action_xml('interface_default')

        self.eth_iface._build_config('absent', admin='up', duplex='half')
        self.assert_action_request(expected)

        self.eth_iface._build_config('absent', stage=True, admin='up', duplex='half')
        self.assert_stage_request(expected, 'action')

    @mock.patch.object(Interface, '_logical_iface')
    def test_remove(self, mock_logical):
        self.lo_iface.remove_logical()
        mock_logical.assert_called_with(remove=True, stage=False)

        self.lo_iface.remove_logical(stage=True)
        mock_logical.assert_called_with(remove=True, stage=True)

    @mock.patch.object(Interface, '_logical_iface')
    def test_create(self, mock_logical):
        self.lo_iface.create_logical()
        mock_logical.assert_called_with(stage=False)

        self.lo_iface.create_logical(stage=True)
        mock_logical.assert_called_with(stage=True)

    @mock.patch.object(Interface, '_build_config')
    def test_build(self, mock_build):
        self.eth_iface.build(admin='up')
        mock_build.assert_called_with(state='present', stage=False, admin='up')

        self.eth_iface.build(admin='up', stage=True)
        mock_build.assert_called_with(state='present', stage=True, admin='up')

    @mock.patch.object(Interface, '_build_config')
    def test_default(self, mock_build):
        self.eth_iface.default()
        mock_build.assert_called_with(state='default', stage=False)

        self.eth_iface.default(stage=True)
        mock_build.assert_called_with(state='default', stage=True)

if __name__ == '__main__':
    unittest.main()
