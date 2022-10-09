from api import flask_celery, mail
from api.models import User, Denomination
from api.bond.schema import ReturnBondSchema
from flask_mail import Message


@flask_celery.celery.task(bind=True)
def export_bonds(self, user_id, denomination_id):
    """Background taks that exports all of the user bonds in pdf format
    and sends an email to the user after successful completion"""
    user = User.query.get_or_404(user_id)
    denomination = Denomination.query.get_or_404(denomination_id)
    bond_schema = ReturnBondSchema(many=True)
    for i in range(10):
        bonds = user.get_bonds_by_denomination(denomination)
        self.update_state(state="PROGRESS",
                          meta={"current": i, "total": 10})
    return {'bonds': bond_schema.dump(bonds),
            'total': 10,
            'status': 'Task completed!',
            'result': len(bonds)}


@flask_celery.celery.task
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
