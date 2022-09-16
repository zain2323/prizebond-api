from api.models import Bond, Denomination


def make_bond_info_response(denominations):
    response = []
    for id in denominations:
        resp = {}
        price = Denomination.query.get(id[0]).price
        count = Bond.query.filter_by(denomination_id=id[0]).count()
        resp["price"] = price
        resp["total"] = count
        resp["worth"] = price * count
        response.append(resp)
    return response
