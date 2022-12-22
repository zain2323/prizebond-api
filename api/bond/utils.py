from werkzeug.exceptions import Forbidden
from flask import current_app as app


def remove_white_spaces(serials):
    serials = serials.split(",")
    serials = list(map(str.strip, serials))
    while ("" in serials):
        serials.remove("")
    return serials


def make_search_response(winner):
    return {
        "serial":  winner.bonds.serial,
        "denomination":  winner.bonds.price.price,
        "position": winner.prize.position,
        "prize":  winner.prize.prize,
        "draw_date": winner.date.date,
        "draw_num":  winner.number.number,
        "location":  winner.location
    }


def make_latest_result_response(listing):
    return {
        "denomination": listing.price,
        "draw_date": listing.date,
        "first": listing.first(),
        "second": listing.second()
    }


def confirm_email_required(token_auth):
    if not app.debug:
        user = token_auth.current_user()
        if not user.confirmed:
            raise Forbidden(
                description="""You need to confirm email before you can access the website functionality.""")