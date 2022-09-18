from api.auth import auth
from api.auth.authentication import basic_auth, token_auth
from apifairy import authenticate, body, other_responses, response
from api.models import User, Token
from api import db
from api.auth.schema import TokenSchema, EmptySchema
from flask import abort


@auth.post("/tokens")
@authenticate(basic_auth)
@response(TokenSchema)
@other_responses({401: 'Invalid username or password'})
def new():
    """Create new access and refresh tokens"""
    user = basic_auth.current_user()
    token = user.generate_auth_token()
    db.session.add(token)
    Token.clean()
    db.session.commit()
    return token


@auth.put("/tokens")
@body(TokenSchema)
@response(TokenSchema, description='Newly issued access and refresh tokens')
@other_responses({401: 'Invalid access or referesh token'})
def refresh(args):
    """Refresh an access token"""
    access_token = args["access_token"]
    refresh_token = args["refresh_token"]
    if not access_token or not refresh_token:
        abort(401)
    token = User.verify_refresh_token(refresh_token, access_token)
    if not token:
        abort(401)
    token.expire([token])
    new_token = token.user.generate_auth_token()
    db.session.add_all([token, new_token])
    db.session.commit()
    return new_token


@auth.delete("/tokens")
@authenticate(token_auth)
@response(EmptySchema, status_code=204, description='Token revoked')
@other_responses({401: "invalid access token"})
def revoke():
    """Revoke an access token"""
    token = token_auth.current_user().token
    if not token:
        abort(401)
    Token.expire(token)
    db.session.commit()
    return {}
