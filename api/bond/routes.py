from apifairy import authenticate, body, response, other_responses
from api.bond import bond
from api.auth.authentication import token_auth
from api.bond.schema import (BondSchema, ReturnBondSchema,
                             BondRangeSchema, DenominationSchema,
                             DrawDateSchema, WinnerSchema, LatestResultSchema)
from api.models import Bond, Denomination, DrawDate, WinningBond, UpdatedLists
from api import db
from flask import abort, request
from typing import Annotated
from api.bond.utils import make_search_response, make_latest_result_response


def add(user, args):
    """Helper function to add bonds"""
    bond = Bond.query.filter_by(
        price=args["price"], serial=args["serial"]).first()
    if not bond:
        bond = Bond(**args)
        db.session.add(bond)
    if not bond.is_bond_holder(user):
        user.add_bond(bond)
    return bond


@bond.post("/bond")
@authenticate(token_auth)
@body(BondSchema)
@response(ReturnBondSchema)
def new(args):
    """Add bond"""
    user = token_auth.current_user()
    bond = add(user, args)
    db.session.commit()
    return bond


@bond.post("/bonds")
@authenticate(token_auth)
@body(BondSchema(many=True))
@response(ReturnBondSchema(many=True))
def add_bonds(args_list):
    """Add bonds"""
    user = token_auth.current_user()
    bonds = []
    for args in args_list:
        bond = add(user, args)
        bonds.append(bond)
    db.session.commit()
    return bonds


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
        bond = Bond.query.filter_by(
            price=args["price"], serial=str(serial)).first()
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


@bond.get("/denominations")
@authenticate(token_auth)
@response(DenominationSchema(many=True))
def denominations():
    """Retrieve all denominations"""
    return Denomination.query.all()


@bond.get("/drawdate/<int:id>")
@authenticate(token_auth)
@response(DrawDateSchema(many=True))
def draw_date(id: Annotated[int, 'Denomination id.']):
    """Retrieve draw date"""
    price = Denomination.query.get_or_404(id)
    return DrawDate.query.filter_by(price=price).all()


@bond.get("/search")
@authenticate(token_auth)
@response(WinnerSchema)
def search():
    """Check if serial is in the winning list"""
    serial = request.args.get("serial")
    price = request.args.get("price")
    date = request.args.get("date")
    denomination = Denomination.query.filter_by(price=price).first()
    bond = Bond.query.filter_by(serial=serial, price=denomination).first()
    draw_date = DrawDate.query.filter_by(date=date).first()
    winner = WinningBond.query.filter_by(
        bonds=bond, date=draw_date).first()
    if winner:
        return make_search_response(winner)
    else:
        return {}


@bond.get("/search/serials")
@authenticate(token_auth)
@response(WinnerSchema(many=True))
def search_all_serials():
    """Search for results"""
    price = request.args.get("price")
    date = request.args.get("date")

    user = token_auth.current_user()
    denomination = Denomination.query.filter_by(price=price).first()
    bonds = user.get_bonds_by_denomination(denomination)
    draw_date = DrawDate.query.filter_by(date=date).first()

    response = []
    for serial in bonds:
        winner = WinningBond.query.filter_by(
            bonds=serial, date=draw_date).first()
        if winner:
            response.append(make_search_response(winner))
    return response


@bond.get("/search/serials/all")
@authenticate(token_auth)
@response(WinnerSchema(many=True))
def search_all():
    """Search all of your serials"""
    user = token_auth.current_user()
    bonds = user.get_bonds()
    response = []
    for serial in bonds:
        winners = WinningBond.query.filter_by(bonds=serial).all()
        for winner in winners:
            if winner:
                response.append(make_search_response(winner))
    return response


@bond.get("/search/serials/denomination")
@authenticate(token_auth)
@response(WinnerSchema(many=True))
def search_by_denomination():
    """Search all of your serials"""
    price = request.args.get("price")
    user = token_auth.current_user()
    denomination = Denomination.query.filter_by(price=price).first()
    bonds = user.get_bonds_by_denomination(denomination)
    response = []
    for serial in bonds:
        winners = WinningBond.query.filter_by(bonds=serial).all()
        for winner in winners:
            if winner:
                response.append(make_search_response(winner))
    return response


@bond.get("/result")
@response(WinnerSchema(many=True))
def retrieveResultsList():
    """Retrieve all of the result lists"""
    response = []
    winners = WinningBond.query.limit(50)
    for winner in winners:
        response.append(make_search_response(winner))
    return response


@bond.get("/winners")
@response(LatestResultSchema(many=True))
def retreiveLatestWinners():
    """Retrieve latest result listings"""
    response = []
    denominations = Denomination.query.all()
    for denomination in denominations:
        listing = UpdatedLists.latest(denomination)
        if listing:
            response.append(make_latest_result_response(listing))
    return response
