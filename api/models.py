from api import db
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import jwt
import secrets

class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(64), nullable=False, index=True)
    access_expiration = db.Column(db.DateTime, nullable=False)
    refresh_token = db.Column(db.String(64), nullable=False, index=True)
    refresh_expiration = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    def generate(self):
        self.access_token = secrets.token_urlsafe()
        self.access_expiration = datetime.utcnow() \
            + timedelta(minutes=app.config.get("ACCESS_TOKEN_MINUTES"))
        self.refresh_token = secrets.token_urlsafe()
        self.refresh_expiration = datetime.utcnow() \
            + timedelta(days=app.config.get("ACCESS_TOKEN_DAYS"))
    
    def expire(self):
        self.access_expiration = datetime.utcnow()
        self.refresh_expiration = datetime.utcnow()
    
    @staticmethod
    def clean():
        """Remove any tokens that have been expired for more than a day"""
        yesterday = datetime.utcnow() - timedelta(days=1)
        db.session.remove(Token.query.filter_by(refresh_expiration < yesterday))
    
    def __repr__(self):
        return f"Access Token: {self.access_token}"

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(102), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    confirmed = db.Column(db.Boolean, default=False, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)
    
    @staticmethod
    def get_user(id):
        return User.query.get(id)

    def set_password(self, plain_password):
        self.password = self.generate_hashed_password(plain_password)
    
    @staticmethod
    def generate_hashed_password(plain_password):
        return generate_password_hash(plain_password)

    def verify_password(self,plain_password):
        return check_password_hash(self.password, plain_password)

    def generate_auth_token(self):
        token = Token(user=self)
        token.generate()
        return token

    @staticmethod
    def verify_access_token(token):
        user = User.query.filter_by(token=token).first()
        if token:
            if token.access_expiration > datetime.utcnow():
                return token.user

    @staticmethod
    def verify_refresh_token(refresh_token, access_token):
        token = Token.query.filterb_by(access_token=access_token, refresh_token=refresh_token)
        if token:
            if token.refresh_expiration > datetime.utcnow():
                return token

            # someone tried to refresh with an expired token
            # revoke all tokens from this user as a precaution
            token.user.revoke_all()
            db.session.commit()
    
    def revoke_all(self):
        db.session.remove(Token.query.filter_by(user=self))
    
    def encode_auth_token(self, user_id):
        try:
            payload = {
                "exp": datetime.utcnow() + timedelta(days=0, seconds=3600),
                "iat": datetime().utcnow(),
                "sub": user_id
            }

            return jwt.encode(
                payload,
                app.config.get("SECRET_KEY"),
                algorithm="HS256"
            )
        except Exception as e:
            return e
    
    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(auth_token, app.config.get("SECRET_KEY"))
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            return "Signature Expired"
        except jwt.InvalidTokenError:
            return "Invalid token"

    def __repr__(self):
        return f"{self.name}, {self.email}"