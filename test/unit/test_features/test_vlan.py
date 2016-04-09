import unittest
import mock
from lxml import etree

from ncclient.operations.retrieve import GetReply
from pyhpecw7.features.vlan import Vlan
from pyhpecw7.features.errors import VlanIDError, LengthOfStringError

from base_feature_test import BaseFeatureCase

class VlanTestCase(BaseFeatureCase):

    @mock.patch('pyhpecw7.comware.HPCOM7')
    def setUp(self, mock_device):
        self.device = mock_device
        self.vlan = Vlan(self.device, vlanid='77')

    def test_get_vlan_list(self):
        expected_get, get_reply = self.xml_get_and_reply('vlan_list')
        self.device.get.return_value = get_reply

        expected = ['1', '20', '77']

        vlan_list = self.vlan.get_vlan_list()

        self.assertEqual(vlan_list, expected)
        self.assert_get_request(expected_get)

    def test_get_config(self):
        expected_get, get_reply = self.xml_get_and_reply('vlan')
        self.device.get.return_value = get_reply

        expected = {'name': 'hello', 'vlanid': '77', 'descr': 'goodbye'}

        vlan = self.vlan.get_config()

        self.assertEqual(vlan, expected)
        self.assert_get_request(expected_get)

    def test_build_config(self):
        result = self.vlan._build_config(state='present')
        expected = self.read_config_xml('vlan')
        self.assert_elements_equal(result, expected)

        result = self.vlan._build_config(state='present', name='hello')
        expected = self.read_config_xml('vlan_name')
        self.assert_elements_equal(result, expected)

        result = self.vlan._build_config('present', name='hello', descr='goodbye')
        expected = self.read_config_xml('vlan_name_descr')
        self.assert_elements_equal(result, expected)

        result = self.vlan._build_config('absent')
        expected = self.read_config_xml('vlan_absent')
        self.assert_elements_equal(result, expected)

    def test_param_check(self):
        with self.assertRaises(LengthOfStringError):
            self.vlan.param_check(name=('a' * 255))

        with self.assertRaises(LengthOfStringError):
            self.vlan.param_check(descr=('b' * 255))

    @mock.patch.object(Vlan, '_build_config')
    def test_build(self, mock_build_config):
        self.vlan.build(name='a', descr='b')
        mock_build_config.assert_called_with(state='present', name='a', descr='b')
        self.device.edit_config.assert_called_with(mock_build_config.return_value)

        self.vlan.build(stage=False, name='a', descr='b')
        mock_build_config.assert_called_with(state='present', name='a', descr='b')
        self.device.edit_config.assert_called_with(mock_build_config.return_value)

        self.vlan.build(stage=True, name='a', descr='b')
        mock_build_config.assert_called_with(state='present', name='a', descr='b')
        self.device.stage_config.assert_called_with(mock_build_config.return_value, 'edit_config')

    @mock.patch.object(Vlan, '_build_config')
    def test_remove(self, mock_build_config):
        self.vlan.remove()
        mock_build_config.assert_called_with(state='absent')
        self.device.edit_config.assert_called_with(mock_build_config.return_value)

        self.vlan.remove(stage=False)
        mock_build_config.assert_called_with(state='absent')
        self.device.edit_config.assert_called_with(mock_build_config.return_value)

        self.vlan.remove(stage=True)
        mock_build_config.assert_called_with(state='absent')
        self.device.stage_config.assert_called_with(mock_build_config.return_value, 'edit_config')


if __name__ == '__main__':
    unittest.main()