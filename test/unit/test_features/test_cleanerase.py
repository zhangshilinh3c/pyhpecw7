import unittest
import mock

from pyhpecw7.features.cleanerase import CleanErase
from base_feature_test import BaseFeatureCase

class CleanEraseTestCase(BaseFeatureCase):

    @mock.patch('pyhpecw7.comware.HPCOM7')
    def setUp(self, mock_device):
        self.device = mock_device
        self.clean_erase = CleanErase(self.device)

    def test_build(self):
        self.clean_erase.build(factory_default=True)
        self.device.cli_display.assert_called_with(['restore factory-default'])

        self.clean_erase.build(factory_default=True, stage=True)
        self.device.stage_config.assert_called_with(['restore factory-default'], 'cli_display')
        self.device.reboot.assert_called_with()

        result = self.clean_erase.build()
        self.assertEqual(result, None)

if __name__ == "__main__":
    unittest.main()