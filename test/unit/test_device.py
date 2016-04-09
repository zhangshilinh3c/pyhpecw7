import unittest
import mock

from lxml import etree
from ncclient.operations.rpc import RPCReply

from pyhpecw7.comware import HPCOM7, NCTimeoutError, ConnectionClosedError, NCError,\
    ConnectionAuthenticationError, ConnectionSSHError, ConnectionUknownHostError,\
    ConnectionError, LockConflictError, UnlockConflictError, NcTransErrors, NcOpErrors, RPCError,\
    socket

class HPCOM7TestCase(unittest.TestCase):


    def setUp(self):
        self.device = HPCOM7(host='host', username='user', password='pass')
        self.device.connection = mock.MagicMock()
        self.device.connection.connected = True

    def test_init(self):
        self.assertEqual(self.device.host, 'host')
        self.assertEqual(self.device.username, 'user')
        self.assertEqual(self.device.password, 'pass')
        self.assertEqual(self.device.port, 830)
        self.assertEqual(self.device.timeout, 30)
        self.assertEqual(self.device.staged, [])
        self.assertEqual(self.device._locked, False)

    @mock.patch('pyhpecw7.comware.manager', autospec=True)
    def test_open(self, mock_manager):
        self.device.open()
        mock_manager.connect.assert_called_with(allow_agent=False,
                                                device_params={'name': 'hpcomware'},
                                                host='host',
                                                hostkey_verify=False,
                                                look_for_keys=False,
                                                password='pass',
                                                port=830,
                                                timeout=30,
                                                username='user')


    @mock.patch('pyhpecw7.comware.manager', autospec=True)
    def test_open_auth_error(self, mock_manager):
        mock_manager.connect.side_effect = NcTransErrors.AuthenticationError
        with self.assertRaises(ConnectionAuthenticationError):
            self.device.open()

    @mock.patch('pyhpecw7.comware.manager', autospec=True)
    def test_open_ssh_error(self, mock_manager):
        mock_manager.connect.side_effect = NcTransErrors.SSHError
        with self.assertRaises(ConnectionSSHError):
            self.device.open()

    @mock.patch('pyhpecw7.comware.manager', autospec=True)
    def test_open_dns_error(self, mock_manager):
        mock_manager.connect.side_effect = socket.gaierror
        with self.assertRaises(ConnectionUknownHostError):
            self.device.open()

    @mock.patch('pyhpecw7.comware.manager', autospec=True)
    def test_open_ncclient_extensions_error(self, mock_manager):
        mock_manager.connect.side_effect = ImportError
        with self.assertRaisesRegexp(ImportError, 'comware extensions'):
            self.device.open()

    @mock.patch('pyhpecw7.comware.manager', autospec=True)
    def test_open_generic_error(self, mock_manager):
        mock_manager.connect.side_effect = Exception
        with self.assertRaises(ConnectionError):
            self.device.open()

    @mock.patch('pyhpecw7.comware.Facts')
    def test_facts(self, mock_facts):
        mock_facts.return_value.facts = {'a': 1}

        result = self.device.facts
        self.assertEqual(result, {'a': 1})

    @mock.patch('pyhpecw7.comware.Facts')
    def test_facts_no_connection(self, mock_facts):
        self.device.connection.connected = False
        mock_facts.return_value.facts = {'a': 1}

        result = self.device.facts
        self.assertEqual(result, None)

    def test_connected(self):
        self.assertEqual(self.device.connected, True)

    def test_connected_false(self):
        self.device.connection.connected = False
        self.assertEqual(self.device.connected, False)

    def test_connected_not_opened(self):
        del self.device.connection
        self.assertEqual(self.device.connected, False)

    def test_close(self):
        self.device.close()
        self.device.connection.close_session.assert_called_with()

    def test_close_timeout_error(self):
        self.device.connection.close_session.side_effect = NcOpErrors.TimeoutExpiredError

        with self.assertRaises(NCTimeoutError):
            self.device.close()

    def test_stage_config(self):
        for cfg_type in ['edit_config', 'action', 'cli_config',
                        'cli_display', 'save', 'rollback']:
            config = etree.Element('top')
            prev_len = len(self.device.staged)
            result = self.device.stage_config(config, cfg_type)

            self.assertEqual(len(self.device.staged), prev_len + 1)
            self.assertEqual(result, True)

    def test_stage_config_error(self):
        config = etree.Element('top')
        with self.assertRaises(ValueError):
            self.device.stage_config(config, 'bad_cfg_type')

    def test_staged_to_string(self):
        config = etree.Element('top')
        self.device.stage_config(config, 'edit_config')
        self.device.stage_config('display run', 'cli_display')

        result = self.device.staged_to_string()
        self.assertEqual(result, ['<top/>', 'display run'])

    def test_execute_connection_closed(self):
        self.device.connection.connected = False
        with self.assertRaises(ConnectionClosedError):
            self.device.execute(self.device.connection.cli_display)

    def test_execute_rpc_error(self):
        self.device.connection.cli_display.side_effect = RPCError(etree.Element('error'))
        with self.assertRaises(NCError):
            self.device.execute(self.device.connection.cli_display, ['display current'])

    def test_execute_timeout_error(self):
        self.device.connection.cli_display.side_effect = NcOpErrors.TimeoutExpiredError
        with self.assertRaises(NCTimeoutError):
            self.device.execute(self.device.connection.cli_display, ['display current'])

    def test_execute_transport_error(self):
        self.device.connection.cli_display.side_effect = NcTransErrors.TransportError
        with self.assertRaises(ConnectionClosedError):
            self.device.execute(self.device.connection.cli_display, ['display current'])

    @mock.patch.object(HPCOM7, 'lock')
    @mock.patch.object(HPCOM7, 'unlock')
    def test_execute(self, mock_unlock, mock_lock):
        result = self.device.execute(self.device.connection.cli_display, ['display current'], {'b': 2})

        mock_lock.assert_called_with()
        mock_unlock.assert_called_with()
        self.device.connection.cli_display.assert_called_with('display current', b=2)
        self.assertEqual(result, self.device.connection.cli_display.return_value)

    @mock.patch.object(HPCOM7, 'edit_config')
    @mock.patch.object(HPCOM7, 'action')
    @mock.patch.object(HPCOM7, 'cli_config')
    @mock.patch.object(HPCOM7, 'cli_display')
    @mock.patch.object(HPCOM7, 'save')
    @mock.patch.object(HPCOM7, 'rollback')
    def test_execute_staged(self,
                            mock_rollback,
                            mock_save,
                            mock_cli_display,
                            mock_cli_config,
                            mock_action,
                            mock_edit_config):

        for cfg_type in ['edit_config', 'action', 'cli_config', 'cli_display', 'save', 'rollback']:
            self.device.staged.append(dict(cfg_type=cfg_type, config='config object'))

        self.device.execute_staged()

        for func_tuple in [
            (mock_edit_config, [], dict(target='running', config='config object')),
            (mock_action, ['config object'], {}),
            (mock_cli_config, ['config object'], {}),
            (mock_cli_display, ['config object'], {}),
            (mock_save, ['config object'], {}),
            (mock_rollback, ['config object'], {})
        ]:
            func = func_tuple[0]
            args = func_tuple[1]
            kwargs = func_tuple[2]

            func.assert_any_call(*args, **kwargs)

        self.assertEqual(len(self.device.staged), 0)

    def test_lock(self):
        self.device._locked = False

        self.device.lock()

        self.device.connection.lock.assert_called_with('running')
        self.assertEqual(self.device._locked, True)

    def test_lock_conflict_error(self):
        error = RPCError(etree.Element('lock-denied'))
        error._tag = 'lock-denied'

        self.device.connection.lock.side_effect = error
        with self.assertRaises(LockConflictError):
            self.device.lock()

    def test_lock_error(self):
        self.device.connection.lock.side_effect = RPCError(etree.Element('error'))
        with self.assertRaises(NCError):
            self.device.lock()


    def test_unlock(self):
        self.device._locked = True

        self.device.unlock()

        self.device.connection.unlock.assert_called_with('running')
        self.assertEqual(self.device._locked, False)

    def test_unlock_conflict_error(self):
        self.device._locked = True

        error = RPCError(etree.Element('operation-failed'))
        error._tag = 'operation-failed'
        error._message = 'Unlock Failed'

        self.device.connection.unlock.side_effect = error
        with self.assertRaises(UnlockConflictError):
            self.device.unlock()

    def test_unlock_error(self):
        self.device._locked = True
        self.device.connection.unlock.side_effect = RPCError(etree.Element('error'))
        with self.assertRaises(NCError):
            self.device.unlock()

    @mock.patch.object(HPCOM7, 'execute')
    def test_edit_config(self, mock_execute):
        config = etree.Element('top')
        result = self.device.edit_config(config)
        expected_kwargs = dict(config=config, target='running')

        mock_execute.assert_called_with(self.device.connection.edit_config, kwargs=expected_kwargs)
        self.assertEqual(result, mock_execute.return_value)

    @mock.patch.object(HPCOM7, 'execute')
    def test_get(self, mock_execute):
        get_tuple = ('subtree', etree.Element('top'))
        result = self.device.get(get_tuple=get_tuple)
        expected_args = [get_tuple]

        mock_execute.assert_called_with(self.device.connection.get, expected_args)
        self.assertEqual(result, mock_execute.return_value)

    @mock.patch.object(HPCOM7, 'execute')
    def test_action(self, mock_execute):
        element = etree.Element('top')
        result = self.device.action(element)
        expected_args = [element]

        mock_execute.assert_called_with(self.device.connection.action, expected_args)
        self.assertEqual(result, mock_execute.return_value)

    @mock.patch.object(HPCOM7, 'execute')
    def test_save(self, mock_execute):
        filename = 'safety.cfg'
        result = self.device.save(filename=filename)
        expected_args = [filename]

        mock_execute.assert_called_with(self.device.connection.save, expected_args)
        self.assertEqual(result, mock_execute.return_value)

    @mock.patch.object(HPCOM7, 'execute')
    def test_rollback(self, mock_execute):
        filename = 'safety.cfg'
        result = self.device.rollback(filename=filename)
        expected_args = [filename]

        mock_execute.assert_called_with(self.device.connection.rollback, expected_args)
        self.assertEqual(result, mock_execute.return_value)

    @mock.patch.object(HPCOM7, 'execute')
    def test_cli_display(self, mock_execute):
        mock_execute.return_value = RPCReply("""<?xml version="1.0" encoding="UTF-8"?><rpc-reply xmlns:config="http://www.hp.com/netconf/config:1.0" xmlns:data="http://www.hp.com/netconf/data:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:44406142-e989-11e5-a4a3-60f81db7542c"><CLI><Execution><![CDATA[<HP1>display arp
  Type: S-Static   D-Dynamic   O-Openflow   R-Rule   M-Multiport  I-Invalid
IP address      MAC address    VLAN     Interface                Aging Type
10.1.100.1      0014-1c57-a4c2 N/A      M-GE0/0/0                18    D
]]></Execution></CLI></rpc-reply>""")

        command = 'display arp'
        result = self.device.cli_display(command)
        expected = '<HP1>display arp\n  Type: S-Static   D-Dynamic   O-Openflow   R-Rule   M-Multiport  I-Invalid\nIP address      MAC address    VLAN     Interface                Aging Type\n10.1.100.1      0014-1c57-a4c2 N/A      M-GE0/0/0                18    D\n'

        mock_execute.assert_called_with(self.device.connection.cli_display, [command])
        self.assertEqual(result, expected)

    @mock.patch.object(HPCOM7, 'execute')
    def test_cli_config(self, mock_execute):
        mock_execute.return_value = RPCReply("""<?xml version="1.0" encoding="UTF-8"?><rpc-reply xmlns:config="http://www.hp.com/netconf/config:1.0" xmlns:data="http://www.hp.com/netconf/data:1.0" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:5dcf4d19-e98b-11e5-8af9-60f81db7542c"><CLI><Configuration><![CDATA[<HP1>system
System View: return to User View with Ctrl+Z.
[HP1]interface FortyGigE1/0/1
]]></Configuration></CLI></rpc-reply>""")

        command = 'FortyGigE1/0/1'
        result = self.device.cli_config(command)
        expected = '<HP1>system\nSystem View: return to User View with Ctrl+Z.\n[HP1]interface FortyGigE1/0/1\n'

        mock_execute.assert_called_with(self.device.connection.cli_config, [command])
        self.assertEqual(result, expected)

    def test_reboot(self):
        self.device.reboot()
        self.device.connection.cli_display.assert_called_with(['reboot force'])

    def test_reboot_on_timeout(self):
        self.device.connection.cli_display.side_effect = NCTimeoutError

        self.device.reboot()
        self.device.connection.cli_display.assert_called_with(['reboot force'])






















if __name__ == "__main__":
    unittest.main()