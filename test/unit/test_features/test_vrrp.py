import unittest
import mock

from pyhpecw7.features.vrrp import VRRP
from base_feature_test import BaseFeatureCase

IFACE_NAME = 'vlan100'
VRID = '100'

class VRRPTestCase(BaseFeatureCase):

    @mock.patch('pyhpecw7.comware.HPCOM7')
    def setUp(self, mock_device):
        self.device = mock_device
        self.vrrp = VRRP(self.device, IFACE_NAME, VRID)

    def test_get_groups(self):
        expected_cmd = 'display vrrp interface vlan100 verbose'
        RAW_OUT = """IPv4 Virtual Router Information:
 Running mode      : Standard
 Total number of virtual routers on interface Vlan-interface100 : 1
   Interface Vlan-interface100
     VRID           : 100                 Adver Timer  : 100
     Admin Status   : Up                  State        : Initialize
     Config Pri     : 100                 Running Pri  : 100
     Preempt Mode   : Yes                 Delay Time   : 0
     Auth Type      : None
     Virtual IP     : 100.100.100.1
     Master IP      : 0.0.0.0
"""
        self.device.cli_display.return_value = RAW_OUT

        result = self.vrrp.get_vrrp_groups()
        expected = ['100']

        self.assertEqual(result, expected)
        self.device.cli_display.assert_called_with(expected_cmd)

    def test_get_auth(self):
        expected_cmd = 'display current-configuration interface vlan100 | inc "vrid 100 auth"'
        RAW_OUT = """<HP1>display current-configuration interface vlan100 | inc "vrid 100 auth"
 vrrp vrid 100 authentication-mode simple cipher $c$3$ePQsjr4juyIoqhrNpWXUhRx0JQr220UaQj8=

"""
        self.device.cli_display.return_value = RAW_OUT

        result = self.vrrp.get_auth_type()
        expected = {'key_type': 'cipher', 'auth_mode': 'simple', 'key': '$c$3$ePQsjr4juyIoqhrNpWXUhRx0JQr220UaQj8='}

        self.assertEqual(result, expected)
        self.device.cli_display.assert_called_with(expected_cmd)

    def test_remove(self):
        expected_cmds = ['interface vlan100', 'undo vrrp vrid 100', '\n']

        result = self.vrrp.remove()
        self.device.cli_config.assert_called_with(expected_cmds)
        self.assertEqual(result, self.device.cli_config.return_value)

        result = self.vrrp.remove(stage=True)
        self.device.stage_config.assert_called_with(expected_cmds, 'cli_config')
        self.assertEqual(result, self.device.stage_config.return_value)

    def test_shutdown(self):
        expected_cmds = ['interface vlan100', 'vrrp vrid 100 shutdown', '\n']

        result = self.vrrp.shutdown()
        self.device.cli_config.assert_called_with(expected_cmds)
        self.assertEqual(result, self.device.cli_config.return_value)

        result = self.vrrp.shutdown(stage=True)
        self.device.stage_config.assert_called_with(expected_cmds, 'cli_config')
        self.assertEqual(result, self.device.stage_config.return_value)

    def test_undoshutdown(self):
        expected_cmds = ['interface vlan100', 'undo vrrp vrid 100 shutdown', '\n']

        result = self.vrrp.undoshutdown()
        self.device.cli_config.assert_called_with(expected_cmds)
        self.assertEqual(result, self.device.cli_config.return_value)

        result = self.vrrp.undoshutdown(stage=True)
        self.device.stage_config.assert_called_with(expected_cmds, 'cli_config')
        self.assertEqual(result, self.device.stage_config.return_value)

    @mock.patch.object(VRRP, 'get_auth_type')
    @mock.patch.object(VRRP, 'get_vrrp_groups')
    def test_get_config(self, mock_groups, mock_auth):
        mock_auth.return_value = {'key_type': 'cipher', 'auth_mode': 'simple', 'key': '$c$3$TMGInQzbelfMG2TrL1ESE+mkxEWfT+UbkOw='}
        mock_groups.return_value = ['100']

        self.vrrp._existing_all = [{'key_type': 'cipher', 'admin': 'Up', 'vrid': '100', 'vip': '100.100.100.1', 'auth_mode': 'simple', 'priority': '100', 'preempt': 'no', 'key': '$c$3$TMGInQzbelfMG2TrL1ESE+mkxEWfT+UbkOw='}]

        expected = {'key_type': 'cipher', 'admin': 'Up', 'vrid': '100', 'vip': '100.100.100.1', 'auth_mode': 'simple', 'priority': '100', 'preempt': 'no', 'key': '$c$3$TMGInQzbelfMG2TrL1ESE+mkxEWfT+UbkOw='}

        result = self.vrrp.get_config()
        self.assertEqual(result, expected)

    def test_build(self):
        kwargs = dict(vip='100', auth_mode='md5', key_type='plain', key='secret', priority='10', preempt='yes')
        expected_cmds = ['interface vlan100', 'vrrp vrid 100 virtual-ip 100', 'vrrp vrid 100 priority 10', 'vrrp vrid 100 preempt-mode', 'vrrp vrid 100 authentication-mode md5 plain secret', '\n']

        result = self.vrrp.build(**kwargs)
        self.device.cli_config.assert_called_with(expected_cmds)
        self.assertEqual(result, self.device.cli_config.return_value)

        result = self.vrrp.build(stage=True, **kwargs)
        self.device.stage_config.assert_called_with(expected_cmds, 'cli_config')
        self.assertEqual(result, self.device.stage_config.return_value)






if __name__ == '__main__':
    unittest.main()