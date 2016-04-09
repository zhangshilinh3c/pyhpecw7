import unittest
import mock
import __builtin__
from tempfile import NamedTemporaryFile

from pyhpecw7.features.file_copy import FileCopy, FileNotEnoughSpaceError, FileNotReadableError, FileHashMismatchError, FileTransferError, NCError
from base_feature_test import BaseFeatureCase

SOURCE_FILE = '/path/to/source/file.txt'

class FileCopyTestCase(BaseFeatureCase):

    @mock.patch('pyhpecw7.comware.HPCOM7')
    def setUp(self, mock_device):
        self.device = mock_device
        self.file_copy = FileCopy(self.device, SOURCE_FILE)

    def test_init(self):
        self.assertEqual(self.file_copy._remote_dir, 'flash:/')
        self.assertEqual(self.file_copy.src, SOURCE_FILE)
        self.assertEqual(self.file_copy.dst, 'flash:/file.txt')
        self.assertEqual(self.file_copy.port, 22)
        self.assertEqual(self.file_copy.remote_dir_exists, True)

    def test_get_flash_size(self):
        self.device.cli_display.return_value = self.read_cli_display('dir_flash')
        result = self.file_copy._get_flash_size()

        self.assertEqual(result, 742204000)

        self.device.cli_display.return_value = 'garbaldigook'
        result = self.file_copy._get_flash_size()

        self.assertEqual(result, 0)

    @mock.patch.object(FileCopy, '_get_flash_size')
    @mock.patch('os.path.getsize')
    def test_enough_space(self, mock_getsize, mock_get_flash_size):
        mock_getsize.return_value = 2
        mock_get_flash_size.return_value = 1

        with self.assertRaises(FileNotEnoughSpaceError):
            self.file_copy._enough_space()

        mock_getsize.return_value = 1
        mock_get_flash_size.return_value = 2

        result = self.file_copy._enough_space()
        self.assertEqual(result, None)

    @mock.patch.object(FileCopy, '_get_remote_md5')
    @mock.patch.object(FileCopy, '_get_local_md5')
    def test_file_already_exists(self, mock_local_md5, mock_remote_md5):
        mock_local_md5.return_value = 'abc123'
        mock_remote_md5.return_value = 'abc123'

        result = self.file_copy.file_already_exists()
        self.assertEqual(result, True)

        self.file_copy.remote_dir_exists = False
        result = self.file_copy.file_already_exists()
        self.assertEqual(result, False)

        self.file_copy.remote_dir_exists = True
        mock_remote_md5.return_value = None
        result = self.file_copy.file_already_exists()
        self.assertEqual(result, False)

        mock_remote_md5.side_effect = NCError
        result = self.file_copy.file_already_exists()
        self.assertEqual(result, False)

    @mock.patch.object(__builtin__, 'open')
    def test_safety_checks_file_not_readable(self, mock_open):
        mock_open.side_effect = IOError
        with self.assertRaises(FileNotReadableError):
            self.file_copy._safety_checks()

    @mock.patch.object(__builtin__, 'open')
    def test_safety_checks_no_remote_dir(self, mock_open):
        self.file_copy.remote_dir_exists = False
        with self.assertRaises(FileRemoteDirDoesNotExist):
            self.file_copy._safety_checks()

    @mock.patch.object(__builtin__, 'open')
    def test_safety_checks_no_remote_dir(self, mock_open):
        self.file_copy.remote_dir_exists = False
        with self.assertRaises(FileRemoteDirDoesNotExist):
            self.file_copy._safety_checks()

    @mock.patch.object(FileCopy, 'file_already_exists')
    @mock.patch.object(FileCopy, '_enough_space')
    @mock.patch.object(__builtin__, 'open')
    def test_safety_checks_no_remote_dir(self, mock_open, mock_enough_space, mock_file_already_exists):
        mock_file_already_exists.return_value = False
        self.file_copy._safety_checks()
        mock_enough_space.assert_called_with()

    def test_remote_md5(self):
        expected_get, get_reply = self.xml_action_and_reply('file_copy_remote_md5')
        self.device.action.return_value = get_reply

        expected = '44d5527772e1b9841f99cb03f31cbc1c'
        result = self.file_copy._get_remote_md5()

        self.assertEqual(result, expected)
        self.assert_action_request(expected_get)

    def test_local_md5(self):
        test_file = NamedTemporaryFile()
        self.file_copy.src = test_file.name

        test_file.write('Test content.')
        test_file.flush()

        result = self.file_copy._get_local_md5()
        self.assertEqual(result, 'bcb898f62d9e1ac765c77e6804cbd872')

        test_file.close()

    def test_remote_dir(self):
        expected_get, get_reply = self.xml_get_and_reply('file_copy_remote_dir')
        self.device.get.return_value = get_reply

        expected = True
        result = self.file_copy._remote_dir_exists()

        self.assertEqual(result, expected)
        self.assert_get_request(expected_get)


    @mock.patch('pyhpecw7.features.file_copy.paramiko')
    @mock.patch('pyhpecw7.features.file_copy.SCPClient')
    @mock.patch.object(FileCopy, '_safety_checks')
    @mock.patch.object(FileCopy, '_get_local_md5')
    @mock.patch.object(FileCopy, '_get_remote_md5')
    def test_transfer_file(self, mock_remote_md5, mock_local_md5, mock_safety_checks, mock_SCP, mock_paramiko):
        mock_remote_md5.return_value = 'abc'
        mock_local_md5.return_value = 'abc'

        mock_ssh = mock_paramiko.SSHClient.return_value

        self.file_copy.transfer_file()

        mock_paramiko.SSHClient.assert_called_with()

        mock_ssh.set_missing_host_key_policy.assert_called_with(mock_paramiko.AutoAddPolicy.return_value)
        mock_ssh.connect.assert_called_with(allow_agent=False,
                                             hostname=self.device.host,
                                             look_for_keys=False,
                                             password=self.device.password,
                                             port=22,
                                             username=self.device.username)

        mock_SCP.assert_called_with(mock_ssh.get_transport.return_value)
        mock_SCP.return_value.put.assert_called_with('/path/to/source/file.txt', 'flash:/file.txt')
        mock_SCP.return_value.close.assert_called_with()

    @mock.patch('pyhpecw7.features.file_copy.paramiko')
    @mock.patch('pyhpecw7.features.file_copy.SCPClient')
    @mock.patch.object(FileCopy, '_safety_checks')
    @mock.patch.object(FileCopy, '_get_local_md5')
    @mock.patch.object(FileCopy, '_get_remote_md5')
    def test_transfer_file_mismatch_hash(self, mock_remote_md5, mock_local_md5, mock_safety_checks, mock_SCP, mock_paramiko):
        mock_remote_md5.return_value = 'abc'
        mock_local_md5.return_value = 'def'

        mock_ssh = mock_paramiko.SSHClient.return_value

        with self.assertRaises(FileHashMismatchError):
            self.file_copy.transfer_file()

        mock_paramiko.SSHClient.assert_called_with()

        mock_ssh.set_missing_host_key_policy.assert_called_with(mock_paramiko.AutoAddPolicy.return_value)
        mock_ssh.connect.assert_called_with(allow_agent=False,
                                             hostname=self.device.host,
                                             look_for_keys=False,
                                             password=self.device.password,
                                             port=22,
                                             username=self.device.username)

        mock_SCP.assert_called_with(mock_ssh.get_transport.return_value)
        mock_SCP.return_value.put.assert_called_with('/path/to/source/file.txt', 'flash:/file.txt')
        mock_SCP.return_value.close.assert_called_with()

    @mock.patch('pyhpecw7.features.file_copy.paramiko')
    @mock.patch('pyhpecw7.features.file_copy.SCPClient')
    @mock.patch.object(FileCopy, '_safety_checks')
    @mock.patch.object(FileCopy, '_get_local_md5')
    @mock.patch.object(FileCopy, '_get_remote_md5')
    def test_transfer_file_error(self, mock_remote_md5, mock_local_md5, mock_safety_checks, mock_SCP, mock_paramiko):
        mock_remote_md5.return_value = 'abc'
        mock_local_md5.return_value = 'def'

        mock_ssh = mock_paramiko.SSHClient.return_value

        mock_SCP.return_value.put.side_effect = Exception

        with self.assertRaises(FileTransferError):
            self.file_copy.transfer_file()

        mock_paramiko.SSHClient.assert_called_with()

        mock_ssh.set_missing_host_key_policy.assert_called_with(mock_paramiko.AutoAddPolicy.return_value)
        mock_ssh.connect.assert_called_with(allow_agent=False,
                                             hostname=self.device.host,
                                             look_for_keys=False,
                                             password=self.device.password,
                                             port=22,
                                             username=self.device.username)

        mock_SCP.assert_called_with(mock_ssh.get_transport.return_value)
        mock_SCP.return_value.put.assert_called_with('/path/to/source/file.txt', 'flash:/file.txt')


    def test_create_dir(self):
        self.file_copy._remote_dir = 'flash:/unit/'

        expected_get, get_reply = self.xml_action_and_reply('file_copy_create_remote_dir')
        self.device.action.return_value = get_reply

        expected = None
        result = self.file_copy.create_remote_dir()

        self.assertEqual(result, expected)
        self.assert_action_request(expected_get)


if __name__ == "__main__":
    unittest.main()