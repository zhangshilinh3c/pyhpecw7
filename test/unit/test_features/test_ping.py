import unittest
import mock

from pyhpecw7.features.ping import Ping
from pyhpecw7.features.errors import InvalidIPAddress
from base_feature_test import BaseFeatureCase

TARGET = '8.8.8.8'

class PingTestCase(BaseFeatureCase):

    @mock.patch('pyhpecw7.comware.HPCOM7')
    def setUp(self, mock_device):
        self.device = mock_device

    @mock.patch.object(Ping, '_ping')
    def test_init(self, mock_ping):
        ping = Ping(self.device, TARGET)

        self.assertEqual(ping.vrf, '')
        self.assertEqual(ping.host, TARGET)
        self.assertEqual(ping.v6, False)
        self.assertEqual(ping.detail, False)

        ping6 = Ping(self.device, TARGET, v6=True)

        self.assertEqual(ping6.vrf, '')
        self.assertEqual(ping6.host, TARGET)
        self.assertEqual(ping6.v6, True)
        self.assertEqual(ping6.detail, False)

        mock_ping.assert_has_calls([mock.call(), mock.call()])

    @mock.patch.object(Ping, '_build_response')
    def test_ping(self, mock_build):
        ping = Ping(self.device, TARGET)

        action, reply = self.xml_action_and_reply('ping')
        self.device.action.return_value = reply

        result = ping._ping()

        self.assert_action_request(action)
        mock_build.assert_called_with(reply)
        self.assertEqual(result, mock_build.return_value)

    @mock.patch.object(Ping, '_ping')
    def test_build_response(self, mock_ping):
        ping = Ping(self.device, TARGET, detail=True)
        reply = self.read_action_reply_xml('ping')
        result = ping._build_response(reply)

        expected = {
            'payload_length': '56',
            'max': '8',
            'packets_rx': '5',
            'detailed_response': [
                {
                    'reply_time': '8',
                    'icmp_seq': '0'
                },
                {
                    'reply_time': '7',
                    'icmp_seq': '1'
                },
                {
                    'reply_time': '7',
                    'icmp_seq': '2'
                },
                {
                    'reply_time': '7',
                    'icmp_seq': '3'
                },
                {
                    'reply_time': '11',
                    'icmp_seq': '4'
                }
            ],
            'loss_rate': '0',
            'host': '8.8.8.8',
            'min': '8',
            'packets_tx': '5',
            'avg': '8'
        }

        self.assertEqual(result, expected)

    @mock.patch.object(Ping, '_ping')
    def test_param_check(self, mock_ping):
        ping = Ping(self.device, '1.2.3')
        with self.assertRaises(InvalidIPAddress):
            ping.param_check(host=ping.host)


if __name__ == '__main__':
    unittest.main()
