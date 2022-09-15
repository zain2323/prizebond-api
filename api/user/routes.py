from api.user import user
from api.models import User
from apifairy import authenticate, body, response
from api import db
from api.user.schema import UserSchema
from api.auth.authentication import token_auth
from typing import Annotated


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


@user.get("/user/<int:id>")
@authenticate(token_auth)
@response(UserSchema)
def get(id: Annotated[int, 'The id of the user to retrieve.']):
    """Retrieve user by id"""
    return User.query.get(id)
