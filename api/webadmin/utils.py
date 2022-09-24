from api.models import Denomination, Prize, DrawDate
from pathlib import Path
import secrets


def load_denominations():
    denominations = Denomination.query.all()
    return [d.price for d in denominations]


def load_date(denomination):
    try:
        denomination = int(denomination)
    except Exception:
        return []
    bond_price = Denomination.query.filter_by(price=denomination).first()
    date = DrawDate.query.filter_by(price=bond_price).all()
    return [str(d.date) for d in date]


def load_prizes():
    prizes = Prize.query.all()
    return [d.prize for d in prizes]


def load_prizes_by_price(denomination):
    price = Denomination.query.filter_by(price=denomination).first()
    prizes = Prize.query.filter_by(price=price).all()
    return prizes


def load_user_bonds(user):
    bonds = user.get_bonds()
    return [bond.serial for bond in bonds]


def load_denomination_prizes(price):
    denominations = Denomination.query.filter_by(price=price).first()
    bond_prizes = Prize.query.filter_by(
        bond_price_id=denominations.id).all()
    return [bond_prize.prize for bond_prize in bond_prizes]


def save_picture(file_data):
    '''
    This saves the thumbnail picture of the product in the
    static/product_pictures directory. Picture is being renamed to
    the randomly chosen 32 bit string in order to avoid the
    naming clash.
    '''
    try:
        path = Path('./api/static/results')
    except FileNotFoundError:
        raise FileNotFoundError("Path is invalid or does not exist.")
    try:
        _, ext = file_data.filename.split(".")
    except Exception():
        ext = file_data.filename.split(".")[-1]
    file_name_with_ext = generate_hex_name() + "." + ext
    path = path.joinpath(file_name_with_ext)
    file_data.save(path)
    return file_name_with_ext


def delete_picture(img_name):
    try:
        path = Path("./api/static/results/" + img_name)
    except FileNotFoundError:
        raise FileNotFoundError("Path is invalid or does not exist.")
    if path.exists():
        path.unlink()
    else:
        raise FileNotFoundError("File with the given name do not exists.")


def generate_hex_name():
    '''
    Returns the 32 bit random digits
    '''
    return secrets.token_hex(32)


def normalize_serials(serials):
    serials = serials.split(",")
    serials = list(map(str.strip, serials))
    while ("" in serials):
        serials.remove("")
    return serials


def count_leading_zeroes(serial):
    count = 0
    for char in serial:
        if char != '0':
            break
        count += 1
    return count


def append_leading_zeroes(serial_start, serial_end):
    diff = abs(len(serial_start) - len(serial_end))
    zeroes = ""
    for i in range(diff):
        zeroes += '0'
    return zeroes + serial_end
