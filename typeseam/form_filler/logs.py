from flask import current_app

LOG_LEVELS = {
    'debug':    10,
    'info':     20,
    'warning':  30,
    'error':    40,
    'critical': 50,
}

class SimpleLogEvent:
    def __init__(self, event_type="EVENT", level='info'):
        self.level = level
        self.level_code = LOG_LEVELS[level]
        self.event_type = event_type

    def __call__(self, msg, *args, **kwargs):
        current_app.logger.log(
            self.level_code,
            self.event_type + " " + msg, *args, **kwargs)


log_typeform_get = SimpleLogEvent("TYPEFORM_GET_RESPONSES")
log_seamless_post = SimpleLogEvent("SEAMLESS_POST_RESPONSE")
log_seamless_get_pdf = SimpleLogEvent("SEAMLESS_PDF_RESPONSE")
log_seamless_pdf_missing = SimpleLogEvent("SEAMLESS_PDF_MISSING", 'warning')