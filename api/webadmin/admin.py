from api import admin_manager as admin, db
from api.models import (User, Role)
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask import redirect, url_for, flash
from flask_login import current_user
from flask_admin.base import AdminIndexView


class RestrictedAccess(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role.name == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        flash("Please sign in to continue", 'info')
        return redirect(url_for('web_admin.sign_in'))


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        return redirect(url_for("web_admin.sign_out"))


class UserView(RestrictedAccess):
    can_create = False
    can_delete = False
    column_exclude_list = ['password', 'token', 'token_expiration']
    column_searchable_list = ['name', 'email']


class RoleView(RestrictedAccess):
    can_create = True
    can_edit = True
    can_delete = False

    form_excluded_columns = ['user']


admin.add_view(UserView(User, db.session, endpoint="users"))
# admin.add_view(RoleView(Role, db.session))
# admin.add_view(PrescribedMedicinesView(PrescribedMedicines, db.session))
admin.add_view(LogoutView(name="Logout", endpoint="logout"))
