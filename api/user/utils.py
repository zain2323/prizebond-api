from api.models import Denomination


def make_bond_info_response(bonds):
    response = []
    denominations = Denomination.query.all()
    for denomination in denominations:
        resp = {}
        price = denomination.price
        count = len(bonds.filter_by(price=denomination).all())
        resp["price"] = price
        resp["total"] = count
        resp["worth"] = price * count
        response.append(resp)
    return response
