# coding: utf-8

# Copyright 2017 Flávio Pontes <flaviocpontes@gmail.com> Tafarel Yan <tafarel.yan@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from unittest import mock
import tempfile

import rows

import tests.utils as utils


class PluginJsonLinesTestCase(utils.RowsTestMixIn, unittest.TestCase):

    plugin_name = 'json_lines'
    file_extension = 'jsonl'
    filename = 'tests/data/all-field-types.jsonl'
    encoding = 'utf-8'
    assert_meta_encoding = True

    def test_imports(self):
        self.assertIs(rows.import_from_json_lines,
                      rows.plugins.plugin_json_lines.import_from_json_lines)
        self.assertIs(rows.export_to_json_lines, rows.plugins.plugin_json_lines.export_to_json_lines)

    @mock.patch('rows.plugins.plugin_json_lines.create_table')
    def test_import_from_json_lines_uses_create_table(self, mocked_create_table):
        mocked_create_table.return_value = 42
        kwargs = {'some_key': 123, 'other': 456, }
        result = rows.import_from_json_lines(self.filename, encoding=self.encoding,
                                             **kwargs)
        self.assertTrue(mocked_create_table.called)
        self.assertEqual(mocked_create_table.call_count, 1)
        self.assertEqual(result, 42)

        call = mocked_create_table.call_args
        kwargs['meta'] = {'imported_from': 'json_lines',
                          'filename': self.filename,
                          'encoding': self.encoding, }
        self.assertEqual(call[1], kwargs)

    @mock.patch('rows.plugins.plugin_json_lines.create_table')
    def test_import_from_json_lines_retrieve_desired_data(self, mocked_create_table):
        mocked_create_table.return_value = 42

        # import using filename
        table_1 = rows.import_from_json_lines(self.filename)
        call_args = mocked_create_table.call_args_list[0]
        self.assert_create_table_data(call_args, field_ordering=False)

        # import using fobj
        with open(self.filename) as fobj:
            table_2 = rows.import_from_json_lines(fobj)
            call_args = mocked_create_table.call_args_list[1]
            self.assert_create_table_data(call_args, field_ordering=False)

    @mock.patch('rows.plugins.plugin_json_lines.prepare_to_export')
    def test_export_to_json_lines_uses_prepare_to_export(self,
            mocked_prepare_to_export):
        temp = tempfile.NamedTemporaryFile(delete=False, mode='wb')
        self.files_to_delete.append(temp.name)
        kwargs = {'test': 123, 'parameter': 3.14, }
        mocked_prepare_to_export.return_value = \
                iter([utils.table.fields.keys()])

        rows.export_to_json_lines(utils.table, temp.name, **kwargs)
        self.assertTrue(mocked_prepare_to_export.called)
        self.assertEqual(mocked_prepare_to_export.call_count, 1)

        call = mocked_prepare_to_export.call_args
        self.assertEqual(call[0], (utils.table, ))
        self.assertEqual(call[1], kwargs)

