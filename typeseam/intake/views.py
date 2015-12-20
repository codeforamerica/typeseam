from typeseam.intake import blueprint

from .models import TypeformResponse

@blueprint.route('/', methods=['POST'])
def process_typeform_post():
    return 'Hello'

