from api.user import user
from api.models import User
from apifairy import authenticate, body, response
from api import db
from api.user.schema import UserSchema
from api.auth.authentication import token_auth

@user.post("/users")
@body(UserSchema)
@response(UserSchema, 201)
def new(args):
    """Register a new user"""
    user = User(**args)
    db.session.add(user)
    db.session.commit()
    return user


@user.get("/users")
@authenticate(token_auth)
@response(UserSchema(many=True))
def all():
    """Retrieve all users"""
    return User.query.all()
