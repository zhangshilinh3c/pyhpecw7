import unittest
import mock

from pyhpecw7.features.switchport import Switchport

from base_feature_test import BaseFeatureCase

IFACE_INDEX = '9'
IFACE_NAME = 'FortyGigE1/0/3'


class SwitchportTestCase(BaseFeatureCase):

    @mock.patch('pyhpecw7.comware.HPCOM7')
    @mock.patch('pyhpecw7.features.switchport.Interface')
    def setUp(self, mock_iface, mock_device):
        self.device = mock_device

        mock_iface.return_value.iface_index = IFACE_INDEX
        mock_iface.return_value.is_routed = True
        mock_iface.return_value.interface_name = IFACE_NAME

        self.switchport = Switchport(self.device, IFACE_NAME)

    def test_init(self):
        self.assertEqual(self.switchport.interface_name, IFACE_NAME)
        self.assertEqual(self.switchport.link_type, 'unknown')

    def test_get_config(self):
        expected_get, get_reply = self.xml_get_and_reply('switchport')
        self.device.get.return_value = get_reply

        expected = {'pvid': '1', 'link_type': 'access'}

        result = self.switchport.get_config()

        self.assertEqual(self.switchport.link_type, 'access')
        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    def test_get_config_none(self):
        expected_get, get_reply = self.xml_get_and_reply('switchport_none')
        self.device.get.return_value = get_reply

        expected = {}

        result = self.switchport.get_config()

        self.assertEqual(self.switchport.link_type, 'unknown')
        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    @mock.patch.object(Switchport, 'build')
    def test_default(self, mock_build):
        expected_args = {'pvid': '1', 'link_type': 'access'}
        self.switchport.default()

        mock_build.assert_called_with(stage=False, **expected_args)

    def test_convert_interface_access(self):
        expected = self.read_config_xml('switchport_convert_access')
        self.switchport.convert_interface('access')
        self.assert_config_request(expected)

        self.switchport.convert_interface('access', stage=True)
        self.assert_stage_request(expected, 'edit_config')

    def test_convert_interface_trunk(self):
        expected = self.read_config_xml('switchport_convert_trunk')
        self.switchport.convert_interface('trunk')
        self.assert_config_request(expected)

        self.switchport.convert_interface('trunk', stage=True)
        self.assert_stage_request(expected, 'edit_config')

    def test_build_access(self):
        expected = self.read_config_xml('switchport_build_access')
        self.switchport.build(link_type='access', pvid='2')
        self.assert_config_request(expected)

        self.switchport.build(stage=True, link_type='access', pvid='2')
        self.assert_stage_request(expected, 'edit_config')

    def test_build_trunk(self):
        expected = self.read_config_xml('switchport_build_trunk')
        self.switchport.build(link_type='trunk', pvid='2')
        self.assert_config_request(expected)

        self.switchport.build(stage=True, link_type='trunk', pvid='2')
        self.assert_stage_request(expected, 'edit_config')


if __name__ == '__main__':
    unittest.main()
