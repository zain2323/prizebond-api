from apifairy import authenticate, body, response
from api.bond import bond
from api.auth.authentication import token_auth
from api.bond.schema import AddBondSchema, ReturnBondSchema
from api.models import Bond
from api import db


@bond.post("/bond")
@authenticate(token_auth)
@body(AddBondSchema)
@response(ReturnBondSchema)
def new(args):
    """Add bond     """
    user = token_auth.current_user()
    bond = Bond(**args)
    db.session.add(bond)
    user.add_bond(bond)
    db.session.commit()
    return bond

@bond.post("/bond/range")
@authenticate(token_auth)
@body(AddBondSchema)
@response(ReturnBondSchema)
def upload_range():
    pass

