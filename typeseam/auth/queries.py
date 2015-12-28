from typeseam.app import db
from typeseam.auth.serializers import UserSerializer


user_serializer = UserSerializer()

def create_user(data):
    model, errors = user_serializer.load(data, session=db.session)
    if errors:
        return errors
    db.session.add(model)
    db.session.commit()
    return model