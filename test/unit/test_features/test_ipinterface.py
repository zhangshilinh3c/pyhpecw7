import unittest
import mock
from lxml import etree

from pyhpecw7.features.ipinterface import V4, V6, IpInterface
from pyhpecw7.features.errors import IpIfaceMissingData

from base_feature_test import BaseFeatureCase

IFACE_INDEX = '9'

class IpInterfaceTestCase(BaseFeatureCase):

    @mock.patch('pyhpecw7.comware.HPCOM7')
    @mock.patch('pyhpecw7.features.ipinterface.Interface')
    def setUp(self, mock_iface, mock_device):
        self.device = mock_device

        mock_iface.return_value.iface_index = IFACE_INDEX
        mock_iface.return_value.is_routed = True

        self.ip4interface = IpInterface(self.device, 'FortyGigE1/0/3')
        self.ip6interface = IpInterface(self.device, 'FortyGigE1/0/3', version=V6)


    def test_init(self):
        self.assertEqual(self.ip4interface.is_routed, True)
        self.assertEqual(self.ip4interface.interface.iface_index, IFACE_INDEX)
        self.assertEqual(self.ip4interface.version, V4)

        self.assertEqual(self.ip6interface.is_routed, True)
        self.assertEqual(self.ip6interface.interface.iface_index, IFACE_INDEX)
        self.assertEqual(self.ip6interface.version, V6)


    def test_get_config_ipv4(self):
        expected_get, get_reply = self.xml_get_and_reply('ipinterface_v4')
        self.device.get.return_value = get_reply

        expected = [{'mask': '255.255.255.0', 'addr': '192.168.3.5'}]

        ipint = self.ip4interface.get_config()

        self.assertEqual(ipint, expected)
        self.assert_get_request(expected_get)

    def test_get_config_ipv6(self):
        expected_get, get_reply = self.xml_get_and_reply('ipinterface_v6')
        self.device.get.return_value = get_reply

        expected = [{'mask': '10', 'addr': '2001:DB8::1'}, {'mask': '10', 'addr': '2001:DB8::2'}, {'mask': '10', 'addr': 'FE80::4631:92FF:FE7C:C866'}]

        ipint = self.ip6interface.get_config()

        self.assertEqual(ipint, expected)
        self.assert_get_request(expected_get)

    def test_build_config(self):
        # V4 Tests

        result = self.ip4interface._build_config('present', addr='1.2.3.4', mask='255.255.255.0')
        expected = self.read_config_xml('ipint_v4_basic')
        self.assert_elements_equal(result, expected)

        result = self.ip4interface._build_config('present', addr='1.2.3.4', mask='24')
        expected = self.read_config_xml('ipint_v4_basic')
        self.assert_elements_equal(result, expected)

        with self.assertRaises(IpIfaceMissingData):
            self.ip4interface._build_config('present', addr='1.2.3.4')

        result = self.ip4interface._build_config('absent', addr='1.2.3.4', mask='24')
        expected = self.read_config_xml('ipint_v4_absent')
        self.assert_elements_equal(result, expected)

        result = self.ip4interface._build_config('absent', addr='1.2.3.4', mask='255.255.255.0')
        expected = self.read_config_xml('ipint_v4_absent')
        self.assert_elements_equal(result, expected)


        # V6 Tests

        result = self.ip6interface._build_config('present', addr='2001:DB8::1', mask='10')
        expected = self.read_config_xml('ipint_v6_basic')
        self.assert_elements_equal(result, expected)

        result = self.ip6interface._build_config('absent', addr='2001:DB8::1', mask='10')
        expected = self.read_config_xml('ipint_v6_absent')
        self.assert_elements_equal(result, expected)


    @mock.patch.object(IpInterface, '_build_config')
    def test_build(self, mock_build_config):
        self.ip4interface.build(addr='1.2.3.4', mask='24')
        mock_build_config.assert_called_with(state='present', addr='1.2.3.4', mask='24')
        self.device.edit_config.assert_called_with(mock_build_config.return_value)

        self.ip4interface.build(stage=False, addr='1.2.3.4', mask='24')
        mock_build_config.assert_called_with(state='present', addr='1.2.3.4', mask='24')
        self.device.edit_config.assert_called_with(mock_build_config.return_value)

        self.ip4interface.build(stage=True, addr='1.2.3.4', mask='24')
        mock_build_config.assert_called_with(state='present', addr='1.2.3.4', mask='24')
        self.device.stage_config.assert_called_with(mock_build_config.return_value, 'edit_config')

    @mock.patch.object(IpInterface, '_build_config')
    def test_remove(self, mock_build_config):
        self.ip4interface.remove(addr='1.2.3.4', mask='24')
        mock_build_config.assert_called_with(state='absent', addr='1.2.3.4', mask='24')
        self.device.edit_config.assert_called_with(mock_build_config.return_value)

        self.ip4interface.remove(stage=False, addr='1.2.3.4', mask='24')
        mock_build_config.assert_called_with(state='absent', addr='1.2.3.4', mask='24')
        self.device.edit_config.assert_called_with(mock_build_config.return_value)

        self.ip4interface.remove(stage=True, addr='1.2.3.4', mask='24')
        mock_build_config.assert_called_with(state='absent', addr='1.2.3.4', mask='24')
        self.device.stage_config.assert_called_with(mock_build_config.return_value, 'edit_config')


if __name__ == '__main__':
    unittest.main()