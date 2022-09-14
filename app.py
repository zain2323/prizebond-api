from flask import redirect, url_for
from api import create_app
from api.models import *

app = create_app()

# @app.shell_context_processor
# def make_shell_context():
#     pass

@app.route('/')
def index():
    return redirect(url_for('apifairy.docs'))

if __name__ == 'main':
    app.run(debug=True)