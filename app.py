from flask import redirect, url_for, jsonify
from api import create_app, db
from api import models
from api import socketIO
from api.config import Config
from api.tasks import long_task


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


@app.post('/longtask')
def longtask():
    task = long_task.apply_async()
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}


@app.get('/status/<task_id>')
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
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
            'status': task.info.get('status', '')
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
