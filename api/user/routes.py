from api.user import user
from api.models import User, Bond
from apifairy import authenticate, body, response, other_responses
from api import db
from api.user.schema import UserSchema, UpdateUserSchema
from api.user.utils import make_bond_info_response
from api.auth.authentication import token_auth
from typing import Annotated
from api.bond.schema import ReturnBondSchema, BondInfoSchema
from flask import abort


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
    return User.query.get(404) or abort(404)


@user.get("/user/bonds")
@authenticate(token_auth)
@response(ReturnBondSchema(many=True))
def bonds():
    """Retrieve user bonds"""
    user = token_auth.current_user()
    return user.get_bonds()


@user.get("/user/bonds/info")
@authenticate(token_auth)
@response(BondInfoSchema(many=True))
def bond_info():
    """Retrieve bonds info"""
    user = token_auth.current_user()
    bonds = user.bonds
    denomination_ids = bonds.\
                            with_entities(Bond.denomination_id).\
                            distinct().\
                            all()
    response = make_bond_info_response(denomination_ids)
    return response


@user.get("/about")
@authenticate(token_auth)
@response(UserSchema)
def me():
    """Retrieve the authenticated user"""
    return token_auth.current_user()


@user.put("/about")
@authenticate(token_auth)
@body(UpdateUserSchema)
@response(UserSchema)
def put(args):
    """Update your info"""
    email = args.get("email")
    password = args.get("password")
    name = args.get("name")
    user = token_auth.current_user()
    if email:
        user.email = email
    if name:
        user.name = name
    if password:
        user.password = password
    db.sesion.commit()
    return user
