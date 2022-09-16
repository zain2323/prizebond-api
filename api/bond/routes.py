from apifairy import authenticate, body, response
from api.bond import bond
from api.auth.authentication import token_auth
from api.bond.schema import AddBondSchema, ReturnBondSchema, AddBondRangeSchema
from api.models import Bond
from api import db


@bond.post("/bond")
@authenticate(token_auth)
@body(AddBondSchema)
@response(ReturnBondSchema)
def new(args):
    """Add bond"""
    user = token_auth.current_user()
    bond = Bond(**args)
    db.session.add(bond)
    user.add_bond(bond)
    db.session.commit()
    return bond


@bond.post("/bond/range")
@authenticate(token_auth)
@body(AddBondRangeSchema)
@response(ReturnBondSchema(many=True))
def add_range(args):
    """Add bond series"""
    user = token_auth.current_user()
    start = int(args["start"])
    end = int(args["end"])
    price = args["price"]
    bonds = []
    for serial in range(start, end+1):
        bond = Bond(serial=serial, price=price)
        db.session.add(bond)
        user.add_bond(bond)
        bonds.append(bond)
    db.session.commit()
    return bonds
