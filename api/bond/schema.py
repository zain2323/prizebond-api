from api import ma
from marshmallow import fields, validate, validates, ValidationError, post_load
from api.models import Denomination
from api.bond.utils import remove_white_spaces


class DenominationSchema(ma.Schema):
    class Meta:
        ordered = True
        description = "This schema represents the attributes of the denomination"
    id = fields.Integer(dump_only=True)
    price = fields.Integer()


class AddBondSchema(ma.Schema):
    class Meta:
        ordered = True
        description = "This schema represents the attributes of the bond"
    serial = fields.String(
            required=True,
            validate=[validate.Length(equal=6, error="Serials must contain exactly 6 digits")])
    price = fields.Integer(required=True, load_only=True)

    @validates("price")
    def validate_price(self, value):
        price = Denomination.query.filter_by(price=value).first()
        if not price:
            raise ValidationError("Invalid price selected")

    @validates("serial")
    def validate_serial(self, value):
        serials = remove_white_spaces(value)
        for serial in serials:
            if not serial.isdigit():
                raise ValidationError("Invalid serials")

    @post_load
    def wrap_denomination(self, data, **kwargs):
        data["price"] = Denomination.query.filter_by(price=data["price"]).first()
        return data


class ReturnBondSchema(ma.Schema):
    class Meta:
        ordered = True
        description = "This schema represents the attributes of the bond when returned"
    id = fields.Integer(dump_only=True)
    serial = fields.String()
    price = fields.Nested(DenominationSchema)

