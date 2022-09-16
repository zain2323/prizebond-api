from api import ma
from marshmallow import (fields, validate, validates, ValidationError, 
                         post_load, validates_schema)
from api.models import Denomination
from api.bond.utils import remove_white_spaces


def validate_serial(value):
    serials = remove_white_spaces(value)
    for serial in serials:
        if not serial.isdigit() or len(serial) != 6:
            raise ValidationError("Invalid serials")


class DenominationSchema(ma.Schema):
    class Meta:
        ordered = True
        description = """This schema represents the attributes of the
                         denomination"""
    id = fields.Integer(dump_only=True)
    price = fields.Integer()


class AddBondSchema(ma.Schema):
    class Meta:
        ordered = True
        description = "This schema represents the attributes of the bond"
    serial = fields.String(
            required=True,
            validate=[
                validate.Length(equal=6,
                                error="Serials must contain exactly 6 digits"),
                validate_serial]
            )
    price = fields.Integer(required=True, load_only=True)

    @validates("price")
    def validate_price(self, value):
        price = Denomination.query.filter_by(price=value).first()
        if not price:
            raise ValidationError("Invalid price selected")

    @post_load
    def wrap_denomination(self, data, **kwargs):
        data["price"] = Denomination.query.filter_by(price=data["price"]).first()
        return data


class ReturnBondSchema(ma.Schema):
    class Meta:
        ordered = True
        description = """This schema represents the attributes of the bond when
                         returned"""
    id = fields.Integer(dump_only=True)
    serial = fields.String()
    price = fields.Nested(DenominationSchema)


class AddBondRangeSchema(ma.Schema):
    class Meta:
        ordered = True
        description = """This schema represents the attributes required when
                         adding a new series"""
    id = fields.Integer(dump_only=True)
    start = fields.String(
        required=True,
        validate=[validate.Length(
                                equal=6,
                                error="Serials must contain exactly 6 digits"),
                  validate_serial]
    )
    end = fields.String(
        required=True,
        validate=[validate.Length(
            equal=6,
            error="Serials must contain exactly 6 digits"),
                  validate_serial]
    )
    price = fields.Integer()

    @validates("price")
    def validate_price(self, value):
        price = Denomination.query.filter_by(price=value).first()
        if not price:
            raise ValidationError("Invalid price selected")

    @post_load
    def wrap_denomination(self, data, **kwargs):
        data["price"] = Denomination.query.filter_by(price=data["price"]).first()
        return data

    @validates_schema
    def validate_range(self, data, **kwargs):
        try:
            start = data["start"]
            end = data["end"]
        except:
            raise ValidationError("Invalid serials")

        if start > end:
            raise ValidationError("End must be greater than start")
