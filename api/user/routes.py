from api.user import user
from api.models import User, Bond
from apifairy import authenticate, body, response
from api import db
from api.user.schema import UserSchema
from api.user.utils import make_bond_info_response
from api.auth.authentication import token_auth
from typing import Annotated
from api.bond.schema import ReturnBondSchema, BondInfoSchema


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
