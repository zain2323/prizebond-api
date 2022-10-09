from api.models import Denomination
from flask import render_template, current_app as app
# from api.tasks import send_email


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


def send_confirmation_email(user):
    subject = "Confirm your email"
    sender = app.config["MAIL_USERNAME"]
    text_body = render_template("email/email_confirmation.txt",
                                user=user.name)
    html_body = render_template("email/email_confirmation.html",
                                user=user.name)
    recipient = user.email
    # send_email(subject, sender, recipient, text_body, html_body)
