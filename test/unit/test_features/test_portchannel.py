import unittest
import mock

from pyhpecw7.features.portchannel import Portchannel, InvalidPortType, AggregationGroupError
from base_feature_test import BaseFeatureCase

R_GROUP_ID = '101'
B_GROUP_ID = '100'

class PortChannelTestCase(BaseFeatureCase):

    @mock.patch('pyhpecw7.comware.HPCOM7')
    def setUp(self,  mock_device):
        self.device = mock_device
        self.rpc = Portchannel(self.device, R_GROUP_ID, 'routed')
        self.bpc = Portchannel(self.device, B_GROUP_ID, 'bridged')

    def test_init(self):
        self.assertEqual(self.rpc.pc_type, 'routed')
        self.assertEqual(self.bpc.pc_type, 'bridged')


    def test_get_portchannels(self):
        expected_get, get_reply = self.xml_get_and_reply('portchannel_list')
        self.device.get.return_value = get_reply

        expected = ['3', '100']

        result = self.bpc.get_portchannels()

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    @mock.patch.object(Portchannel, 'get_interface_from_index')
    @mock.patch.object(Portchannel, 'get_lacp_mode_by_name')
    def test_get_config(self, mock_lacp_mode, mock_iface_from_index):
        mock_lacp_mode.return_value = 'active'

        iface_list = ['FortyGigE1/0/2', 'FortyGigE1/0/1']
        def mock_iface_gen(self):
            return iface_list.pop()

        mock_iface_from_index.side_effect = mock_iface_gen

        expected_get, get_reply = self.xml_get_and_reply('portchannel')
        self.device.get.return_value = get_reply

        expected = {
            'min_ports': None,
            'max_ports': None,
            'lacp_modes_by_interface': [
                {
                    'interface': 'FortyGigE1/0/1',
                    'lacp_mode': 'active'
                },
                {
                    'interface': 'FortyGigE1/0/2',
                    'lacp_mode': 'active'
                }
            ],
            'nc_groupid': '100',
            'mode': 'static',
            'members': [
                'FortyGigE1/0/1',
                'FortyGigE1/0/2'
            ],
            'lacp_edge': 'disabled',
            'pc_index': '33736',
            'groupid': '100'
        }

        result = self.bpc.get_config()

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    @mock.patch.object(Portchannel, 'get_interface_from_index')
    def test_all_members(self, mock_iface_from_index):
        iface_list = ['FortyGigE1/0/2', 'FortyGigE1/0/1']
        def mock_iface_gen(self):
            return iface_list.pop()

        mock_iface_from_index.side_effect = mock_iface_gen

        expected_get, get_reply = self.xml_get_and_reply('portchannel_all_members')
        self.device.get.return_value = get_reply

        expected = ['FortyGigE1/0/1', 'FortyGigE1/0/2']
        result = self.bpc.get_all_members()

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    @mock.patch.object(Portchannel, 'get_interface_from_index')
    def test_all_members_ifindex(self, mock_iface_from_index):
        iface_list = ['FortyGigE1/0/2', 'FortyGigE1/0/1']
        def mock_iface_gen(self):
            return iface_list.pop()

        mock_iface_from_index.side_effect = mock_iface_gen

        expected_get, get_reply = self.xml_get_and_reply('portchannel_all_members')
        self.device.get.return_value = get_reply

        expected = ['1', '5']
        result = self.bpc.get_all_members(list_type='ifindex')

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    @mock.patch.object(Portchannel, 'get_interface_from_index')
    def test_all_members_asdict(self, mock_iface_from_index):
        iface_list = ['FortyGigE1/0/2', 'FortyGigE1/0/1']
        def mock_iface_gen(self):
            return iface_list.pop()

        mock_iface_from_index.side_effect = mock_iface_gen

        expected_get, get_reply = self.xml_get_and_reply('portchannel_all_members')
        self.device.get.return_value = get_reply

        expected = {'FortyGigE1/0/2': '100', 'FortyGigE1/0/1': '100'}
        result = self.bpc.get_all_members(asdict=True)

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    @mock.patch.object(Portchannel, 'get_index_from_interface')
    def test_lacp_mode_by_name_passive(self, mock_index_from_iface):
        mock_index_from_iface.return_value = '41'

        expected_get, get_reply = self.xml_get_and_reply('portchannel_lacp_mode_by_name_passive')
        self.device.get.return_value = get_reply

        expected = 'passive'
        result = self.bpc.get_lacp_mode_by_name('FortyGigE1/0/11')

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    @mock.patch.object(Portchannel, 'get_index_from_interface')
    def test_lacp_mode_by_name_active(self, mock_index_from_iface):
        mock_index_from_iface.return_value = '1'

        expected_get, get_reply = self.xml_get_and_reply('portchannel_lacp_mode_by_name_active')
        self.device.get.return_value = get_reply

        expected = 'active'
        result = self.bpc.get_lacp_mode_by_name('FortyGigE1/0/1')

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    def test_interface_from_index(self):
        expected_get, get_reply = self.xml_get_and_reply('portchannel_interface_from_index')
        self.device.get.return_value = get_reply

        expected = 'FortyGigE1/0/11'
        result = self.bpc.get_interface_from_index('41')

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    @mock.patch('pyhpecw7.features.portchannel.Interface')
    def test_index_from_Interface(self, mock_iface):
        mock_iface.return_value.iface_index = '96'

        result = self.bpc.get_index_from_interface('FortyGigE1/0/1')
        self.assertEqual(result, '96')

        # check local caching
        mock_iface.return_value.iface_index = '1111'

        result = self.bpc.get_index_from_interface('FortyGigE1/0/1')
        self.assertEqual(result, '96')

    @mock.patch.object(Portchannel, 'get_index_from_interface')
    def test_add_lagg_member(self, mock_index_from_iface):
        mock_index_from_iface.return_value = '1'
        expected = self.read_config_xml('portchannel_lagg_member')
        result = self.bpc._add_lagg_member('FortyGigE1/0/1', lacp='active')

        self.assert_elements_equal(result, expected)

    @mock.patch.object(Portchannel, 'get_index_from_interface')
    def test_build_config(self, mock_index_from_iface):
        index_list = ['1', '5']
        def mock_index_gen(interface):
            return index_list.pop(0)

        mock_index_from_iface.side_effect = mock_index_gen

        expected_call = self.read_config_xml('portchannel_basic')
        self.bpc._build_config('present', members=['FortyGigE1/0/1', 'FortyGigE1/0/2'])

        self.assert_config_request(expected_call)

    @mock.patch.object(Portchannel, 'get_index_from_interface')
    def test_build_config_stage(self, mock_index_from_iface):
        index_list = ['1', '5']
        def mock_index_gen(interface):
            return index_list.pop(0)

        mock_index_from_iface.side_effect = mock_index_gen

        expected_call = self.read_config_xml('portchannel_basic')
        self.bpc._build_config('present', stage=True, members=['FortyGigE1/0/1', 'FortyGigE1/0/2'])

        self.assert_stage_request(expected_call, 'edit_config')

    @mock.patch.object(Portchannel, 'get_index_from_interface')
    def test_build_config_remove_members(self, mock_index_from_iface):
        index_list = ['1', '5', '9']
        def mock_index_gen(interface):
            return index_list.pop(0)

        mock_index_from_iface.side_effect = mock_index_gen

        self.bpc.members_to_remove = ['FortyGigE1/0/3']

        expected_call = self.read_config_xml('portchannel_basic_remove_members')
        self.bpc._build_config('present', members=['FortyGigE1/0/1', 'FortyGigE1/0/2'])

        self.assert_config_request(expected_call)

    @mock.patch.object(Portchannel, 'get_index_from_interface')
    def test_build_config_change_lacp(self, mock_index_from_iface):
        index_list = ['1', '5', '9']
        def mock_index_gen(interface):
            return index_list.pop(0)

        mock_index_from_iface.side_effect = mock_index_gen

        self.bpc.desired_lacp_mode = 'bridged'

        expected_call = self.read_config_xml('portchannel_change_lacp')
        self.bpc._build_config('present', members=['FortyGigE1/0/1', 'FortyGigE1/0/2'], lacp_to_change=['FortyGigE1/0/1'])

        self.assert_config_request(expected_call)

    def test_build_config_no_members(self):
        expected_call = self.read_config_xml('portchannel_no_members')
        self.bpc._build_config('present')

        self.assert_config_request(expected_call)

    def test_build_config_remove(self):
        expected_call = self.read_config_xml('portchannel_remove')
        self.bpc._build_config('absent')

        self.assert_config_request(expected_call)

    def test_build_config_min_max(self):
        expected_xml_call = self.read_config_xml('portchannel_no_members')
        expected_cli_call = ['interface Bridge-Aggregation 100', 'link-aggregation selected-port minimum 2', 'link-aggregation selected-port maximum 8']

        self.bpc._build_config('present', min_ports='2', max_ports='8')

        self.assert_config_request(expected_xml_call)
        self.bpc.device.cli_config.assert_called_with(expected_cli_call)

    @mock.patch.object(Portchannel, '_build_config')
    def test_build(self, mock_build_config):
        kwargs = dict(members=['FortyGigE1/0/1', 'FortyGigE1/0/2'])
        self.bpc.build(**kwargs)
        mock_build_config.assert_called_with(state='present', stage=False, **kwargs)

    @mock.patch.object(Portchannel, '_build_config')
    def test_remove(self, mock_build_config):
        self.bpc.remove()
        mock_build_config.assert_called_with(state='absent', stage=False)

    @mock.patch('pyhpecw7.features.portchannel.Interface')
    @mock.patch.object(Portchannel, 'get_all_members')
    def test_param_check(self, mock_get_all_members, mock_iface):
        mock_iface.return_value.get_config.return_value = {'type': 'bridged'}
        mock_get_all_members.return_value = {'FortyGigE1/0/1': B_GROUP_ID}
        self.bpc.param_check(members=['FortyGigE1/0/1'])

        mock_iface.return_value.get_config.return_value = {'type': 'routed'}
        with self.assertRaises(InvalidPortType):
            self.bpc.param_check(members=['FortyGigE1/0/1'])

        mock_iface.return_value.get_config.return_value = {'type': 'bridged'}
        mock_get_all_members.return_value = {'FortyGigE1/0/1': '300'}
        with self.assertRaises(AggregationGroupError):
            self.bpc.param_check(members=['FortyGigE1/0/1'])


if __name__ == '__main__':
    unittest.main()
