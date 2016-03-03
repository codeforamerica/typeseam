
class MissingProcessorError(Exception):
    pass


class InvalidTranslatorError(Exception):
    pass


def access_path(keypath, dictionary, sep="."):
    if sep in keypath:
        pieces = keypath.split(sep)
        val = dictionary
        for key in pieces:
            if key in val:
                val = val[key]
            else:
                return ""
        return val
    else:
        return dictionary.get(keypath, "")


def translate_to_seamless(input_data, translator, processors, key_separator="."):
    translated_answers = {}
    if not hasattr(translator, 'items'):
        raise InvalidTranslatorError(
            "translators must be dictionary-like objects, not '{}'".format(type(translator)))
    for target, config in translator.items():
        answer_key = config[0]
        answer_keys = []
        input_arg_data = ""
        if not isinstance(answer_key, str):
            answer_keys = answer_key
        if answer_keys:
            input_arg_data = [access_path(k, input_data, key_separator) for k in answer_keys]
        else:
            input_arg_data = access_path(answer_key, input_data, key_separator)

        final_value = ""
        if len(config) == 2:
            processor_keys = config[-1]
            for k in processor_keys:
                if k not in processors:
                    raise MissingProcessorError(
                        "'{}' is not among the given processors".format(k))
            answer_processors = [processors[k] for k in processor_keys]
            for answer_processor in answer_processors:
                # unpack any list or tuple-like arg data, but not strings.
                if hasattr(input_arg_data, '__iter__') and not hasattr(input_arg_data, 'strip'):
                    input_arg_data = answer_processor(target, *input_arg_data)
                else:
                    input_arg_data = answer_processor(target, input_arg_data)
            final_value = input_arg_data
        elif "yesno" in answer_key:
            yn_processor = processors["yesno"]
            final_value = yn_processor(target, input_arg_data)
        else:
            final_value = input_arg_data
        translated_answers[target] = final_value

    return translated_answers
