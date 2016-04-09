import unittest
import mock

from pyhpecw7.features.install_os import InstallOs
from base_feature_test import BaseFeatureCase


class InstallOsTestCase(BaseFeatureCase):

    @mock.patch('pyhpecw7.comware.HPCOM7')
    def setUp(self, mock_device):
        self.device = mock_device
        self.ios = InstallOs(self.device)

    def test_get_config(self):
        expected_get, get_reply = self.xml_get_and_reply('install_os')
        self.device.get.return_value = get_reply

        expected = {'current': {'boot': '5930-cmw710-boot-e2415.bin', 'system': '5930-cmw710-system-e2415.bin'}, 'startup-primary': {'boot': '5930-cmw710-boot-e2415.bin', 'system': '5930-cmw710-system-e2415.bin'}}

        result = self.ios.get_config()

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    def test_build_ipe(self):
        expected_call = self.read_action_xml('install_os_ipe')
        result = self.ios.build('ipe', ipe='ipe_name', delete_ipe=True)
        self.assert_action_request(expected_call)

        result = self.ios.build('ipe', ipe='ipe_name', delete_ipe=True, stage=True)
        self.assert_stage_request(expected_call, 'action')

    def test_build_boot_sys(self):
        expected_call = self.read_action_xml('install_os_bootsys')
        result = self.ios.build('bootsys', boot='boot_image', system='sys_image')
        self.assert_action_request(expected_call)

        result = self.ios.build('bootsys', boot='boot_image', system='sys_image', stage=True)
        self.assert_stage_request(expected_call, 'action')


if __name__ == "__main__":
    unittest.main()