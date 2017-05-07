# coding: utf-8

# Copyright 2014-2016 Álvaro Justen <https://github.com/turicas/rows/>
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

from __future__ import unicode_literals

import datetime
import decimal
import json
import tempfile
import six

import json_lines

from rows import fields
from rows.plugins.utils import (create_table, export_data,
                                get_filename_and_fobj, prepare_to_export)


def import_from_json_lines(filename_or_fobj, encoding='utf-8', *args, **kwargs):
    '''Import a JSON file or file-like object into a `rows.Table`

    If a file-like object is provided it MUST be open in text (non-binary) mode
    on Python 3 and could be open in both binary or text mode on Python 2.
    '''
    filename, fobj = get_filename_and_fobj(filename_or_fobj)

    json_lines_obj = list(json_lines.reader(fobj))
    field_names = list(json_lines_obj[0].keys())
    table_rows = [[item[key] for key in field_names] for item in json_lines_obj]

    meta = {'imported_from': 'json_lines',
            'filename': filename,
            'encoding': encoding, }
    return create_table([field_names] + table_rows, meta=meta, *args, **kwargs)


def _convert(value, field_type, *args, **kwargs):
    if value is None or field_type in (
                fields.BinaryField,
                fields.BoolField,
                fields.FloatField,
                fields.IntegerField,
                fields.JSONField,
                fields.TextField,
    ):
        # If the field_type is one of those, the value can be passed directly
        # to the JSON encoder
        return value
    else:
        # The field type is not represented natively in JSON, then it needs to
        # be serialized (converted to a string)
        return field_type.serialize(value, *args, **kwargs)


def export_to_json_lines(table, filename_or_fobj=None, encoding='utf-8', *args, **kwargs):
    '''Export a `rows.Table` to a JSON file or file-like object

    If a file-like object is provided it MUST be open in binary mode (like in
    `open('myfile.json', mode='wb')`).
    '''
    fields = table.fields
    prepared_table = prepare_to_export(table, *args, **kwargs)
    field_names = next(prepared_table)
    data = [{field_name: _convert(value, fields[field_name], *args, **kwargs)
             for field_name, value in zip(field_names, row)}
            for row in prepared_table]

    result = '\n'.join([json.dumps(item) for item in data])

    if type(result) is six.text_type:  # Python 3
        result = result.encode(encoding)

    return export_data(filename_or_fobj, result, mode='wb')

