from apifairy import authenticate, body, response, other_responses
from api.bond import bond
from api.auth.authentication import token_auth
from api.bond.schema import BondSchema, ReturnBondSchema, BondRangeSchema
from api.models import Bond
from api import db
from flask import abort


@bond.post("/bond")
@authenticate(token_auth)
@body(BondSchema)
@response(ReturnBondSchema)
def new(args):
    """Add bond"""
    user = token_auth.current_user()
    bond = Bond.query.filter_by(price=args["price"]).first()
    if not bond:
        bond = Bond(**args)
        db.session.add(bond)
    if not bond.is_bond_holder(user):
        user.add_bond(bond)
        db.session.commit()
    return bond


@bond.get("/bond")
@authenticate(token_auth)
@response(ReturnBondSchema(many=True))
def all():
    """Retrieve all bonds"""
    return Bond.query.all()


@bond.post("/bond/range")
@authenticate(token_auth)
@body(BondRangeSchema)
@response(ReturnBondSchema(many=True))
def add_range(args):
    """Add bond series"""
    user = token_auth.current_user()
    start = int(args["start"])
    end = int(args["end"])
    price = args["price"]
    bonds = []
    for serial in range(start, end+1):
        bond = Bond.query.filter_by(price=args["price"]).first()
        # if bond does not exists
        if not bond:
            bond = Bond(serial=serial, price=price)
            db.session.add(bond)
        # add bond only it is not owned by the user
        if not bond.is_bond_holder(user):
            user.add_bond(bond)
        bonds.append(bond)
    db.session.commit()
    return bonds


@bond.delete("/bond/<int:id>")
@authenticate(token_auth)
@other_responses({403: 'Not allowed to deleted this bond'})
def remove(id):
    """Remove bond"""
    user = token_auth.current_user()
    bond = Bond.query.filter_by(id=id).first_or_404()
    if not bond.is_bond_holder(user):
        abort(403)
    user.remove_bond(bond)
    db.session.commit()
    print("done")
    return '', 204


@bond.delete("/bond/range")
@authenticate(token_auth)
@body(BondRangeSchema)
@other_responses({403: 'Not allowed to deleted this bond'})
def remove_range(args):
    """Remove bond series"""
    user = token_auth.current_user()
    start = int(args["start"])
    end = int(args["end"])
    price = args["price"]
    for serial in range(start, end+1):
        bond = Bond(serial=serial, price=price)
        if not bond.is_bond_holder(user):
            abort(403)
    db.session.commit()
    return '', 204
