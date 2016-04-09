import unittest
import os
from operator import attrgetter

from ncclient.operations.retrieve import GetReply, RPCReply
from lxml import etree

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

class BaseFeatureCase(unittest.TestCase):

    def read_xml(self, operation, filename):
        if not filename.endswith('.xml'):
            filename = filename + '.xml'

        path = os.path.join(CURRENT_DIR, 'fixtures', operation, filename)
        with open(path) as f:
            content = f.read()

        return content

    def read_txt(self, operation, filename):
        if not filename.endswith('.txt'):
            filename = filename + '.txt'

        path = os.path.join(CURRENT_DIR, 'fixtures', operation, filename)
        with open(path) as f:
            content = f.read()

        return content

    def read_get_xml(self, filename):
        return etree.fromstring(self.read_xml('get', filename))

    def read_get_reply_xml(self, filename):
        return GetReply(self.read_xml('get_reply', filename))

    def read_config_xml(self, filename):
        return etree.fromstring(self.read_xml('edit_config', filename))

    def read_action_xml(self, filename):
        return etree.fromstring(self.read_xml('action', filename))

    def read_action_reply_xml(self, filename):
        return RPCReply(self.read_xml('action_reply', filename))

    def xml_get_and_reply(self, filename):
        return self.read_get_xml(filename), self.read_get_reply_xml(filename)

    def xml_action_and_reply(self, filename):
        return self.read_action_xml(filename), self.read_action_reply_xml(filename)

    def args_in_mock_call(self, func):
        last = len(func.mock_calls) - 1
        name, args, kwargs = func.mock_calls[last]
        while not args and last > 0:
            last = last - 1
            name, args, kwargs = func.mock_calls[last]

        return args

    def args_in_all_mock_calls(self, func):
        return list(x[1] for x in func.mock_calls if x[1])

    def read_cli_display(self, filename):
        return self.read_txt('cli_display', filename)

    def assert_get_request(self, expected):
        get_arg = self.args_in_mock_call(self.device.get)[0]

        self.assertEqual(get_arg[0], 'subtree')
        self.assert_elements_equal(get_arg[1], expected)

    def assert_action_request(self, expected):
        action_arg = self.args_in_mock_call(self.device.action)[0]
        self.assert_elements_equal(action_arg, expected)

    def assert_config_request(self, expected):
        config_arg = self.args_in_mock_call(self.device.edit_config)[0]
        self.assert_elements_equal(config_arg, expected)

    def assert_stage_request(self, expected, op_type):
        stage_args = self.args_in_mock_call(self.device.stage_config)

        self.assertEqual(stage_args[1], op_type)

        if isinstance(stage_args[0], str):
            self.assertEqual(stage_args[0], expected)
        else:
            self.assert_elements_equal(stage_args[0], expected)


    def assert_stage_requests_multiple(self, expected_list):
        actual_list = self.args_in_all_mock_calls(self.device.stage_config)
        for i in range(len(actual_list)):
            actual_ele, actual_op_type = tuple(actual_list[i])
            expected_ele, expected_op_type = tuple(expected_list[i])

            self.assertEqual(actual_op_type, expected_op_type)

            if isinstance(actual_ele, str):
                self.assertEqual(actual_ele, expected_ele)
            else:
                self.assert_elements_equal(actual_ele, expected_ele)

    def elements_are_equal(self, e1, e2):
        if e1.tag != e2.tag: return False
        if e1.text != e2.text:
            if e1.text == '' and e2.text is None:
                pass
            elif e1.text is None and e2.text == '':
                pass
            else:
                return False
        if e1.tail != e2.tail: return False
        if e1.attrib != e2.attrib: return False
        if len(e1) != len(e2): return False


        return all(self.elements_are_equal(c1, c2) for c1, c2 in zip(sorted(e1, key=attrgetter('tag')), sorted(e2, key=attrgetter('tag'))))

    def assert_elements_equal(self, e1, e2):
        are_equal = self.elements_are_equal(e1, e2)
        self.assertTrue(are_equal)


