import os
import re
import subprocess
import random
import string
from tempfile import mkstemp


class PdftkError(Exception):
    pass


class DuplicateFormFieldError(Exception):
    pass


class MissingFormFieldError(Exception):
    pass


class InvalidOptionError(Exception):
    pass


class TooManyPDFsError(Exception):
    pass


class InvalidAnswersError(Exception):
    pass


class UnsupportedFieldTypeError(Exception):
    pass


class PDFTKWrapper:

    supported_field_types = ['text', 'button', 'choice']

    def __init__(self, encoding='latin-1', tmp_path=None, clean_up=True):
        self.encoding = encoding
        self.TEMP_FOLDER_PATH = tmp_path
        self._tmp_files = []
        self._cache_fdf_for_filling = False
        self._fdf_cache = None
        self.clean_up = clean_up
        self.PDFTK_PATH = os.environ.get('PDFTK_PATH', 'pdftk')

    def _coerce_to_file_path(self, path_or_file_or_bytes):
        """This converst file-like objects and `bytes` into
        existing files and returns a filepath
        if strings are passed in, it is assumed that they are existing
        files
        """
        if not isinstance(path_or_file_or_bytes, str):
            if isinstance(path_or_file_or_bytes, bytes):
                return self._write_tmp_file(
                    bytestring=path_or_file_or_bytes)
            else:
                return self._write_tmp_file(
                    file_obj=path_or_file_or_bytes)
        return path_or_file_or_bytes

    def _write_tmp_file(self, file_obj=None, bytestring=None):
        """Take a file-like object or a bytestring,
        create a temporary file and return a file path.
        file-like objects will be read and written to the tempfile
        bytes objects will be written directly to the tempfile
        """
        tmp_path = self.TEMP_FOLDER_PATH
        os_int, tmp_fp = mkstemp(dir=tmp_path)
        with open(tmp_fp, 'wb') as tmp_file:
            if file_obj:
                tmp_file.write(file_obj.read())
            elif bytestring:
                tmp_file.write(bytestring)
        self._tmp_files.append(tmp_fp)
        return tmp_fp

    def clean_up_tmp_files(self):
        if not self._tmp_files:
            return
        for i in range(len(self._tmp_files)):
            path = self._tmp_files.pop()
            os.remove(path)

    def _get_file_contents(self, path, decode=False, encoding=None):
        """given a file path, return the contents of the file
        if decode is True, the contents will be decoded using the default
        encoding
        """
        bytestring = open(path, 'rb').read()
        if decode:
            return bytestring.decode(encoding or self.encoding)
        return bytestring

    def run_command(self, args):
        """Run a command to pdftk on the command line.
            `args` is a list of command line arguments.
        This method is reponsible for handling errors that arise from
        pdftk's CLI
        """
        if args[0] != self.PDFTK_PATH:
            args.insert(0, self.PDFTK_PATH)
        process = subprocess.Popen(args,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if err:
            raise PdftkError(err.decode('utf-8'))
        return out.decode('utf-8')

    def parse_fdf_fields(self, fdf_str):
        '''Yields a series of tuples, using the escaped name of the field
        followed by a dict with useful meta information about the match
            https://regex101.com/r/iL6hW3/5
        '''
        field_pattern = re.compile(
            r'\/V\ (?P<value>.*)\n\/T\ \((?P<name>.*)\)')
        for match in re.finditer(field_pattern, fdf_str):
            # it's necessary to deal with escape slashes in the field name
            # because it may otherwise fail to match the field name extracted
            # from the data field dump
            datum = {
                'name': match.group('name'),
                'escaped_name': match.group('name').replace('\\', ''),
                'name_span': match.span('name'),
                'value_template': match.group('value'),
                'value_template_span': match.span('value')
            }
            yield (datum['escaped_name'], datum)

    def parse_data_fields(self, data_str):
        '''Pulls out field data from the resulting string of
            `pdftk dump_data_fields_utf8`
        '''
        field_opts_key = 'FieldStateOption'
        field_name_key = 'FieldName'
        for field_text in data_str.split('---'):
            datum = {}
            for line in field_text.split('\n'):
                if line.strip():
                    propName, value = line.split(':')
                    if propName == field_opts_key:
                        if field_opts_key not in datum:
                            datum[field_opts_key] = [value.strip()]
                        else:
                            datum[field_opts_key].append(value.strip())
                    else:
                        datum[propName] = value.strip()
            if datum:
                yield (datum[field_name_key], datum)

    def get_fdf(self, pdf_file_path):
        """Given a path to a pdf form, this returns the decoded
        text of an output fdf file
        """
        pdf_file_path = self._coerce_to_file_path(pdf_file_path)
        tmp_outfile = self._write_tmp_file()
        self.run_command([pdf_file_path, 'generate_fdf',
                          'output', tmp_outfile])
        contents = self._get_file_contents(
            tmp_outfile, decode=True)
        if self._cache_fdf_for_filling:
            self._fdf_cache = contents
        return contents

    def get_data_fields(self, pdf_file_path):
        pdf_file_path = self._coerce_to_file_path(pdf_file_path)
        tmp_outfile = self._write_tmp_file()
        self.run_command([pdf_file_path, 'dump_data_fields_utf8',
                          'output', tmp_outfile])
        contents = self._get_file_contents(
            tmp_outfile, decode=True, encoding='utf-8')
        return contents

    def _get_full_form_field_data(self, pdf_file_path):
        # fdf_data & field_data are generators
        fdf_data = self.parse_fdf_fields(
            self.get_fdf(pdf_file_path))
        field_data = self.parse_data_fields(
            self.get_data_fields(pdf_file_path))
        fields = {}
        for name, datum in field_data:
            if name in fields:
                raise DuplicateFormFieldError(
                    "Duplicate field data: '{}'".format(name))
            fields[name] = datum
        for name, datum in fdf_data:
            if name not in fields:
                raise MissingFormFieldError(
                    "No matching data for field: '{}'".format(name))
            elif 'fdf' in fields[name]:
                raise DuplicateFormFieldError(
                    "Duplicate fdf field: '{}'".format(name))
            fields[name]['fdf'] = datum
        return fields

    def get_field_data(self, pdf_file_path):
        full_data = self._get_full_form_field_data(
            pdf_file_path)
        data = []
        for key in full_data:
            full_datum = full_data[key]
            datum = {
                'name': key,
                'type': full_datum['FieldType'].lower(),
            }
            if 'FieldValue' in full_datum:
                datum['value'] = full_datum['FieldValue']
            if 'FieldStateOption' in full_datum:
                datum['options'] = full_datum['FieldStateOption']
                if 'value' in datum:
                    if datum['value'] not in datum['options']:
                        datum['options'].append(datum['value'])
            if datum['type'] not in self.supported_field_types:
                raise UnsupportedFieldTypeError(
                    "Unsupported field type: '{}'".format(datum['type']))
            data.append(datum)
        return sorted(data, key=lambda d: d['name'])

    def _build_answer_insertion(self, value, field):
        value = str(value)
        field_type = field['FieldType'].lower()
        options = field.get('FieldStateOption', [])
        if field_type == 'button':
            span = field['fdf']['value_template_span']
            start = span[0] + 1
            end = span[1]
            if value not in options:
                raise InvalidOptionError(
                    "'{}' is not in options for '{}': {}".format(
                        value,
                        field['FieldName'], str(options)))
            return (start, end, value)
        else:  # 'choice' and 'text' types
            span = field['fdf']['value_template_span']
            start = span[0] + 1
            end = span[1] - 1
            # we could check options here, but that would exclude
            # custom other values
            return (start, end, value)

    def _generate_answer_insertions(self, pdf_path, answers):
        fields = self._get_full_form_field_data(pdf_path)
        insertions = []
        for key in answers:
            if key in fields:
                insertion = self._build_answer_insertion(
                    answers[key], fields[key])
                insertions.append(insertion)
        if not insertions:
            raise InvalidAnswersError("""No valid answers were found.
Answer Keys: {}
Available Fields: {}
""".format(
                str(list(answers.keys())),
                str(list(fields.keys()))
            ))
        insertions.sort(key=lambda i: i[0])
        return insertions

    def _patch_fdf_with_insertions(self, insertions, fdf_str=None):
        if not fdf_str:
            fdf_str = self._fdf_cache
        fdf = []
        position = 0
        for start, end, value in insertions:
            fdf.append(fdf_str[position:start])
            fdf.append(value)
            position = end
        fdf.append(fdf_str[position:])
        return ''.join(fdf)

    def _load_patched_fdf_into_pdf(self, pdf_file_path, fdf_str):
        filled_fdf_path = self._write_tmp_file(
            bytestring=fdf_str.encode(self.encoding))
        tmp_pdf_path = self._write_tmp_file()
        self.run_command([
            pdf_file_path,
            'fill_form', filled_fdf_path,
            'output', tmp_pdf_path
        ])
        return tmp_pdf_path

    def join_pdfs(self, pdf_paths):
        """
        pdftk A=in1.pdf B=in2.pdf cat A1 B2-20even output out.pdf
        """
        if len(pdf_paths) > 99999:
            raise TooManyPDFsError(
                "I'm worred about combining more than 99,999 pdfs")
        pdf_paths = [self._coerce_to_file_path(p) for p in pdf_paths]
        combined_pdf_path = self._write_tmp_file()
        handle_length = 4
        pdftk_args = []
        handles = []
        for i, path in enumerate(pdf_paths):
            idxs = [int(n) for n in "{num:05d}".format(num=i)]
            handle = ''.join(
                string.ascii_uppercase[idx]
                for idx in idxs
            )
            handles.append(handle)
            pdftk_args.append(
                "{}={}".format(handle, path)
            )
        pdftk_args.append('cat')
        pdftk_args.extend(handles)
        pdftk_args.extend([
            'output', combined_pdf_path
        ])
        self.run_command(pdftk_args)
        result = open(combined_pdf_path, 'rb').read()
        if self.clean_up:
            self.clean_up_tmp_files()
        return result

    def fill_pdf_many(self, pdf_path, multiple_answers):
        pdfs = []
        _clean_up_setting = self.clean_up
        # don't clean up while filling multiple pdfs
        self.clean_up = False
        pdf_path = self._coerce_to_file_path(pdf_path)
        for answer in multiple_answers:
            filled_pdf = self.fill_pdf(pdf_path, answer)
            pdf_path = self._write_tmp_file(bytestring=filled_pdf)
            pdfs.append(pdf_path)
        # restore the clean up setting
        self.clean_up = _clean_up_setting
        return self.join_pdfs(pdfs)

    def fill_pdf(self, pdf_path, answers):
        self._cache_fdf_for_filling = True
        pdf_path = self._coerce_to_file_path(pdf_path)
        insertions = self._generate_answer_insertions(pdf_path, answers)
        patched_fdf_str = self._patch_fdf_with_insertions(insertions)
        output_path = self._load_patched_fdf_into_pdf(
            pdf_path, patched_fdf_str)
        result = open(output_path, 'rb').read()
        if self.clean_up:
            self.clean_up_tmp_files()
        return result