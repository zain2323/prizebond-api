from api.commands import commands
from api.models import Role, Denomination, Prize, NotificationType
from api import db


@commands.cli.command()
def setup_database():
    """Inserts the necessary data to to database"""
    insert_roles()
    insert_denomination()
    insert_prize()
    insert_notification_types()
    db.session.commit()
    print('Data inserted')


def insert_roles():
    admin = Role(name="admin")
    user = Role(name="user")
    db.session.add(admin)
    db.session.add(user)
    db.session.commit()


def insert_denomination():
    price_list = [100, 200, 750, 1500]
    for price in price_list:
        denomination = Denomination(price=price)
        db.session.add(denomination)


def insert_prize():
    prize_dict = {
        "100": [700000, 200000, 1000],
        "200": [750000, 250000, 1250],
        "750": [1500000, 500000, 9300],
        "1500": [3000000, 1000000, 18500]
    }

    for price in prize_dict:
        denomination = Denomination.query.filter_by(price=int(price))
        prize_list = prize_dict.get(price)
        first = Prize(price=denomination, prize=prize_list[0], pos=1)
        second = Prize(price=denomination, prize=prize_list[1], pos=2)
        third = Prize(price=denomination, prize=prize_list[2], pos=3)
        db.session.add_all([first, second, third])


def insert_notification_types():
    result = NotificationType(type="result")
    winner = NotificationType(type="winner")
    db.session.add(result)
    db.session.add(winner)
    db.session.commit()
