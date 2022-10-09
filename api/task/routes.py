from api.task import task
from apifairy import authenticate
from flask import jsonify
from api.task.tasks import export_bonds
from celery.utils import uuid
from api.auth.authentication import token_auth


@task.post("/export/bonds")
@authenticate(token_auth)
def export():
    """Export your bonds in pdf format"""
    user = token_auth.current_user()
    denomination_id = 1
    task = export_bonds.apply_async(
        args=[user.id, denomination_id], task_id="celery_task_id_" + uuid())
    return jsonify({"id": task.id})


@task.get("/export/bonds/status/<id>")
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
