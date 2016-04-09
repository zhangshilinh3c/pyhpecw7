import unittest
import mock

from pyhpecw7.features.l2vpn import L2VPN
from base_feature_test import BaseFeatureCase

class L2VPNTestCase(BaseFeatureCase):

    @mock.patch('pyhpecw7.comware.HPCOM7')
    def setUp(self, mock_device):
        self.device = mock_device
        self.l2vpn = L2VPN(self.device)

    def test_get_config(self):
        expected_get, get_reply = self.xml_get_and_reply('l2vpn')
        self.device.get.return_value = get_reply

        expected = 'enabled'

        result = self.l2vpn.get_config()

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    def test_build_config(self):
        expected = self.read_config_xml('l2vpn_enabled')
        result = self.l2vpn._build_config('enabled')
        self.elements_are_equal(result, expected)

        expected = self.read_config_xml('l2vpn_disabled')
        result = self.l2vpn._build_config('disabled')
        self.elements_are_equal(result, expected)

    @mock.patch.object(L2VPN, '_build_config')
    def test_enable(self, mock_build_config):
        mock_build_config.return_value = self.read_config_xml('l2vpn_enabled')

        self.l2vpn.enable()
        mock_build_config.assert_called_with(state='enabled')
        self.assert_config_request(mock_build_config.return_value)

        self.l2vpn.enable(stage=True)
        mock_build_config.assert_called_with(state='enabled')
        self.assert_stage_request(mock_build_config.return_value, 'edit_config')

    @mock.patch.object(L2VPN, '_build_config')
    def test_disable(self, mock_build_config):
        mock_build_config.return_value = self.read_config_xml('l2vpn_disabled')

        self.l2vpn.disable()
        mock_build_config.assert_called_with(state='disabled')
        self.assert_config_request(mock_build_config.return_value)

        self.l2vpn.disable(stage=True)
        mock_build_config.assert_called_with(state='disabled')
        self.assert_stage_request(mock_build_config.return_value, 'edit_config')


if __name__ == "__main__":
    unittest.main()