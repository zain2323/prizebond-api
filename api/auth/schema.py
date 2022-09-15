from api import ma
from marshmallow import fields


class TokenSchema(ma.Schema):
    class Meta:
        ordered = True
        description = "This schema represents the attributes of the Token"

    access_token = fields.String(required=True)
    refresh_token = fields.String()


class EmptySchema(ma.Schema):
    pass
