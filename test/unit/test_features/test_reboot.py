import unittest
import mock

from pyhpecw7.features.reboot import Reboot, RebootDateError, RebootTimeError

from base_feature_test import BaseFeatureCase

class RebootTestCase(BaseFeatureCase):

    @mock.patch('pyhpecw7.comware.HPCOM7')
    def setUp(self, mock_device):
        self.device = mock_device
        self.reboot = Reboot(self.device)

    def test_build(self):
        self.reboot.build(reboot=True)
        self.device.cli_display.assert_called_with(['reboot force'])

        self.reboot.build(stage=True, reboot=True)
        self.device.stage_config.assert_called_with(['reboot force'], 'cli_display')

    def test_build_delay(self):
        self.reboot.build(reboot=True, delay='20')
        self.device.cli_display.assert_called_with(['scheduler reboot delay 20'])

        self.reboot.build(stage=True, delay='20', reboot=True)
        self.device.stage_config.assert_called_with(['scheduler reboot delay 20'], 'cli_display')

    def test_build_at_time(self):
        self.reboot.build(reboot=True, time='10')
        self.device.cli_display.assert_called_with(['scheduler reboot at 10'])

        self.reboot.build(stage=True, time='10', reboot=True)
        self.device.stage_config.assert_called_with(['scheduler reboot at 10'], 'cli_display')

    def test_build_at_time_and_date(self):
        self.reboot.build(reboot=True, time='10', date='15')
        self.device.cli_display.assert_called_with(['scheduler reboot at 10 15'])

        self.reboot.build(stage=True, time='10', date='15', reboot=True)
        self.device.stage_config.assert_called_with(['scheduler reboot at 10 15'], 'cli_display')

    def test_param_check_time(self):
        result = self.reboot.param_check(time='03:02')
        self.assertEqual(result, None)

        with self.assertRaises(RebootTimeError):
            self.reboot.param_check(time='20')

        with self.assertRaises(RebootTimeError):
            self.reboot.param_check(time='0::03')

        with self.assertRaises(RebootTimeError):
            self.reboot.param_check(time='0:203')

    def test_param_check_date(self):
        result = self.reboot.param_check(date='03/02/2939')
        self.assertEqual(result, None)

        with self.assertRaises(RebootDateError):
            self.reboot.param_check(date='03.02.2939')

        with self.assertRaises(RebootDateError):
            self.reboot.param_check(date='03/02/2939/3929')

        with self.assertRaises(RebootDateError):
            self.reboot.param_check(date='003/02/2939')

        with self.assertRaises(RebootDateError):
            self.reboot.param_check(date='03/002/2939')

        with self.assertRaises(RebootDateError):
            self.reboot.param_check(date='03/02/29393')

if __name__ == "__main__":
    unittest.main()