from api.commands import commands   
from api.models import Role
from api import db

@commands.cli.command()
def setup_database():
    """Inserts the necessary data to to database""" 
    insert_roles()
    db.session.commit()
    print('Data inserted')

def insert_roles():
    admin = Role(name="admin")
    user = Role(name="user")
    db.session.add(admin)
    db.session.add(user)
    db.session.commit()