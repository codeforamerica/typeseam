"""
a set of functions that may be used to translate Typeform answers
into the appropriate SeamlessDocs formats

"""

def initials(target, input_value):
    return input_value.strip()[0].upper()

def add(target, *args):
    return " ".join(args)

def yesno(target, input_value):
    if input_value == "1":
        return "Yes"
    else:
        return "No"

def phone_switch(target, value='', value_type='', value_type_other=''):
    target_type = target.split("_")[-1]
    type_search = value_type.lower()
    if target_type in type_search:
        return value
    else:
        return ""

lookup = {
    "initials": initials,
    "add": add,
    "phone_switch": phone_switch,
    "yesno": yesno,
}