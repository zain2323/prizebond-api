from api import ma
from marshmallow import validate, validates, ValidationError, fields
from api.models import User


class UserSchema(ma.Schema):
    class Meta:
        ordered = True
        description = "Represents the attributes of the user object"
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=64)])
    email = fields.Email(required=True, validate=[validate.Length(max=120),
                         validate.Email()])
    password = fields.String(required=True, validate=validate.Length(min=8),
                             load_only=True)
    registered_at = fields.DateTime(dump_only=True)
    confirmed = fields.Boolean(dump_only=True)

    @validates("email")
    def validate_email(self, value):
        user = User.query.filter_by(email=value).first()
        if user is not None:
            return ValidationError("This email is already in use")

    @validates("name")
    def validate_name(self, value):
        if not value[0].isalpha():
            raise ValidationError("Name must start with a letter")
