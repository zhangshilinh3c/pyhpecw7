import unittest
import mock

from pyhpecw7.features.irf import IrfPort, IrfMember, InterfaceAbsentError, IRFMemberDoesntExistError
from base_feature_test import BaseFeatureCase

class IrfTestCase(BaseFeatureCase):

    @mock.patch('pyhpecw7.comware.HPCOM7')
    def setUp(self, mock_device):
        self.device = mock_device
        self.irf_port = IrfPort(self.device)
        self.irf_member = IrfMember(self.device)

    @mock.patch.object(IrfPort, '_build_iface_updown')
    def test_ports_build(self, mock_iface_updown):
        expected_port_build = self.read_config_xml('irf_port_build')
        expected_activate = self.read_action_xml('irf_port_build_activate')

        expected_call_list = [
            [expected_port_build, 'edit_config'],
            ['startup.cfg', 'save'],
            [expected_activate, 'action']

        ]

        down_ifaces = ['FortyGigE1/0/2', 'FortyGigE1/0/1', 'FortyGigE1/0/3', 'FortyGigE1/0/4']
        up_ifaces = ['FortyGigE1/0/1', 'FortyGigE1/0/2', 'FortyGigE1/0/3', 'FortyGigE1/0/4']

        self.irf_port.build('1', [], [], ['FortyGigE1/0/1', 'FortyGigE1/0/2'], ['FortyGigE1/0/3', 'FortyGigE1/0/4'])

        self.assert_stage_requests_multiple(expected_call_list)
        mock_iface_updown.assert_has_calls([mock.call(down_ifaces, 'down'), mock.call(up_ifaces, 'up')])

    @mock.patch.object(IrfPort, '_build_iface_updown')
    def test_ports_build_remove(self, mock_iface_updown):
        expected_port_build = self.read_config_xml('irf_port_build_remove')
        expected_activate = self.read_action_xml('irf_port_build_activate')

        expected_call_list = [
            [expected_port_build, 'edit_config'],
            ['startup.cfg', 'save'],
            [expected_activate, 'action']

        ]

        down_ifaces = ['FortyGigE1/0/2', 'FortyGigE1/0/1', 'FortyGigE1/0/3', 'FortyGigE1/0/4']
        up_ifaces = []

        self.irf_port.build('1', ['FortyGigE1/0/1', 'FortyGigE1/0/2'], ['FortyGigE1/0/3', 'FortyGigE1/0/4'], [], [])

        self.assert_stage_requests_multiple(expected_call_list)
        mock_iface_updown.assert_has_calls([mock.call(down_ifaces, 'down'), mock.call(up_ifaces, 'up')])

    def test_ports_get_config(self):
        expected_get, get_reply = self.xml_get_and_reply('irf_ports')
        self.device.get.return_value = get_reply

        expected = {'1': {'irf_p2': ['FortyGigE1/0/3', 'FortyGigE1/0/4'], 'irf_p1': ['FortyGigE1/0/1', 'FortyGigE1/0/2']}}

        result = self.irf_port.get_config()

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    @mock.patch('pyhpecw7.features.irf.Interface')
    def test_ports_iface_updown(self, mock_interface):
        mock_iface_instance = mock_interface.return_value
        mock_iface_instance.iface_exists = True

        self.irf_port._build_iface_updown(['FortyGigE1/0/1'], 'up')
        mock_iface_instance.build.assert_called_with(admin='up', stage=True)

        mock_iface_instance.iface_exists = False
        with self.assertRaises(InterfaceAbsentError):
            self.irf_port._build_iface_updown(['FortyGigE1/0/1'], 'up')

    def test_member_get_member_config(self):
        expected_get, get_reply = self.xml_get_and_reply('irf_member_config')
        self.device.get.return_value = get_reply

        expected = {'new_member_id': '1', 'priority': '4', 'descr': 'They used to call me HP1'}

        result = self.irf_member._get_member_config('1')

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    def test_member_build_member_config(self):
        expected_call_list = [
            ['irf member 1 description From unit test', 'cli_config'],
            ['irf member 1 renumber 2', 'cli_config'],
            ['irf member 1 priority 3', 'cli_config']
        ]

        result = self.irf_member._build_member_config(member_id='1', new_member_id='2', priority='3', descr='From unit test')

        self.assert_stage_requests_multiple(expected_call_list)
        self.assertTrue(result)

    def test_member_get_domain_config(self):
        expected_get, get_reply = self.xml_get_and_reply('irf_member_domain_config')
        self.device.get.return_value = get_reply

        expected = {'domain_id': '1'}

        result = self.irf_member._get_domain_config()

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    def test_member_get_au_config(self):
        expected_get, get_reply = self.xml_get_and_reply('irf_member_au_config')
        self.device.get.return_value = get_reply

        expected = {'auto_update': 'enable'}

        result = self.irf_member._get_auto_update_config()

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)

    def test_member_build_au_domain_config(self):
        result = self.irf_member._build_auto_update_domain_config('enable', '2')
        expected_call = self.read_config_xml('irf_member_au_domain')

        self.assert_stage_request(expected_call, 'edit_config')
        self.assertTrue(result)

    def test_member_get_mad_exclude(self):
        self.device.cli_display.return_value = '<HP1>display current | inc "mad exclude interface"\r\n mad exclude interface FortyGigE1/0/9\r\n mad exclude interface FortyGigE1/0/10\r\n'
        result = self.irf_member._get_mad_exclude()

        self.device.cli_display.assert_called_with('display current | inc "mad exclude interface"')
        self.assertEqual(result, {'mad_exclude': ['FortyGigE1/0/9', 'FortyGigE1/0/10']})

    @mock.patch('pyhpecw7.features.irf.Interface')
    def test_member_build_mad_exclude(self, mock_interface):
        mock_iface_instance = mock_interface.return_value
        mock_iface_instance.iface_exists = True
        mock_iface_instance.interface_name = 'FortyGigE1/0/9'

        result = self.irf_member._build_mad_exclude(['FortyGigE1/0/9'])
        self.assert_stage_request('mad exclude interface FortyGigE1/0/9', 'cli_config')

        mock_iface_instance.iface_exists = False
        with self.assertRaises(InterfaceAbsentError):
            self.irf_member._build_mad_exclude(['FortyGigE1/0/9'])

    @mock.patch.object(IrfMember, '_get_member_config')
    @mock.patch.object(IrfMember, '_get_domain_config')
    @mock.patch.object(IrfMember, '_get_mad_exclude')
    @mock.patch.object(IrfMember, '_get_auto_update_config')
    def test_member_get_config(self, mock_au, mock_mad, mock_domain, mock_member):
        mock_member.return_value = {'a': 1}
        mock_domain.return_value = {'b': 2}
        mock_mad.return_value = {'c': 3}
        mock_au.return_value = {'d': 4}

        result = self.irf_member.get_config('1')
        expected = {'a': 1, 'b': 2, 'c': 3, 'd': 4}

        self.assertEqual(result, expected)

        mock_member.return_value = None
        with self.assertRaises(IRFMemberDoesntExistError):
            self.irf_member.get_config('1')

    @mock.patch.object(IrfMember, '_build_member_config')
    @mock.patch.object(IrfMember, '_build_auto_update_domain_config')
    @mock.patch.object(IrfMember, '_build_mad_exclude')
    def test_member_build(self, mock_mad, mock_au_domain, mock_member):
        params = dict(
            auto_update='disable',
            mad_exclude=['FortyGigE1/0/9', 'FortyGigE1/0/10'],
            member_id='1',
            new_member_id='1',
            domain_id='4',
            priority='2',
            descr='Configured from unit test.'
        )

        result = self.irf_member.build(**params)

        mock_member.assert_called_with(**params)
        mock_au_domain.assert_called_with('disable', '4')
        mock_mad.assert_called_with(['FortyGigE1/0/9', 'FortyGigE1/0/10'])

        self.assertTrue(result)

    def test_remove_mad_exclude(self):
        iface_list = ['FortyGigE1/0/9', 'FortyGigE1/0/10']
        self.irf_member.remove_mad_exclude(iface_list)

        self.assert_stage_requests_multiple(
            [
                ['undo mad exclude interface FortyGigE1/0/9', 'cli_config'],
                ['undo mad exclude interface FortyGigE1/0/10', 'cli_config'],
            ]
        )











if __name__ == "__main__":
    unittest.main()