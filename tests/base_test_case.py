import unittest
from api import create_app, db
from api.config import TestConfig
from flask import current_app


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.appctx = self.app.app_context()
        self.appctx.push()
        db.create_all()
        self.client = self.app.test_client()
        self.test_cli_runner = self.app.test_cli_runner()
        self.test_cli_runner.invoke(args="commands setup-database")

    def tearDown(self):
        db.drop_all()
        self.appctx.pop()
        self.app = None
        self.appctx = None
        self.client = None
        self.test_cli_runner = None

    def test_app(self):
        assert self.app is not None
        assert current_app == self.app
