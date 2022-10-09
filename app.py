from flask import redirect, url_for
from api import create_app, db
from api import models
from api import socketIO
from api.config import Config


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


if __name__ == 'main':
    socketIO.run(app)
