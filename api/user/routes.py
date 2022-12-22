from api.user import user
from api.models import User, Denomination, Notification, Token
from apifairy import authenticate, body, response
from api import api_fairy, db, socketIO
from api.user.schema import UserSchema, UpdateUserSchema, NotificationSchema
from api.user.utils import make_bond_info_response, send_confirmation_email, confirm_email_required
from api.auth.authentication import token_auth
from typing import Annotated
from api.bond.schema import (
    ReturnBondSchema, BondInfoSchema)
from flask import abort
from flask_socketio import emit, ConnectionRefusedError
import json


@user.post("/users")
@body(UserSchema)
@response(UserSchema, 201)
def new(args, spec):
    """Register a new user"""
    user = User(**args)
    db.session.add(user)
    db.session.commit()
    # send_confirmation_email(user)
    return user


@user.put("/confirm_email/<string:token>")
def confirm_email(token):
    user = User.decode_jwt_token(token)
    if not user:
        return abort(403)
    user.confirmed = True
    db.session.commit()
    return {}, 204


@user.get("/users")
@authenticate(token_auth)
@response(UserSchema(many=True))
def all():
    """Retrieve all users"""
    confirm_email_required(token_auth)
    return User.query.all()


@user.get("/user/<int:id>")
@authenticate(token_auth)
@response(UserSchema)
def get(id: Annotated[int, 'The id of the user to retrieve.']):
    """Retrieve user by id"""
    confirm_email_required(token_auth)
    return User.query.get(id) or abort(404)


@user.get("/user/bonds")
@authenticate(token_auth)
@response(ReturnBondSchema(many=True))
def bonds():
    """Retrieve user bonds"""
    confirm_email_required(token_auth)
    user = token_auth.current_user()
    return user.get_bonds()


@user.get("/user/bonds/<int:id>")
@authenticate(token_auth)
@response(ReturnBondSchema(many=True))
def bonds_by_denomination(id: Annotated[int, 'Denomination id']):
    """Retrieve user bonds by denomination id"""
    confirm_email_required(token_auth)
    user = token_auth.current_user()
    denomination = Denomination.query.get_or_404(id)
    return user.get_bonds_by_denomination(denomination)


@user.get("/user/bonds/info")
@authenticate(token_auth)
@response(BondInfoSchema(many=True))
def bond_info():
    """Retrieve bonds info"""
    confirm_email_required(token_auth)
    user = token_auth.current_user()
    bonds = user.bonds
    response = make_bond_info_response(bonds)
    return response


@user.get("/about")
@authenticate(token_auth)
@response(UserSchema)
def me():
    """Retrieve the authenticated user"""
    confirm_email_required(token_auth)
    return token_auth.current_user()


@user.put("/about")
@authenticate(token_auth)
@body(UpdateUserSchema)
@response(UserSchema)
def put(args):
    """Update user info"""
    confirm_email_required(token_auth)
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
    db.session.commit()
    return user


# This sends notification to the connected client using websockets
@socketIO.on("fetchNotifications")
def send_notfications(token):
    token = Token.query.filter_by(access_token=token).first()
    user = token.user
    if token is None or user is None:
        raise ConnectionRefusedError("authorization failed")
    notifications = user.\
        notifications.\
        filter(Notification.seen == False).\
        order_by(Notification.sent_at.asc()).all()
    response = []
    for n in notifications:
        payload = json.loads(n.content.payload)
        response.append({
            "id": n.id,
            "name": n.content.name,
            "description": n.content.description,
            "payload": payload,
            "seen": n.seen,
            "seen_at": n.seen_at
        })
    response = NotificationSchema(many=True).dump(response)
    emit("notifications", response)


# This updates the notification status if the client has seen it.
@socketIO.on("update_seen_status")
def update_seen_status(token, notifications):
    token = Token.query.filter_by(access_token=token).first()
    user = token.user
    if token is None or user is None:
        raise ConnectionRefusedError("authorization failed")
    for n in notifications:
        notification = Notification.query.get_or_404(n["id"])
        notification.seen = True
    db.session.commit()
