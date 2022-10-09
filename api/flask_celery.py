from celery import Celery


class FlaskCelery():

    def __init__(self, name):
        self.celery = Celery(name, backend="redis://localhost:6379/0",
                             broker="redis://localhost:6379/0")

    def init_app(self, app):
        self.celery.conf.update(app.config)

        class ContextTask(self.celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        self.celery.Task = ContextTask
