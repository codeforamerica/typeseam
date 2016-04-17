from unittest import TestCase
from unittest.mock import Mock, patch
from typeseam.form_filler.pdftk_wrapper import PDFTKWrapper, PdftkError

# these are based on the pdf form in 'data/sample_pdfs/sample_form.pdf'
FDF_STR_SAMPLE = "%FDF-1.2\n%âãÏÓ\n1 0 obj \n<<\n/FDF \n<<\n/Fields [\n<<\n/V /\n/T (US Citizen)\n>> \n<<\n/V ()\n/T (How did you hear about the Clean Slate Program)\n>> \n<<\n/V ()\n/T (Email Address)\n>> \n<<\n/V ()\n/T (Home phone number)\n>> \n<<\n/V /\n/T (Arrested outside SF)\n>> \n<<\n/V ()\n/T (Last Name)\n>> \n<<\n/V /\n/T (May we leave voicemail)\n>> \n<<\n/V ()\n/T (MI)\n>> \n<<\n/V ()\n/T (Social Security Number)\n>> \n<<\n/V ()\n/T (Address State)\n>> \n<<\n/V ()\n/T (First Name)\n>> \n<<\n/V /\n/T (May we send mail here)\n>> \n<<\n/V ()\n/T (Monthly expenses)\n>> \n<<\n/V ()\n/T (What is your monthly income)\n>> \n<<\n/V ()\n/T (Address Street)\n>> \n<<\n/V ()\n/T (Drivers License)\n>> \n<<\n/V ()\n/T (Other phone number)\n>> \n<<\n/V ()\n/T (If probation where and when?)\n>> \n<<\n/V ()\n/T (Dates arrested outside SF)\n>> \n<<\n/V ()\n/T (Address Zip)\n>> \n<<\n/V /\n/T (On probation or parole)\n>> \n<<\n/V /\n/T (Charged with a crime)\n>> \n<<\n/V /\n/T (Serving a sentence)\n>> \n<<\n/V ()\n/T (Date of Birth)\n>> \n<<\n/V ()\n/T (Work phone number)\n>> \n<<\n/V ()\n/T (Cell phone number)\n>> \n<<\n/V ()\n/T (Date)\n>> \n<<\n/V ()\n/T (Address City)\n>> \n<<\n/V /\n/T (Employed)\n>>]\n>>\n>>\nendobj \ntrailer\n\n<<\n/Root 1 0 R\n>>\n%%EOF\n"
DATA_FIELDS_STR_SAMPLE = "---\nFieldType: Text\nFieldName: Date\nFieldNameAlt: Date\nFieldFlags: 4096\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: Last Name\nFieldNameAlt: Last Name\nFieldFlags: 4096\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: MI\nFieldNameAlt: MI\nFieldFlags: 4096\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: Social Security Number\nFieldNameAlt: Social Security Number\nFieldFlags: 0\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: Drivers License\nFieldNameAlt: Driver’s License #\nFieldFlags: 0\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: Email Address\nFieldNameAlt: Email Address\nFieldFlags: 0\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: What is your monthly income\nFieldNameAlt: What is your monthly income? $\nFieldFlags: 0\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: How did you hear about the Clean Slate Program\nFieldNameAlt: How did you hear about the Clean Slate Program?\nFieldFlags: 0\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: Date of Birth\nFieldNameAlt: Date of Birth\nFieldFlags: 4096\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: First Name\nFieldNameAlt: First Name\nFieldFlags: 4096\nFieldJustification: Left\n---\nFieldType: Button\nFieldName: US Citizen\nFieldFlags: 49152\nFieldJustification: Left\nFieldStateOption: No\nFieldStateOption: Off\nFieldStateOption: Yes\n---\nFieldType: Text\nFieldName: If probation where and when?\nFieldFlags: 0\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: Dates arrested outside SF\nFieldFlags: 0\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: Monthly expenses\nFieldNameAlt: Monthly expenses\nFieldFlags: 0\nFieldJustification: Left\n---\nFieldType: Button\nFieldName: Employed\nFieldFlags: 49152\nFieldJustification: Left\nFieldStateOption: No\nFieldStateOption: Off\nFieldStateOption: Yes\n---\nFieldType: Button\nFieldName: Arrested outside SF\nFieldFlags: 49152\nFieldJustification: Left\nFieldStateOption: No\nFieldStateOption: Off\nFieldStateOption: Yes\n---\nFieldType: Button\nFieldName: Charged with a crime\nFieldFlags: 49152\nFieldJustification: Left\nFieldStateOption: No\nFieldStateOption: Off\nFieldStateOption: Yes\n---\nFieldType: Button\nFieldName: Serving a sentence\nFieldFlags: 49152\nFieldJustification: Left\nFieldStateOption: No\nFieldStateOption: Off\nFieldStateOption: Yes\n---\nFieldType: Button\nFieldName: On probation or parole\nFieldFlags: 49152\nFieldJustification: Left\nFieldStateOption: No\nFieldStateOption: Off\nFieldStateOption: Yes\n---\nFieldType: Button\nFieldName: May we leave voicemail\nFieldFlags: 49152\nFieldJustification: Left\nFieldStateOption: No\nFieldStateOption: Off\nFieldStateOption: Yes\n---\nFieldType: Button\nFieldName: May we send mail here\nFieldFlags: 49152\nFieldJustification: Left\nFieldStateOption: No\nFieldStateOption: Off\nFieldStateOption: Yes\n---\nFieldType: Text\nFieldName: Address Street\nFieldFlags: 0\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: Address City\nFieldFlags: 0\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: Address State\nFieldFlags: 0\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: Address Zip\nFieldFlags: 0\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: Cell phone number\nFieldFlags: 0\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: Home phone number\nFieldFlags: 0\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: Work phone number\nFieldFlags: 0\nFieldJustification: Left\n---\nFieldType: Text\nFieldName: Other phone number\nFieldFlags: 0\nFieldJustification: Left\n"
PARSED_FDF_FIELDS = [('US Citizen', {'name': 'US Citizen', 'escaped_name': 'US Citizen', 'name_span': (58, 68), 'value_template': '/', 'value_template_span': (52, 53)}), ('How did you hear about the Clean Slate Program', {'name': 'How did you hear about the Clean Slate Program', 'escaped_name': 'How did you hear about the Clean Slate Program', 'name_span': (87, 133), 'value_template': '()', 'value_template_span': (80, 82)}), ('Email Address', {'name': 'Email Address', 'escaped_name': 'Email Address', 'name_span': (152, 165), 'value_template': '()', 'value_template_span': (145, 147)}), ('Home phone number', {'name': 'Home phone number', 'escaped_name': 'Home phone number', 'name_span': (184, 201), 'value_template': '()', 'value_template_span': (177, 179)}), ('Arrested outside SF', {'name': 'Arrested outside SF', 'escaped_name': 'Arrested outside SF', 'name_span': (219, 238), 'value_template': '/', 'value_template_span': (213, 214)}), ('Last Name', {'name': 'Last Name', 'escaped_name': 'Last Name', 'name_span': (257, 266), 'value_template': '()', 'value_template_span': (250, 252)}), ('May we leave voicemail', {'name': 'May we leave voicemail', 'escaped_name': 'May we leave voicemail', 'name_span': (284, 306), 'value_template': '/', 'value_template_span': (278, 279)}), ('MI', {'name': 'MI', 'escaped_name': 'MI', 'name_span': (325, 327), 'value_template': '()', 'value_template_span': (318, 320)}), ('Social Security Number', {'name': 'Social Security Number', 'escaped_name': 'Social Security Number', 'name_span': (346, 368), 'value_template': '()', 'value_template_span': (339, 341)}), ('Address State', {'name': 'Address State', 'escaped_name': 'Address State', 'name_span': (387, 400), 'value_template': '()', 'value_template_span': (380, 382)}), ('First Name', {'name': 'First Name', 'escaped_name': 'First Name', 'name_span': (419, 429), 'value_template': '()', 'value_template_span': (412, 414)}), ('May we send mail here', {'name': 'May we send mail here', 'escaped_name': 'May we send mail here', 'name_span': (447, 468), 'value_template': '/', 'value_template_span': (441, 442)}), ('Monthly expenses', {'name': 'Monthly expenses', 'escaped_name': 'Monthly expenses', 'name_span': (487, 503), 'value_template': '()', 'value_template_span': (480, 482)}), ('What is your monthly income', {'name': 'What is your monthly income', 'escaped_name': 'What is your monthly income', 'name_span': (522, 549), 'value_template': '()', 'value_template_span': (515, 517)}), ('Address Street', {'name': 'Address Street',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           'escaped_name': 'Address Street', 'name_span': (568, 582), 'value_template': '()', 'value_template_span': (561, 563)}), ('Drivers License', {'name': 'Drivers License', 'escaped_name': 'Drivers License', 'name_span': (601, 616), 'value_template': '()', 'value_template_span': (594, 596)}), ('Other phone number', {'name': 'Other phone number', 'escaped_name': 'Other phone number', 'name_span': (635, 653), 'value_template': '()', 'value_template_span': (628, 630)}), ('If probation where and when?', {'name': 'If probation where and when?', 'escaped_name': 'If probation where and when?', 'name_span': (672, 700), 'value_template': '()', 'value_template_span': (665, 667)}), ('Dates arrested outside SF', {'name': 'Dates arrested outside SF', 'escaped_name': 'Dates arrested outside SF', 'name_span': (719, 744), 'value_template': '()', 'value_template_span': (712, 714)}), ('Address Zip', {'name': 'Address Zip', 'escaped_name': 'Address Zip', 'name_span': (763, 774), 'value_template': '()', 'value_template_span': (756, 758)}), ('On probation or parole', {'name': 'On probation or parole', 'escaped_name': 'On probation or parole', 'name_span': (792, 814), 'value_template': '/', 'value_template_span': (786, 787)}), ('Charged with a crime', {'name': 'Charged with a crime', 'escaped_name': 'Charged with a crime', 'name_span': (832, 852), 'value_template': '/', 'value_template_span': (826, 827)}), ('Serving a sentence', {'name': 'Serving a sentence', 'escaped_name': 'Serving a sentence', 'name_span': (870, 888), 'value_template': '/', 'value_template_span': (864, 865)}), ('Date of Birth', {'name': 'Date of Birth', 'escaped_name': 'Date of Birth', 'name_span': (907, 920), 'value_template': '()', 'value_template_span': (900, 902)}), ('Work phone number', {'name': 'Work phone number', 'escaped_name': 'Work phone number', 'name_span': (939, 956), 'value_template': '()', 'value_template_span': (932, 934)}), ('Cell phone number', {'name': 'Cell phone number', 'escaped_name': 'Cell phone number', 'name_span': (975, 992), 'value_template': '()', 'value_template_span': (968, 970)}), ('Date', {'name': 'Date', 'escaped_name': 'Date', 'name_span': (1011, 1015), 'value_template': '()', 'value_template_span': (1004, 1006)}), ('Address City', {'name': 'Address City', 'escaped_name': 'Address City', 'name_span': (1034, 1046), 'value_template': '()', 'value_template_span': (1027, 1029)}), ('Employed', {'name': 'Employed', 'escaped_name': 'Employed', 'name_span': (1064, 1072), 'value_template': '/', 'value_template_span': (1058, 1059)})]
PARSED_DATA_FIELDS = [('Date', {'FieldJustification': 'Left', 'FieldNameAlt': 'Date', 'FieldName': 'Date', 'FieldType': 'Text', 'FieldFlags': '4096'}), ('Last Name', {'FieldJustification': 'Left', 'FieldNameAlt': 'Last Name', 'FieldName': 'Last Name', 'FieldType': 'Text', 'FieldFlags': '4096'}), ('MI', {'FieldJustification': 'Left', 'FieldNameAlt': 'MI', 'FieldName': 'MI', 'FieldType': 'Text', 'FieldFlags': '4096'}), ('Social Security Number', {'FieldJustification': 'Left', 'FieldNameAlt': 'Social Security Number', 'FieldName': 'Social Security Number', 'FieldType': 'Text', 'FieldFlags': '0'}), ('Drivers License', {'FieldJustification': 'Left', 'FieldNameAlt': 'Driver’s License #', 'FieldName': 'Drivers License', 'FieldType': 'Text', 'FieldFlags': '0'}), ('Email Address', {'FieldJustification': 'Left', 'FieldNameAlt': 'Email Address', 'FieldName': 'Email Address', 'FieldType': 'Text', 'FieldFlags': '0'}), ('What is your monthly income', {'FieldJustification': 'Left', 'FieldNameAlt': 'What is your monthly income? $', 'FieldName': 'What is your monthly income', 'FieldType': 'Text', 'FieldFlags': '0'}), ('How did you hear about the Clean Slate Program', {'FieldJustification': 'Left', 'FieldNameAlt': 'How did you hear about the Clean Slate Program?', 'FieldName': 'How did you hear about the Clean Slate Program', 'FieldType': 'Text', 'FieldFlags': '0'}), ('Date of Birth', {'FieldJustification': 'Left', 'FieldNameAlt': 'Date of Birth', 'FieldName': 'Date of Birth', 'FieldType': 'Text', 'FieldFlags': '4096'}), ('First Name', {'FieldJustification': 'Left', 'FieldNameAlt': 'First Name', 'FieldName': 'First Name', 'FieldType': 'Text', 'FieldFlags': '4096'}), ('US Citizen', {'FieldJustification': 'Left', 'FieldName': 'US Citizen', 'FieldType': 'Button', 'FieldFlags': '49152', 'FieldStateOption': ['No', 'Off', 'Yes']}), ('If probation where and when?', {'FieldJustification': 'Left', 'FieldName': 'If probation where and when?', 'FieldType': 'Text', 'FieldFlags': '0'}), ('Dates arrested outside SF', {'FieldJustification': 'Left', 'FieldName': 'Dates arrested outside SF', 'FieldType': 'Text', 'FieldFlags': '0'}), ('Monthly expenses', {'FieldJustification': 'Left', 'FieldNameAlt': 'Monthly expenses', 'FieldName': 'Monthly expenses', 'FieldType': 'Text', 'FieldFlags': '0'}), ('Employed', {
    'FieldJustification': 'Left', 'FieldName': 'Employed', 'FieldType': 'Button', 'FieldFlags': '49152', 'FieldStateOption': ['No', 'Off', 'Yes']}), ('Arrested outside SF', {'FieldJustification': 'Left', 'FieldName': 'Arrested outside SF', 'FieldType': 'Button', 'FieldFlags': '49152', 'FieldStateOption': ['No', 'Off', 'Yes']}), ('Charged with a crime', {'FieldJustification': 'Left', 'FieldName': 'Charged with a crime', 'FieldType': 'Button', 'FieldFlags': '49152', 'FieldStateOption': ['No', 'Off', 'Yes']}), ('Serving a sentence', {'FieldJustification': 'Left', 'FieldName': 'Serving a sentence', 'FieldType': 'Button', 'FieldFlags': '49152', 'FieldStateOption': ['No', 'Off', 'Yes']}), ('On probation or parole', {'FieldJustification': 'Left', 'FieldName': 'On probation or parole', 'FieldType': 'Button', 'FieldFlags': '49152', 'FieldStateOption': ['No', 'Off', 'Yes']}), ('May we leave voicemail', {'FieldJustification': 'Left', 'FieldName': 'May we leave voicemail', 'FieldType': 'Button', 'FieldFlags': '49152', 'FieldStateOption': ['No', 'Off', 'Yes']}), ('May we send mail here', {'FieldJustification': 'Left', 'FieldName': 'May we send mail here', 'FieldType': 'Button', 'FieldFlags': '49152', 'FieldStateOption': ['No', 'Off', 'Yes']}), ('Address Street', {'FieldJustification': 'Left', 'FieldName': 'Address Street', 'FieldType': 'Text', 'FieldFlags': '0'}), ('Address City', {'FieldJustification': 'Left', 'FieldName': 'Address City', 'FieldType': 'Text', 'FieldFlags': '0'}), ('Address State', {'FieldJustification': 'Left', 'FieldName': 'Address State', 'FieldType': 'Text', 'FieldFlags': '0'}), ('Address Zip', {'FieldJustification': 'Left', 'FieldName': 'Address Zip', 'FieldType': 'Text', 'FieldFlags': '0'}), ('Cell phone number', {'FieldJustification': 'Left', 'FieldName': 'Cell phone number', 'FieldType': 'Text', 'FieldFlags': '0'}), ('Home phone number', {'FieldJustification': 'Left', 'FieldName': 'Home phone number', 'FieldType': 'Text', 'FieldFlags': '0'}), ('Work phone number', {'FieldJustification': 'Left', 'FieldName': 'Work phone number', 'FieldType': 'Text', 'FieldFlags': '0'}), ('Other phone number', {'FieldJustification': 'Left', 'FieldName': 'Other phone number', 'FieldType': 'Text', 'FieldFlags': '0'})]
FIELD_DATA_MAP_SAMPLE = {'Address Street': {'FieldName': 'Address Street', 'FieldJustification': 'Left', 'FieldFlags': '0', 'FieldType': 'Text', 'fdf': {'value_template_span': (561, 563), 'name_span': (568, 582), 'name': 'Address Street', 'value_template': '()', 'escaped_name': 'Address Street'}}, 'Serving a sentence': {'FieldStateOption': ['No', 'Off', 'Yes'], 'fdf': {'value_template_span': (864, 865), 'name_span': (870, 888), 'name': 'Serving a sentence', 'value_template': '/', 'escaped_name': 'Serving a sentence'}, 'FieldName': 'Serving a sentence', 'FieldJustification': 'Left', 'FieldFlags': '49152', 'FieldType': 'Button'}, 'How did you hear about the Clean Slate Program': {'FieldNameAlt': 'How did you hear about the Clean Slate Program?', 'fdf': {'value_template_span': (80, 82), 'name_span': (87, 133), 'name': 'How did you hear about the Clean Slate Program', 'value_template': '()', 'escaped_name': 'How did you hear about the Clean Slate Program'}, 'FieldName': 'How did you hear about the Clean Slate Program', 'FieldJustification': 'Left', 'FieldFlags': '0', 'FieldType': 'Text'}, 'Last Name': {'FieldNameAlt': 'Last Name', 'fdf': {'value_template_span': (250, 252), 'name_span': (257, 266), 'name': 'Last Name', 'value_template': '()', 'escaped_name': 'Last Name'}, 'FieldName': 'Last Name', 'FieldJustification': 'Left', 'FieldFlags': '4096', 'FieldType': 'Text'}, 'Other phone number': {'FieldName': 'Other phone number', 'FieldJustification': 'Left', 'FieldFlags': '0', 'FieldType': 'Text', 'fdf': {'value_template_span': (628, 630), 'name_span': (635, 653), 'name': 'Other phone number', 'value_template': '()', 'escaped_name': 'Other phone number'}}, 'First Name': {'FieldNameAlt': 'First Name', 'fdf': {'value_template_span': (412, 414), 'name_span': (419, 429), 'name': 'First Name', 'value_template': '()', 'escaped_name': 'First Name'}, 'FieldName': 'First Name', 'FieldJustification': 'Left', 'FieldFlags': '4096', 'FieldType': 'Text'}, 'Address State': {'FieldName': 'Address State', 'FieldJustification': 'Left', 'FieldFlags': '0', 'FieldType': 'Text', 'fdf': {'value_template_span': (380, 382), 'name_span': (387, 400), 'name': 'Address State', 'value_template': '()', 'escaped_name': 'Address State'}}, 'Work phone number': {'FieldName': 'Work phone number', 'FieldJustification': 'Left', 'FieldFlags': '0', 'FieldType': 'Text', 'fdf': {'value_template_span': (932, 934), 'name_span': (939, 956), 'name': 'Work phone number', 'value_template': '()', 'escaped_name': 'Work phone number'}}, 'Address Zip': {'FieldName': 'Address Zip', 'FieldJustification': 'Left', 'FieldFlags': '0', 'FieldType': 'Text', 'fdf': {'value_template_span': (756, 758), 'name_span': (763, 774), 'name': 'Address Zip', 'value_template': '()', 'escaped_name': 'Address Zip'}}, 'Social Security Number': {'FieldNameAlt': 'Social Security Number', 'fdf': {'value_template_span': (339, 341), 'name_span': (346, 368), 'name': 'Social Security Number', 'value_template': '()', 'escaped_name': 'Social Security Number'}, 'FieldName': 'Social Security Number', 'FieldJustification': 'Left', 'FieldFlags': '0', 'FieldType': 'Text'}, 'US Citizen': {'FieldStateOption': ['No', 'Off', 'Yes'], 'fdf': {'value_template_span': (52, 53), 'name_span': (58, 68), 'name': 'US Citizen', 'value_template': '/', 'escaped_name': 'US Citizen'}, 'FieldName': 'US Citizen', 'FieldJustification': 'Left', 'FieldFlags': '49152', 'FieldType': 'Button'}, 'Email Address': {'FieldNameAlt': 'Email Address', 'fdf': {'value_template_span': (145, 147), 'name_span': (152, 165), 'name': 'Email Address', 'value_template': '()', 'escaped_name': 'Email Address'}, 'FieldName': 'Email Address', 'FieldJustification': 'Left', 'FieldFlags': '0', 'FieldType': 'Text'}, 'What is your monthly income': {'FieldNameAlt': 'What is your monthly income? $', 'fdf': {'value_template_span': (515, 517), 'name_span': (522, 549), 'name': 'What is your monthly income', 'value_template': '()', 'escaped_name': 'What is your monthly income'}, 'FieldName': 'What is your monthly income', 'FieldJustification': 'Left', 'FieldFlags': '0', 'FieldType': 'Text'}, 'Arrested outside SF': {'FieldStateOption': ['No', 'Off', 'Yes'], 'fdf': {'value_template_span': (213, 214), 'name_span': (219, 238), 'name': 'Arrested outside SF', 'value_template': '/', 'escaped_name': 'Arrested outside SF'}, 'FieldName': 'Arrested outside SF', 'FieldJustification': 'Left', 'FieldFlags': '49152', 'FieldType': 'Button'}, 'Home phone number': {'FieldName': 'Home phone number', 'FieldJustification': 'Left', 'FieldFlags': '0', 'FieldType': 'Text', 'fdf': {
    'value_template_span': (177, 179), 'name_span': (184, 201), 'name': 'Home phone number', 'value_template': '()', 'escaped_name': 'Home phone number'}}, 'Drivers License': {'FieldNameAlt': 'Driver’s License #', 'fdf': {'value_template_span': (594, 596), 'name_span': (601, 616), 'name': 'Drivers License', 'value_template': '()', 'escaped_name': 'Drivers License'}, 'FieldName': 'Drivers License', 'FieldJustification': 'Left', 'FieldFlags': '0', 'FieldType': 'Text'}, 'May we send mail here': {'FieldStateOption': ['No', 'Off', 'Yes'], 'fdf': {'value_template_span': (441, 442), 'name_span': (447, 468), 'name': 'May we send mail here', 'value_template': '/', 'escaped_name': 'May we send mail here'}, 'FieldName': 'May we send mail here', 'FieldJustification': 'Left', 'FieldFlags': '49152', 'FieldType': 'Button'}, 'Date': {'FieldNameAlt': 'Date', 'fdf': {'value_template_span': (1004, 1006), 'name_span': (1011, 1015), 'name': 'Date', 'value_template': '()', 'escaped_name': 'Date'}, 'FieldName': 'Date', 'FieldJustification': 'Left', 'FieldFlags': '4096', 'FieldType': 'Text'}, 'MI': {'FieldNameAlt': 'MI', 'fdf': {'value_template_span': (318, 320), 'name_span': (325, 327), 'name': 'MI', 'value_template': '()', 'escaped_name': 'MI'}, 'FieldName': 'MI', 'FieldJustification': 'Left', 'FieldFlags': '4096', 'FieldType': 'Text'}, 'Address City': {'FieldName': 'Address City', 'FieldJustification': 'Left', 'FieldFlags': '0', 'FieldType': 'Text', 'fdf': {'value_template_span': (1027, 1029), 'name_span': (1034, 1046), 'name': 'Address City', 'value_template': '()', 'escaped_name': 'Address City'}}, 'On probation or parole': {'FieldStateOption': ['No', 'Off', 'Yes'], 'fdf': {'value_template_span': (786, 787), 'name_span': (792, 814), 'name': 'On probation or parole', 'value_template': '/', 'escaped_name': 'On probation or parole'}, 'FieldName': 'On probation or parole', 'FieldJustification': 'Left', 'FieldFlags': '49152', 'FieldType': 'Button'}, 'Date of Birth': {'FieldNameAlt': 'Date of Birth', 'fdf': {'value_template_span': (900, 902), 'name_span': (907, 920), 'name': 'Date of Birth', 'value_template': '()', 'escaped_name': 'Date of Birth'}, 'FieldName': 'Date of Birth', 'FieldJustification': 'Left', 'FieldFlags': '4096', 'FieldType': 'Text'}, 'Cell phone number': {'FieldName': 'Cell phone number', 'FieldJustification': 'Left', 'FieldFlags': '0', 'FieldType': 'Text', 'fdf': {'value_template_span': (968, 970), 'name_span': (975, 992), 'name': 'Cell phone number', 'value_template': '()', 'escaped_name': 'Cell phone number'}}, 'Monthly expenses': {'FieldNameAlt': 'Monthly expenses', 'fdf': {'value_template_span': (480, 482), 'name_span': (487, 503), 'name': 'Monthly expenses', 'value_template': '()', 'escaped_name': 'Monthly expenses'}, 'FieldName': 'Monthly expenses', 'FieldJustification': 'Left', 'FieldFlags': '0', 'FieldType': 'Text'}, 'May we leave voicemail': {'FieldStateOption': ['No', 'Off', 'Yes'], 'fdf': {'value_template_span': (278, 279), 'name_span': (284, 306), 'name': 'May we leave voicemail', 'value_template': '/', 'escaped_name': 'May we leave voicemail'}, 'FieldName': 'May we leave voicemail', 'FieldJustification': 'Left', 'FieldFlags': '49152', 'FieldType': 'Button'}, 'Dates arrested outside SF': {'FieldName': 'Dates arrested outside SF', 'FieldJustification': 'Left', 'FieldFlags': '0', 'FieldType': 'Text', 'fdf': {'value_template_span': (712, 714), 'name_span': (719, 744), 'name': 'Dates arrested outside SF', 'value_template': '()', 'escaped_name': 'Dates arrested outside SF'}}, 'If probation where and when?': {'FieldName': 'If probation where and when?', 'FieldJustification': 'Left', 'FieldFlags': '0', 'FieldType': 'Text', 'fdf': {'value_template_span': (665, 667), 'name_span': (672, 700), 'name': 'If probation where and when?', 'value_template': '()', 'escaped_name': 'If probation where and when?'}}, 'Charged with a crime': {'FieldStateOption': ['No', 'Off', 'Yes'], 'fdf': {'value_template_span': (826, 827), 'name_span': (832, 852), 'name': 'Charged with a crime', 'value_template': '/', 'escaped_name': 'Charged with a crime'}, 'FieldName': 'Charged with a crime', 'FieldJustification': 'Left', 'FieldFlags': '49152', 'FieldType': 'Button'}, 'Employed': {'FieldStateOption': ['No', 'Off', 'Yes'], 'fdf': {'value_template_span': (1058, 1059), 'name_span': (1064, 1072), 'name': 'Employed', 'value_template': '/', 'escaped_name': 'Employed'}, 'FieldName': 'Employed', 'FieldJustification': 'Left', 'FieldFlags': '49152', 'FieldType': 'Button'}}
FIELD_DATA = [{'name': 'Address City', 'type': 'text'}, {'name': 'Address State', 'type': 'text'}, {'name': 'Address Street', 'type': 'text'}, {'name': 'Address Zip', 'type': 'text'}, {'name': 'Arrested outside SF', 'type': 'button', 'options': ['No', 'Off', 'Yes']}, {'name': 'Cell phone number', 'type': 'text'}, {'name': 'Charged with a crime', 'type': 'button', 'options': ['No', 'Off', 'Yes']}, {'name': 'Date', 'type': 'text'}, {'name': 'Date of Birth', 'type': 'text'}, {'name': 'Dates arrested outside SF', 'type': 'text'}, {'name': 'Drivers License', 'type': 'text'}, {'name': 'Email Address', 'type': 'text'}, {'name': 'Employed', 'type': 'button', 'options': ['No', 'Off', 'Yes']}, {'name': 'First Name', 'type': 'text'}, {'name': 'Home phone number', 'type': 'text'}, {'name': 'How did you hear about the Clean Slate Program', 'type': 'text'}, {
    'name': 'If probation where and when?', 'type': 'text'}, {'name': 'Last Name', 'type': 'text'}, {'name': 'MI', 'type': 'text'}, {'name': 'May we leave voicemail', 'type': 'button', 'options': ['No', 'Off', 'Yes']}, {'name': 'May we send mail here', 'type': 'button', 'options': ['No', 'Off', 'Yes']}, {'name': 'Monthly expenses', 'type': 'text'}, {'name': 'On probation or parole', 'type': 'button', 'options': ['No', 'Off', 'Yes']}, {'name': 'Other phone number', 'type': 'text'}, {'name': 'Serving a sentence', 'type': 'button', 'options': ['No', 'Off', 'Yes']}, {'name': 'Social Security Number', 'type': 'text'}, {'name': 'US Citizen', 'type': 'button', 'options': ['No', 'Off', 'Yes']}, {'name': 'What is your monthly income', 'type': 'text'}, {'name': 'Work phone number', 'type': 'text'}]
CHECKBOX_SAMPLE = [{'name': 'Check Box2', 'options': ['Off', 'Yes'], 'type': 'button'}, {
    'name': 'Check Box3', 'options': ['Off', 'Yes'], 'type': 'button'}]
RADIO_SAMPLE = [{'name': 'Radio Buttons', 'type': 'button',
                 'options': ['Off', 'blue', 'red', 'yellow']}]
LISTBOX_SAMPLE = [{'options': [
    'apple', 'banana', 'durian', 'orange'], 'type': 'choice', 'name': 'List Box1'}]
DROPDOWN_SAMPLE = [{'value': '河', 'type': 'choice',
                    'name': 'Dropdown5', 'options': ['river', 'río', '河', '강']}]
TEXT_SAMPLE = [{'name': 'multiline', 'type': 'text'},
               {'name': 'single', 'type': 'text'}]


class TestPDFTK(TestCase):

    def test_init(self):
        pdftk = PDFTKWrapper()
        self.assertEqual(pdftk.encoding, 'latin-1')
        self.assertEqual(pdftk.TEMP_FOLDER_PATH, None)
        pdftk = PDFTKWrapper(
            encoding='utf-8', tmp_path='data')
        self.assertEqual(pdftk.encoding, 'utf-8')
        self.assertEqual(pdftk.TEMP_FOLDER_PATH, 'data')

    def test_get_fdf(self):
        pdftk = PDFTKWrapper()
        coercer = Mock(return_value='path.pdf')
        pdftk._coerce_to_file_path = coercer
        writer = Mock(return_value='tmp_path.fdf')
        pdftk._write_tmp_file = writer
        runner = Mock()
        pdftk.run_command = runner
        contents_getter = Mock()
        pdftk._get_file_contents = contents_getter
        results = pdftk.get_fdf('something.pdf')
        coercer.assert_called_once_with('something.pdf')
        writer.assert_called_once_with()
        runner.assert_called_once_with([
            'path.pdf', 'generate_fdf',
            'output', 'tmp_path.fdf'])
        contents_getter.assert_called_once_with(
            'tmp_path.fdf', decode=True)

    @patch('typeseam.form_filler.pdftk_wrapper.subprocess')
    def test_run_command(self, subprocess):
        pdftk = PDFTKWrapper()
        comm_err = Mock(return_value=(b'', b'an error'))
        comm_out = Mock(return_value=(b'success', b''))
        proc_out = Mock(communicate=comm_out)
        proc_err = Mock(communicate=comm_err)
        popen_yes = Mock(return_value=proc_out)
        popen_bad = Mock(return_value=proc_err)

        # check the good case
        subprocess.Popen = popen_yes
        args = ['pdftk', 'go']
        result = pdftk.run_command(args)
        self.assertEqual('success', result)
        popen_yes.assert_called_once_with(args,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        comm_out.assert_called_once_with()
        proc_out.assert_not_called()

        # check the arg fixing
        popen_yes.reset_mock()
        result = pdftk.run_command(['dostuff'])
        popen_yes.assert_called_once_with(['pdftk', 'dostuff'],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # check the bad case
        subprocess.reset_mock()
        subprocess.Popen = popen_bad
        args = ['go']
        with self.assertRaises(PdftkError):
            pdftk.run_command(args)
        proc_err.assert_not_called()
        comm_err.assert_called_once_with()
        popen_bad.assert_called_once_with(['pdftk', 'go'],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @patch('typeseam.form_filler.pdftk_wrapper.mkstemp')
    @patch('builtins.open')
    def test_write_tmp_file(self, open, mkstemp):
        mkstemp.return_value = ('os.file', 'filepath')
        mock_file = Mock()

        # check with file_object
        pdftk = PDFTKWrapper()
        path = pdftk._write_tmp_file(mock_file)
        mkstemp.assert_called_once_with(dir=pdftk.TEMP_FOLDER_PATH)
        open.assert_called_once_with('filepath', 'wb')
        mock_file.read.assert_called_once_with()
        self.assertEqual(path, 'filepath')
        self.assertListEqual(pdftk._tmp_files, ['filepath'])

        # check with bytes
        pdftk = PDFTKWrapper()
        mkstemp.reset_mock()
        open.reset_mock()
        path = pdftk._write_tmp_file(bytestring=b'content')
        open.assert_called_once_with('filepath', 'wb')
        self.assertEqual(path, 'filepath')
        self.assertListEqual(pdftk._tmp_files, ['filepath'])

    @patch('typeseam.form_filler.pdftk_wrapper.os.remove')
    def test_clean_up_tmp_files(self, remove):
        pdftk = PDFTKWrapper()
        paths = [c for c in 'hello']
        pdftk._tmp_files = paths
        pdftk.clean_up_tmp_files()
        for p in paths:
            remove.assert_any_call(p)
        self.assertListEqual(pdftk._tmp_files, [])
        # test with no files
        remove.reset_mock()
        pdftk.clean_up_tmp_files()
        remove.assert_not_called()

    def test_coerce_to_file_path(self):
        pdftk = PDFTKWrapper()
        wrt_tmp = Mock(return_value='path')
        pdftk._write_tmp_file = wrt_tmp

        # check with a string input
        result = pdftk._coerce_to_file_path('goodpath')
        self.assertEqual(result, 'goodpath')
        wrt_tmp.assert_not_called()

        # check with a bytestring input
        bstring = b'foo'
        result = pdftk._coerce_to_file_path(bstring)
        self.assertEqual(result, 'path')
        wrt_tmp.assert_called_once_with(bytestring=bstring)

        # check with a not string input
        wrt_tmp.reset_mock()
        not_string = Mock()
        result = pdftk._coerce_to_file_path(not_string)
        self.assertEqual(result, 'path')
        wrt_tmp.assert_called_once_with(file_obj=not_string)

    @patch('builtins.open')
    def test_get_file_contents(self, open):
        pdftk = PDFTKWrapper(encoding='utf-2000')
        decoder = Mock(return_value='decoded')
        # check with no decode
        mock_bytestring = Mock(decode=decoder)
        open.return_value.read.return_value = mock_bytestring
        result = pdftk._get_file_contents('path')
        self.assertEqual(result, mock_bytestring)
        open.assert_called_once_with('path', 'rb')
        decoder.assert_not_called()
        # check with decode
        open.reset_mock()
        open.return_value.read.return_value = mock_bytestring
        result = pdftk._get_file_contents('path', decode=True)
        self.assertEqual(result, 'decoded')
        open.assert_called_once_with('path', 'rb')
        decoder.assert_called_once_with('utf-2000')

    def test_parse_fdf(self):
        pdftk = PDFTKWrapper()
        results = list(pdftk.parse_fdf_fields(FDF_STR_SAMPLE))
        self.assertListEqual(results, PARSED_FDF_FIELDS)

    def test_parse_data_fields(self):
        pdftk = PDFTKWrapper()
        results = list(pdftk.parse_data_fields(
            DATA_FIELDS_STR_SAMPLE))
        self.assertListEqual(results, PARSED_DATA_FIELDS)

    @patch('builtins.open')
    def test_fill_pdf(self, fake_open):
        pdftk = PDFTKWrapper()
        fake_answers = Mock()
        fake_path = "some/fake/path.pdf"

        coerce_to_file_path = Mock(return_value=fake_path)
        pdftk._coerce_to_file_path = coerce_to_file_path

        fake_insertions = Mock()
        gen_answer_insertions = Mock(return_value=fake_insertions)
        pdftk._generate_answer_insertions = gen_answer_insertions

        fake_fdf_str = Mock()
        patch_fdf_with_insertions = Mock(return_value=fake_fdf_str)
        pdftk._patch_fdf_with_insertions = patch_fdf_with_insertions

        fake_output_path = Mock()
        load_patched_fdf = Mock(return_value=fake_output_path)
        pdftk._load_patched_fdf_into_pdf = load_patched_fdf

        fake_read_results = Mock()
        fake_open.return_value = Mock(
            read=Mock(
                return_value=fake_read_results)
        )

        clean_up_tmp_files = Mock()
        pdftk.clean_up_tmp_files = clean_up_tmp_files

        # run the method
        result = pdftk.fill_pdf(fake_path, fake_answers)

        coerce_to_file_path.assert_called_with(fake_path)
        gen_answer_insertions.assert_called_with(fake_path, fake_answers)
        patch_fdf_with_insertions.assert_called_with(fake_insertions)
        load_patched_fdf.assert_called_with(fake_path, fake_fdf_str)
        fake_open.assert_called_with(fake_output_path, 'rb')
        clean_up_tmp_files.assert_called_with()
        self.assertEqual(result, fake_read_results)

        pdftk.clean_up = False
        pdftk.fill_pdf(fake_path, fake_answers)
        clean_up_tmp_files.reset_mock()
        clean_up_tmp_files.assert_not_called()

    def test_fill_pdf_many(self):
        #vars
        pdftk = PDFTKWrapper()
        fake_answer = Mock()
        fake_multiple_answers = [fake_answer]

        #ensure self.clean_up value is preserved
        fake_clean_up = pdftk.clean_up
        _fake_clean_up_setting = fake_clean_up
        fake_clean_up = False
        fake_clean_up = _fake_clean_up_setting

        #pdf path (should be same as in fill_pdf)
        fake_path = "some/fake/path.pdf"

        coerce_to_file_path = Mock(return_value=fake_path)
        pdftk._coerce_to_file_path = coerce_to_file_path
        #for loop
        fake_fill_pdf = Mock()
        pdftk.fill_pdf = fake_fill_pdf

        fake_filled_pdf = Mock()
        pdftk.fill_pdf.return_value = fake_filled_pdf
        fake_write_tmp_file = Mock(return_value=fake_path)
        pdftk._write_tmp_file = fake_write_tmp_file

        #join_pdfs
        fake_join_pdfs = Mock()
        pdftk.join_pdfs = fake_join_pdfs

        #run the method
        result = pdftk.fill_pdf_many(fake_path, fake_multiple_answers)
        self.assertEqual(pdftk.clean_up, fake_clean_up)
        coerce_to_file_path.assert_called_with(fake_path)
        fake_fill_pdf.assert_called_with(fake_path, fake_answer)
        fake_write_tmp_file.assert_called_with(bytestring=fake_filled_pdf)
        fake_join_pdfs.assert_called_with([fake_path])