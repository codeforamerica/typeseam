
import sys
sys.path.append('./data')
import translator

def translate_to_seamless(typeform, processors=None):
    trans = translator.fields
    answers = {}
    answers.update({
        "_meta_date_submitted": typeform['metadata']['date_submit']
        })
    answers.update(typeform['answers'])
    translated_answers = {}

    for target, config in trans.items():
        answer_key = config[0]
        answer_keys = []
        raw_values = ""
        raw_value = ""
        if not isinstance(answer_key, str):
            answer_keys = answer_key
        if answer_keys:
            raw_values = [answers[k] for k in answer_keys if k in answers]
        else:
            raw_value = answers.get(answer_key, "")

        final_value = ""
        if len(config) == 2:
            processor_keys = config[-1]
            answer_processors = [processors.lookup[k] for k in processor_keys]
            for answer_processor in answer_processors:
                if raw_values:
                    final_value = answer_processor(target, *raw_values)
                else:
                    final_value = answer_processor(target, raw_value)
        elif "yesno" in answer_key:
            yn_processor = processors.lookup["yesno"]
            final_value = yn_processor(target, raw_value)
        else:
            final_value = raw_value
        translated_answers[target] = final_value

    return translated_answers
