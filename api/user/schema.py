from api import ma
from marshmallow import (validate, ValidationError,
                         validates_schema, fields)
from api.models import User


def validate_email(email):
    user = User.query.filter_by(email=email).first()
    if user is not None:
        raise ValidationError("This email is already in use")


def validate_name(name):
    if name and not name[0].isalpha():
        raise ValidationError("Name must start with a letter")


class UserSchema(ma.Schema):
    class Meta:
        ordered = True
        description = "Represents the attributes of the user object"
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True,
                         validate=[validate.Length(max=64), validate_name])
    email = fields.Email(required=True,
                         validate=[
                             validate.Length(
                                 max=120), validate.Email(), validate_email
                         ])
    password = fields.String(required=True,
                             validate=validate.Length(min=8), load_only=True)
    registered_at = fields.DateTime(dump_only=True)
    confirmed = fields.Boolean(dump_only=True)


class UpdateUserSchema(ma.Schema):
    class Meta:
        ordered = True
        description = """
        Represents the possible number attributes when updating the user"""
    name = fields.String(load_default=None, validate=[
                         validate.Length(max=64), validate_name])
    email = fields.Email(load_default=None, validate=[validate.Length(max=120),
                                                      validate.Email(),
                                                      validate_email])
    password = fields.String(
        load_default=None, validate=validate.Length(min=8))

    @validates_schema
    def validate_field_presence(self, data, **kwargs):
        if not (data["name"] or data["email"] or data["password"]):
            raise ValidationError("Not all of the fields can be None")


class ResultPayloadSchema(ma.Schema):
    class Meta:
        ordered = True,
        description = "Represents the attributes of the Notification object"
    price = fields.String()
    date = fields.String()


class NotificationSchema(ma.Schema):
    class Meta:
        ordered = True,
        description = "Represents the attributes of the Notification object"
    id = fields.Integer()
    name = fields.String()
    description = fields.String()
    payload = fields.Nested(ResultPayloadSchema())
    seen = fields.Boolean()
    seen_at = fields.DateTime(allow_none=True)
