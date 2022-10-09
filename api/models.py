from api import db, login_manager
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import jwt
import secrets
from flask import current_app as app
from flask_login.mixins import UserMixin
import json
from celery.result import AsyncResult


userbond = db.Table(
    "userbond",
    db.Column('user_id', db.Integer,
              db.ForeignKey('user.id', ondelete='CASCADE'),
              primary_key=True, nullable=False),
    db.Column('bond_id', db.Integer,
              db.ForeignKey('bond.id', ondelete="RESTRICT"),
              primary_key=True, nullable=False)
)


class Bond(db.Model):
    __tablename__ = 'bond'
    __table_args__ = (
        db.UniqueConstraint('denomination_id', 'serial', name="unique_bond"),
    )
    id = db.Column(db.Integer, primary_key=True)
    denomination_id = db.Column(
        db.Integer,
        db.ForeignKey('denomination.id', ondelete='RESTRICT'), nullable=False
    )
    serial = db.Column(db.String(6), nullable=False)
    winning_bond = db.relationship("WinningBond", backref="bonds", lazy=True)

    def __repr__(self):
        return f"{self.serial}"

    def get_users(self):
        return self.user.all()

    def is_bond_holder(self, user):
        return self.user.filter(userbond.c.user_id == user.id).count() > 0


class Denomination(db.Model):
    __tablename__ = 'denomination'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, index=True, unique=True, nullable=False)
    prize = db.relationship("Prize", backref="price", lazy="dynamic")
    bonds = db.relationship("Bond", backref="price", lazy=True)
    updated_lists = db.relationship("UpdatedLists", backref="price", lazy=True)
    drawdate = db.relationship("DrawDate", backref="price", lazy=True)

    def __repr__(self):
        return f"{self.price}"

    def first(self):
        return self.prize.filter_by(position=1).first()

    def second(self):
        return self.prize.filter_by(position=2).first()

    def third(self):
        return self.prize.filter_by(position=3).first()


class Prize(db.Model):
    __tablename__ = 'prize'
    __table_args__ = (
        db.UniqueConstraint("denomination_id", "prize", name="unique_prize"),
    )
    id = db.Column(db.Integer, primary_key=True)
    denomination_id = db.Column(
        db.Integer,
        db.ForeignKey('denomination.id', ondelete='CASCADE'), nullable=False
    )
    prize = db.Column(db.Integer, index=True, nullable=False, unique=True)
    position = db.Column(db.Integer, nullable=False, index=True)
    winning_bond = db.relationship("WinningBond", backref="prize", lazy=True)

    def __repr__(self):
        return f"{self.prize}"


class DrawDate(db.Model):
    __tablename__ = 'drawdate'
    __table_args__ = (db.UniqueConstraint('date', 'denomination_id',
                      name="unique_drawdate"),)
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    denomination_id = db.Column(
        db.Integer,
        db.ForeignKey("denomination.id", ondelete="CASCADE"), nullable=False
    )
    winningbond = db.relationship(
        "WinningBond", backref="date", lazy="dynamic")
    updated_lists = db.relationship("UpdatedLists", backref="date", lazy=True)

    def __repr__(self):
        return f"{self.date}"


class UpdatedLists(db.Model):
    __tablename__ = "updatedlists"
    __table_args__ = (db.UniqueConstraint('date_id',
                      'denomination_id', name="unique_bond_list"),)
    id = db.Column(db.Integer, primary_key=True)
    date_id = db.Column(
        db.Integer,
        db.ForeignKey("drawdate.id", ondelete="CASCADE"), nullable=False
    )
    denomination_id = db.Column(
        db.Integer,
        db.ForeignKey("denomination.id", ondelete="CASCADE"), nullable=False
    )
    uploaded = db.Column(db.Boolean, default=False)

    def first(self):
        price = self.price
        return self.date.winningbond.\
            filter(WinningBond.prize == price.first()).first().bonds

    def second(self):
        price = self.price
        winners = self.date.winningbond.\
            filter(WinningBond.prize == price.second()).all()
        return [winner.bonds for winner in winners]

    def third(self):
        price = self.price
        winners = self.date.winningbond.\
            filter(WinningBond.prize == price.third()).all()
        return [winner.bonds for winner in winners]

    @staticmethod
    def latest(denomination):
        # Returns the latest listing
        listing = UpdatedLists.query.\
            filter_by(price=denomination, uploaded=True).all()
        if len(listing) > 0:
            return listing[-1]
        else:
            return None

    def __repr__(self):
        return f"Date: {self.date} Price: {self.price}"


class DrawLocation(db.Model):
    __tablename__ = "drawlocation"
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(20), nullable=False,
                         index=True, unique=True)
    winningbond = db.relationship("WinningBond", backref="location", lazy=True)

    def __repr__(self):
        return f"{self.location}"


class DrawNumber(db.Model):
    __tablename__ = "drawnumber"
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False, unique=True)
    winningbond = db.relationship("WinningBond", backref="number", lazy=True)

    def __repr__(self):
        return f"{self.number}"


class WinningBond(db.Model):
    __tablename__ = 'winningbond'
    __table_args__ = (
        db.UniqueConstraint('bond_id', 'prize_id', 'date_id',
                            name="unique_winner"),)
    id = db.Column(db.Integer, primary_key=True)
    bond_id = db.Column(db.Integer, db.ForeignKey('bond.id',
                        ondelete="RESTRICT"), nullable=False)
    prize_id = db.Column(db.Integer, db.ForeignKey('prize.id',
                         ondelete="RESTRICT"), nullable=False)
    date_id = db.Column(db.Integer, db.ForeignKey('drawdate.id',
                        ondelete="RESTRICT"), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey("drawlocation.id",
                            ondelete="RESTRICT"), nullable=False)
    draw_id = db.Column(db.Integer, db.ForeignKey("drawnumber.id",
                        ondelete="RESTRICT"), nullable=False)

    def __repr__(self):
        return f"""Bond:{self.bonds}, Prize:{self.prize}, Date:{self.date}"""


class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(64), nullable=False, index=True)
    access_expiration = db.Column(db.DateTime, nullable=False)
    refresh_token = db.Column(db.String(64), nullable=False, index=True)
    refresh_expiration = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"),
                        nullable=False, index=True)

    def generate(self):
        self.access_token = secrets.token_urlsafe()
        self.access_expiration = datetime.utcnow() \
            + timedelta(minutes=app.config.get("ACCESS_TOKEN_MINUTES"))
        self.refresh_token = secrets.token_urlsafe()
        self.refresh_expiration = datetime.utcnow() \
            + timedelta(days=app.config.get("REFRESH_TOKEN_DAYS"))

    def _expire(self):
        self.access_expiration = datetime.utcnow()
        self.refresh_expiration = datetime.utcnow()

    @staticmethod
    def expire(tokens):
        for token in tokens:
            token._expire()

    def is_expired(self):
        return self.access_expiration < datetime.utcnow()

    @staticmethod
    def clean():
        """Remove any tokens that have been expired for more than a day"""
        yesterday = datetime.utcnow() - timedelta(days=1)
        Token.query.filter(Token.refresh_expiration < yesterday).delete()

    def __repr__(self):
        return f"Access Token: {self.access_token}"


class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), index=True, unique=True,
                     default="user", nullable=False)
    user = db.relationship("User", backref="role", lazy=True)

    def __repr__(self):
        return f"{self.name}"


@login_manager.user_loader
def load_user(user_id):
    return User.get_user(user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(102), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow,
                              nullable=False)
    confirmed = db.Column(db.Boolean, default=False, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False,
                        default=2)
    token = db.relationship("Token", backref="user", lazy=True)
    bonds = db.relationship(
        "Bond", secondary=userbond,
        primaryjoin=(userbond.c.user_id == id),
        secondaryjoin=(userbond.c.bond_id == Bond.id),
        backref=db.backref("user", lazy='dynamic'),
        lazy='dynamic', cascade="all, delete")
    notifications = db.relationship(
        "Notification", backref="user", lazy="dynamic")

    def __repr__(self):
        return f"Name: {self.name} Email: {self.email}"

    def add_bond(self, bond):
        self.bonds.append(bond)

    def remove_bond(self, bond):
        self.bonds.remove(bond)

    def get_bonds(self):
        return self.bonds.all()

    def get_bonds_by_denomination(self, denomination):
        return self.bonds.filter_by(price=denomination).all()

    @staticmethod
    def get_user(id):
        return User.query.get(id)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, plain_password):
        self.password_hash = generate_password_hash(plain_password)

    def verify_password(self, plain_password):
        return check_password_hash(self.password_hash, plain_password)

    def generate_auth_token(self):
        token = Token(user=self)
        token.generate()
        return token

    @staticmethod
    def verify_access_token(token):
        token = Token.query.filter_by(access_token=token).first()
        if token:
            if token.access_expiration > datetime.utcnow():
                return token.user

    @staticmethod
    def verify_refresh_token(refresh_token, access_token):
        token = Token.query.filter_by(
            access_token=access_token, refresh_token=refresh_token).first()
        if token:
            if token.refresh_expiration > datetime.utcnow():
                return token

            # someone tried to refresh with an expired token
            # revoke all tokens from this user as a precaution
            token.user.revoke_all()
            db.session.commit()

    def revoke_all(self):
        Token.query.filter(Token.user == self).delete()

    def encode_reset_token(self):
        try:
            payload = {
                "exp": datetime.utcnow() + timedelta(days=0, seconds=3600),
                "iat": datetime().utcnow(),
                "reset_email": self.email
            }

            return jwt.encode(
                payload,
                app.config.get("SECRET_KEY"),
                algorithm="HS256"
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_reset_token(auth_token):
        try:
            payload = jwt.decode(
                auth_token, app.config.get("SECRET_KEY"), algorithms=['HS256'])
            email = payload["reset_email"]
            return User.query.filter_by(email=email).first()
        except jwt.ExpiredSignatureError:
            return "Signature Expired"
        except jwt.InvalidTokenError:
            return "Invalid token"

    def add_notification(self, content):
        # self.notifications.filter_by(name=name).delete()
        notification = Notification.new(content, self)
        return notification


""" There will be two types of notification
1- Results announcements
2- Notifying the winners if we have

Right now only two but the schema should be flexible
enough to support adding new ones."""


class NotificationType(db.Model):
    __tablename__ = 'NotificationType'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32), unique=True, index=True)
    content = db.relationship("NotificationContent",
                              backref="type", lazy="dynamic")

    def __repr__(self):
        return f"Type: {self.type}"


class NotificationContent(db.Model):
    __tablename__ = 'NotificationContent'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.Text)
    payload = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow,
                           nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey("NotificationType.id"),
                        nullable=False, default=1)
    notification = db.relationship("Notification",
                                   backref="content", lazy="dynamic")

    @staticmethod
    def new(name, description, payload, type):
        notification_content = NotificationContent(
            name=name, description=description, payload=json.dumps(payload),
            type=type)
        db.session.add(notification_content)
        return notification_content

    def get_payload(self):
        return json.loads(str(self.payload))

    def __repr__(self):
        return f"""Name: {self.name} Payload: {self.payload}
                Description: {self.description} Type: {self.type}"""


class Notification(db.Model):
    __tablename__ = 'Notification'
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey("NotificationContent.id"),
                           nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    seen = db.Column(db.Boolean, default=False)
    seen_at = db.Column(db.DateTime, nullable=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow,
                        nullable=False)

    @staticmethod
    def new(content, user):
        notification = Notification(content=content, user=user)
        db.session.add(notification)
        return notification

    def __repr__(self):
        return f"Recipient: {self.user} Content: {self.content}"


class Tasks(db.Model):
    __tablename__ = "Tasks"
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    complete = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"id: {self.id} name: {self.name} complete: {self.complete}"

    def get_job(self):
        return AsyncResult(self.id, app=app.celery)
