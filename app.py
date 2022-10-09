from flask import redirect, url_for, jsonify
from api import create_app, db
from api import models
from api import socketIO
from api.config import Config
from api.tasks import export_bonds
from celery.utils import uuid
from apifairy import authenticate, response
from api.auth.authentication import token_auth


app = create_app(Config)


# define the shell context
@app.shell_context_processor
def shell_context():
    ctx = {'db': db}
    for attr in dir(models):
        model = getattr(models, attr)
        if hasattr(model, '__bases__') and \
                db.Model in getattr(model, '__bases__'):
            ctx[attr] = model
    return ctx


@app.route('/')
def index():
    return redirect(url_for('apifairy.docs'))


@app.post("/export/bonds")
@authenticate(token_auth)
def export():
    """Export your bonds in pdf format"""
    user = token_auth.current_user()
    denomination_id = 1
    task = export_bonds.apply_async(
        args=[user.id, denomination_id], task_id="celery_task_id_" + uuid())
    return jsonify({"id": task.id})


@app.get("/export/bonds/status/<id>"    )
@authenticate(token_auth)
def export_bonds_status(id):
    """Check status for the export job"""
    task = export_bonds.AsyncResult(id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', ''),
            "bonds": task.info.get("bonds", "")
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


if __name__ == 'main':
    socketIO.run(app)
