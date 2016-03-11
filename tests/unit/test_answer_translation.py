from unittest import TestCase, mock
from typeseam.utils.translate import (
    MissingProcessorError,
    InvalidTranslatorError,
    translate_to_seamless,
    access_path
    )


def subset(d, keys):
    return {k: d[k] for k in keys if k in d}


class TestTranslations(TestCase):

    def setUp(self):
        self.processors = {
            "cow": mock.Mock(return_value="moo"),
            "duck": mock.Mock(return_value="quack"),
        }

        self.input_data = {
            "meta": {"date_submit": "2016-03-01"},
            "reality": {"van_chase": {"hotel": {"snow_fortress": "inception"}}},
            "unused": "anything",
            "pizza": "party",
            "the_answer": 42,
            "greeting": "hello"
        }

        self.translator = {
            "accessor": ["meta.date_submit"],
            "multi_level_accessor": ["reality.van_chase.hotel.snow_fortress"],
            "one_directly": ["pizza"],
            "not_found": ["missing"],
            "not_found_with_func": ["missing", ["duck"]],
            "single_arg": ["the_answer", ["duck"]],
            "multi_arg": [["pizza", "the_answer"], ["duck"]],
            "multi_func": ["the_answer", ["duck", "cow"]],
            "multi_func_multi_arg": [["pizza", "the_answer"], ["duck", "cow"]],
        }

    def test_accessors(self):
        r = translate_to_seamless(self.input_data, self.translator, self.processors)
        self.assertEqual(r["accessor"], "2016-03-01")
        self.assertEqual(r["multi_level_accessor"], "inception")
        self.assertEqual(r["one_directly"], "party")
        self.assertEqual(r["not_found"], "")
        # the chosen processor should be responsible for handling missing values
        self.assertEqual(r["not_found_with_func"], "quack")
        self.assertDictEqual(r, {
            "accessor": "2016-03-01",
            "multi_level_accessor": "inception",
            "one_directly": "party",
            "not_found": "",
            "not_found_with_func": "quack",
            "single_arg": "quack",
            "multi_arg": "quack",
            "multi_func": "moo",
            "multi_func_multi_arg": "moo",
            })

    def test_access_path(self):
        data = {"van_chase": {"hotel": {"snow_fortress": "inception"}}}
        path = "van_chase.hotel.snow_fortress"
        self.assertEqual(access_path(path, data), "inception")

    def test_single_arg(self):
        t = subset(self.translator, ['single_arg'])
        r = translate_to_seamless(self.input_data, t, self.processors)
        self.processors['duck'].assert_called_once_with('single_arg', 42)

    def test_multi_arg(self):
        t = subset(self.translator, ['multi_arg'])
        r = translate_to_seamless(self.input_data, t, self.processors)
        self.processors['duck'].assert_called_once_with('multi_arg', 'party', 42)

    def test_multi_func(self):
        t = subset(self.translator, ['multi_func'])
        r = translate_to_seamless(self.input_data, t, self.processors)
        # multiple functions should be called in sequence
        self.processors['duck'].assert_called_once_with('multi_func', 42)
        self.processors['cow'].assert_called_once_with('multi_func', 'quack')

    def test_multi_func_multi_arg(self):
        t = subset(self.translator, ['multi_func_multi_arg'])
        r = translate_to_seamless(self.input_data, t, self.processors)
        # each processor chooses whether or not to pass the original args to the next function
        self.processors['duck'].assert_called_once_with('multi_func_multi_arg', "party", 42)
        self.processors['cow'].assert_called_once_with('multi_func_multi_arg', "quack")

    def test_missing_processor(self):
        t = {'should_error': ['pizza', ['nonexistent_function']]}
        with self.assertRaises(MissingProcessorError):
            r = translate_to_seamless(self.input_data, t, self.processors)

    def test_missing_key_and_missing_processor(self):
        t = {'should_error': ['missing', ['nonexistent_function']]}
        with self.assertRaises(MissingProcessorError):
            r = translate_to_seamless(self.input_data, t, self.processors)

    def test_empty_instructions(self):
        t = {}
        r = translate_to_seamless(self.input_data, t, self.processors)
        self.assertDictEqual(r, t)

    def test_invalid_instructions(self):
        t = "just some random non-dict data"
        with self.assertRaises(InvalidTranslatorError):
            r = translate_to_seamless(self.input_data, t, self.processors)

    def test_no_data(self):
        d = {}
        r = translate_to_seamless(d, self.translator, self.processors)
        # processors should be responsible for handling missing data
        # otherwise, all answers should be empty strings
        self.assertDictEqual(r, {
            "accessor": "",
            "multi_level_accessor": "",
            "one_directly": "",
            "not_found": "",
            "not_found_with_func": "quack",
            "single_arg": "quack",
            "multi_arg": "quack",
            "multi_func": "moo",
            "multi_func_multi_arg": "moo",
            })
