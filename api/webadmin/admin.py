from api import admin_manager as admin, db
from api.models import (User, Role, Bond, Prize, Denomination, UpdatedLists,
                        WinningBond, DrawDate, DrawLocation, DrawNumber)
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask import redirect, url_for, flash, request
from flask_login import current_user
from pathlib import Path
from api.webadmin.utils import (load_prizes, load_denominations,
                                normalize_serials, save_picture,
                                delete_picture)
from api.webadmin.forms import FileForm, WinningBondForm
from sqlalchemy import func
from werkzeug.utils import secure_filename


class GenericView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and \
            current_user.role.name == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        flash("Please sign in to continue", 'info')
        return redirect(url_for('web_admin.sign_in', next=request.url))


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        return redirect(url_for("web_admin.sign_out"))


class UserView(GenericView):
    column_exclude_list = ('password_hash')
    column_searchable_list = ('name', 'email')
    can_create = False
    can_edit = True
    can_delete = False


class RoleView(GenericView):
    can_create = True
    can_edit = True
    can_delete = False

    form_excluded_columns = ['user']


class BondView(GenericView):
    column_searchable_list = ['serial']
    can_delete = True
    can_edit = True
    can_create = False


class DenominationView(GenericView):
    form_excluded_columns = ["bonds"]

    def delete_model(self, model):
        try:
            self.on_model_delete(model)
            self.session.flush()
            self.session.delete(model)
            self.session.commit()
        except Exception:
            flash('Can not delete due to other references.', 'error')
            self.session.rollback()
            return False
        else:
            self.after_model_delete(model)
        return True


class PrizeView(GenericView):
    form_excluded_columns = ["winning_bond"]

    def create_model(self, form):
        try:
            model = self.build_new_instance()
            form.populate_obj(model)
            self.session.add(model)
            self._on_model_change(form, model, True)
            self.session.commit()
        except Exception:
            flash('This denomination already exists.', "warning")
            self.session.rollback()
            return False
        else:
            self.after_model_change(form, model, True)
        return model

    def delete_model(self, model):
        try:
            self.on_model_delete(model)
            self.session.flush()
            self.session.delete(model)
            self.session.commit()
        except Exception:
            flash('Can not delete due to other references.', 'error')
            self.session.rollback()

            return False
        else:
            self.after_model_delete(model)
        return True


class WinningBondView(GenericView):
    page_size = 50
    column_labels = dict(bonds='Serial')
    column_searchable_list = ["bonds.serial", "date.date", "prize.prize"]
    ALLOWED_EXTENSIONS = {'txt'}

    def search_placeholder(self):
        placeholders = ["serial, date", "prize"]
        return u', '.join(placeholders)

    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    @expose('/new/upload_manually', methods=('GET', 'POST'))
    def upload_manually(self):
        form = WinningBondForm()
        form.denomination.choices = load_denominations()
        form.prize.choices = load_prizes()
        if form.validate_on_submit():
            price = int(form.denomination.data)
            prize = int(form.prize.data)
            serials = normalize_serials(form.serial.data)
            date = form.date.data
            location = form.location.data.lower()
            number = form.number.data
            try:
                self.add_bond(price, prize, serials, date, location, number)
            except Exception as e:
                print(e)
                flash("Records already uploaded.", "danger")
                db.session.rollback()
            return redirect(url_for("admin.index"))
        return self.render("admin/upload_manually.html", form=form)

    @expose('/new/upload_from_file', methods=('GET', 'POST'))
    def upload_from_file(self):
        form = FileForm()
        form.price.choices = load_denominations()
        form.prize.choices = load_prizes()
        if form.validate_on_submit():
            price = form.price.data
            prize = form.prize.data
            date = form.date.data
            location = form.location.data.lower()
            number = form.number.data
            file = form.name.data
            if file and self.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = save_picture(file)
                serials = self.get_serials(filename)
                try:
                    self.add_bond(price, prize, serials,
                                  date, location, number)
                except Exception:
                    flash("Records already uploaded.", "danger")
                    db.session.rollback()
                delete_picture(filename)
                return redirect(url_for("admin.index"))
        return self.render('admin/upload_from_file.html', form=form)

    def add_bond(self, price, prize, serials, date, location, number):
        price = int(price)
        prize = int(prize)
        bond_location = DrawLocation.query.filter_by(location=location).first()
        bond_number = DrawNumber.query.filter_by(number=number).first()

        if bond_location is None:
            draw_location = DrawLocation(location=location)
            db.session.add(draw_location)
            db.session.commit()
            bond_location = draw_location

        if bond_number is None:
            draw_number = DrawNumber(number=number)
            db.session.add(draw_number)
            db.session.commit()
            bond_number = draw_number

        bond_price = Denomination.query.filter_by(price=price).first()
        bond_prize = Prize.query.filter_by(prize=prize).first()
        # This is done to add the updated list
        bond_date = DrawDate.query.filter(func.DATE(DrawDate.date) == date) \
            .filter_by(bond_price_id=bond_price.id).first()
        if bond_date is None:
            draw_date = DrawDate(date=date, price=bond_price)
            db.session.add(draw_date)
            db.session.commit()
            bond_date = draw_date

        updated_lists = UpdatedLists.query.filter_by(
            date_id=bond_date.id, bond_price_id=bond_price.id).first()
        if updated_lists is None:
            bond_list = UpdatedLists(
                date_id=bond_date.id, bond_price_id=bond_price.id)
            db.session.add(bond_list)
            db.session.commit()
            updated_lists = bond_list

        for serial in serials:
            bond = Bond.query.filter_by(
                price=bond_price, serial=serial).first()
            if bond:
                winning_bond = WinningBond(bonds=bond, date_id=bond_date.id,
                                           bond_prize_id=bond_prize.id,
                                           location_id=bond_location.id,
                                           draw_id=bond_number.id)
                db.session.add(winning_bond)
            else:
                bond = Bond(serial=serial, price=bond_price)
                db.session.add(bond)
                winning_bond = WinningBond(bonds=bond, date_id=bond_date.id,
                                           bond_prize_id=bond_prize.id,
                                           location_id=bond_location.id,
                                           draw_id=bond_number.id)
                db.session.add(winning_bond)
        try:
            db.session.commit()
            flash("Record added successfully.", "success")
        except Exception as e:
            print(e)
            flash("Records have been already uploaded.", "error")
            db.session.rollback()

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        return self.render('admin/winning_bond_choice.html')

    def get_data(self, file_name):
        data = []
        path = Path('./PrizeBondApp/static/results/'+file_name)
        with open(path) as file:
            for line in file:
                data.append(line)
        return data

    def get_serials(self, file_name):
        data_list = self.get_data(file_name)
        final_serial_list = []
        for data in data_list:
            serials = data.split()
            if len(serials) != 0:
                for serial in serials:
                    try:
                        int(serial)
                        final_serial_list.append(serial)
                    except Exception:
                        print(serial)
                        print("Not a valid serial")
        return final_serial_list


admin.add_view(UserView(User, db.session, endpoint="users"))
admin.add_view(DenominationView(
    Denomination, db.session, endpoint="denomination"))
admin.add_view(PrizeView(Prize, db.session, endpoint="prize"))
admin.add_view(BondView(Bond, db.session, endpoint="bonds"))
admin.add_view(WinningBondView(WinningBond, db.session))
admin.add_view(RoleView(Role, db.session))
admin.add_view(LogoutView(name="Logout", endpoint="logout"))
