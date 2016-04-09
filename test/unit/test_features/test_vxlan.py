import unittest
import mock

from pyhpecw7.features.vxlan import Vxlan, Tunnel, L2EthService
from base_feature_test import BaseFeatureCase

INTERFACE = 'FortyGigE1/0/2'
INSTANCE = '100'
VSI = 'VSI_VXLAN_100'
TUNNEL = '20'

class VxlanTestCase(BaseFeatureCase):

    @mock.patch('pyhpecw7.comware.HPCOM7')
    def setUp(self,  mock_device):
        self.device = mock_device
        self.l2eth = L2EthService(self.device, INTERFACE, INSTANCE, VSI)
        self.vxlan = Vxlan(self.device, INSTANCE, vsi=VSI)
        self.tunnel = Tunnel(self.device, TUNNEL)


    def test_tunnel_get_config(self):
        self.device.cli_display.return_value = """<HP1>display current-configuration interface Tunnel 20
#
interface Tunnel20 mode vxlan
 source 10.1.1.1
 destination 10.1.1.2
#
return
"""
        expected = {'dest': '10.1.1.2', 'src': '10.1.1.1', 'mode': 'vxlan'}
        result = self.tunnel.get_config()

        self.assertEqual(result, expected)

    def test_tunnel_get_config_no_tunnel(self):
        self.device.cli_display.return_value = """                                                    ^
 % Wrong parameter found at '^' position.
"""
        expected = {}
        result = self.tunnel.get_config()

        self.assertEqual(result, expected)

    def test_tunnel_get_global_source(self):
        self.device.cli_display.return_value = """<HP1>display current-configuration | inc "tunnel global source"
 tunnel global source-address 10.10.10.10

"""
        expected = '10.10.10.10'
        result = self.tunnel.get_global_source()

        self.assertEqual(result, expected)

    def test_tunnel_build_config(self):
        self.tunnel._build_config('present', src='1.1.1.1', dest='2.2.2.2', global_src='1.1.1.2')
        expected_call = ['tunnel global source-address 1.1.1.2', 'interface tunnel 20 mode vxlan', 'source 1.1.1.1', 'destination 2.2.2.2']

        self.device.cli_config.assert_called_with(expected_call)

    def test_tunnel_build_config_stage(self):
        self.tunnel._build_config('present', src='1.1.1.1', dest='2.2.2.2', global_src='1.1.1.2', stage=True)
        expected_call = ['tunnel global source-address 1.1.1.2', 'interface tunnel 20 mode vxlan', 'source 1.1.1.1', 'destination 2.2.2.2']

        self.device.stage_config.assert_called_with(expected_call, 'cli_config')

    def test_tunnel_build_config_remove(self):
        self.tunnel._build_config('absent', src='1.1.1.1', dest='2.2.2.2', global_src='1.1.1.2')
        expected_call = ['undo interface tunnel 20']

        self.device.cli_config.assert_called_with(expected_call)

    @mock.patch.object(Tunnel, '_build_config')
    def test_tunnel_remove_stage(self, mock_build_config):
        self.tunnel.remove(stage=True)
        mock_build_config.assert_called_with(state='absent', stage=True)

    @mock.patch.object(Tunnel, '_build_config')
    def test_tunnel_remove(self, mock_build_config):
        self.tunnel.remove()
        mock_build_config.assert_called_with(state='absent', stage=False)

    @mock.patch.object(Tunnel, '_build_config')
    def test_tunnel_build_stage(self, mock_build_config):
        self.tunnel.build(stage=True)
        mock_build_config.assert_called_with(state='present', stage=True)

    @mock.patch.object(Tunnel, '_build_config')
    def test_tunnel_build(self, mock_build_config):
        self.tunnel.build()
        mock_build_config.assert_called_with(state='present', stage=False)

    @mock.patch.object(Vxlan, 'get_tunnels')
    def test_get_config(self, mock_get_tunnels):
        mock_get_tunnels.return_value = ['20']

        expected_get, get_reply = self.xml_get_and_reply('vxlan')
        self.device.get.return_value = get_reply

        expected = {'vsi': 'VSI_VXLAN_100', 'tunnels': ['20'], 'vxlan': '100'}

        result = self.vxlan.get_config()

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    def test_build_vsi(self):
        result = self.vxlan._build_vsi('merge')
        expected = self.read_config_xml('vxlan_vsi')

        self.assert_elements_equal(result, expected)

    def test_build_vxlan(self):
        result = self.vxlan._build_vxlan('merge')
        expected = self.read_config_xml('vxlan')

        self.assert_elements_equal(result, expected)

    def test_build_tunnels(self):
        result = self.vxlan._build_tunnels('merge', ['20', '3'])
        expected = self.read_config_xml('vxlan_tunnels')

        self.assert_elements_equal(result, expected)

    def test_build(self):
        result = self.vxlan.build(tunnels_to_add=['20', '3'])
        expected_add_call = self.read_config_xml('vxlan_tunnels')

        self.assert_config_request(expected_add_call)

        result = self.vxlan.build(tunnels_to_remove=['4', '5'], stage=True)
        expected_rmv_call = self.read_config_xml('vxlan_tunnels_delete')

        self.assert_stage_request(expected_rmv_call, 'edit_config')
        self.assertEqual(result, True)

    def test_create(self):
        expected_vsi_call = self.read_config_xml('vxlan_vsi')
        expected_vxlan_call = self.read_config_xml('vxlan')

        result = self.vxlan.create()
        self.assert_config_request(expected_vxlan_call)

        result = self.vxlan.create(stage=True)
        self.assert_stage_request(expected_vxlan_call, 'edit_config')

    def test_remove_vsi(self):
        expected_vsi_call = self.read_config_xml('vxlan_vsi_delete')
        result = self.vxlan.remove_vsi()

        self.assert_config_request(expected_vsi_call)
        self.assertTrue(result)

        result = self.vxlan.remove_vsi(stage=True)
        self.assert_stage_request(expected_vsi_call, 'edit_config')

    def test_remove_vxlan(self):
        expected_call = self.read_config_xml('vxlan_delete')
        result = self.vxlan.remove_vxlan()

        self.assert_config_request(expected_call)
        self.assertTrue(result)

        result = self.vxlan.remove_vxlan(stage=True)
        self.assert_stage_request(expected_call, 'edit_config')

    def test_get_tunnels(self):
        expected_get, get_reply = self.xml_get_and_reply('vxlan_tunnels')
        self.device.get.return_value = get_reply

        expected = ['20']

        result = self.vxlan.get_tunnels()

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    def test_l2eth_vsi_exist(self):
        expected_get, get_reply = self.xml_get_and_reply('l2eth_vsi_exist')
        self.device.get.return_value = get_reply

        expected = {'vsi': 'VSI_VXLAN_100'}

        result = self.l2eth.vsi_exist()

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    @mock.patch.object(L2EthService, '_index_from_interface')
    def test_l2eth_get_vsi_map(self, mock_index_from_interface):
        mock_index_from_interface.return_value = '125'

        expected_get, get_reply = self.xml_get_and_reply('l2eth_vsi_map')
        self.device.get.return_value = get_reply

        expected = {'vsi': 'VSI_VXLAN_100', 'access_mode': 'ethernet', 'index': '125', 'instance': '100'}

        result = self.l2eth.get_vsi_map()

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    @mock.patch.object(L2EthService, '_index_from_interface')
    @mock.patch.object(L2EthService, '_get_interface_from_index')
    def test_l2eth_get_vsi_encap(self, mock_iface_from_index, mock_index_from_interface):
        mock_iface_from_index.return_value = 'FortyGigE1/0/32'
        mock_index_from_interface.return_value = '125'

        expected_get, get_reply = self.xml_get_and_reply('l2eth_vsi_encap')
        self.device.get.return_value = get_reply

        expected = {'interface': 'FortyGigE1/0/32', 'index': '125', 'encap': 'tagged', 'instance': '100'}

        result = self.l2eth.get_vsi_encap()

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)


    @mock.patch.object(L2EthService, '_index_from_interface')
    def test_l2eth_build_encap_default(self, mock_index_from_interface):
        mock_index_from_interface.return_value = '125'
        expected_call = self.read_config_xml('l2eth_build_encap_default')

        self.l2eth._build_encap('merge', encap='default')
        self.assert_config_request(expected_call)

        self.l2eth._build_encap('merge', stage=True, encap='default')
        self.assert_stage_request(expected_call, 'edit_config')

    @mock.patch.object(L2EthService, '_index_from_interface')
    def test_l2eth_build_encap_tagged(self, mock_index_from_interface):
        mock_index_from_interface.return_value = '125'
        expected_call = self.read_config_xml('l2eth_build_encap_tagged')

        self.l2eth._build_encap('merge', encap='tagged')
        self.assert_config_request(expected_call)

        self.l2eth._build_encap('merge', stage=True, encap='tagged')
        self.assert_stage_request(expected_call, 'edit_config')

    @mock.patch.object(L2EthService, '_index_from_interface')
    def test_l2eth_build_encap_only_tagged(self, mock_index_from_interface):
        mock_index_from_interface.return_value = '125'
        expected_call = self.read_config_xml('l2eth_build_encap_only_tagged')

        self.l2eth._build_encap('merge', encap='only-tagged', vlanid='10')
        self.assert_config_request(expected_call)

        self.l2eth._build_encap('merge', stage=True, encap='only-tagged', vlanid='10')
        self.assert_stage_request(expected_call, 'edit_config')

    @mock.patch.object(L2EthService, '_index_from_interface')
    def test_l2eth_build_encap_only_delete(self, mock_index_from_interface):
        mock_index_from_interface.return_value = '125'
        expected_call = self.read_config_xml('l2eth_build_encap_delete')

        self.l2eth._build_encap('delete')
        self.assert_config_request(expected_call)

        self.l2eth._build_encap('delete', stage=True)
        self.assert_stage_request(expected_call, 'edit_config')

    def test_l2eth_build_xconnect(self):
        expected_call = self.read_config_xml('l2eth_build_xconnect')

        self.l2eth._build_xconnect('merge', '125', access_mode='ethernet')
        self.assert_config_request(expected_call)

        self.l2eth._build_xconnect('merge', '125', stage=True, access_mode='ethernet')
        self.assert_stage_request(expected_call, 'edit_config')

    @mock.patch.object(L2EthService, '_build_encap')
    @mock.patch.object(L2EthService, '_build_xconnect')
    def test_l2eth_build_config(self, mock_xconnect, mock_encap):
        self.l2eth.jindex = '999'

        self.l2eth._build_config('present', encap='tagged', access_mode='vlan')
        mock_encap.assert_called_with('merge', access_mode='vlan', encap='tagged', stage=False)
        mock_xconnect.assert_called_with('merge', '999', access_mode='vlan', encap='tagged', stage=False)

    @mock.patch.object(L2EthService, '_build_encap')
    @mock.patch.object(L2EthService, '_build_xconnect')
    def test_l2eth_build_config_absent(self, mock_xconnect, mock_encap):
        self.l2eth.jindex = '999'

        self.l2eth._build_config('absent', encap='tagged', access_mode='vlan')
        mock_encap.assert_called_with('delete', access_mode='vlan', encap='tagged', stage=False)
        mock_xconnect.assert_not_called()

    @mock.patch.object(L2EthService, '_build_config')
    def test_l2eth_build(self, mock_build_config):
        self.l2eth.build(vsi='abc', encap='tagged', access_mode='ethernet')
        mock_build_config.assert_called_with(access_mode='ethernet', encap='tagged', stage=False, state='present', vsi='abc')

    @mock.patch.object(L2EthService, '_build_config')
    def test_l2eth_remove(self, mock_build_config):
        self.l2eth.remove()
        mock_build_config.assert_called_with(stage=False, state='absent')

    def test_l2eth_get_interface_from_index(self):
        expected_get, get_reply = self.xml_get_and_reply('l2eth_get_interface_from_index')
        self.device.get.return_value = get_reply

        expected = 'FortyGigE1/0/32'

        result = self.l2eth._get_interface_from_index('125')

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)


if __name__ == '__main__':
    unittest.main()
