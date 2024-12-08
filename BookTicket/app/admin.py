from flask_sqlalchemy.model import Model
from app import db, app
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from app.models import Flight, FlightRoute, User, UserRole, IntermediateAirport
from flask_login import current_user, logout_user
from flask import redirect


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)


class FlightRouteView(AuthenticatedView):
    can_export = True
    can_view_details = True
    # form_columns = ['dep_airport_id', 'des_airport_id']
    column_list = ['dep_airport', 'des_airport', 'flights']


class FlightView(AuthenticatedView):
    can_export = True
    # column_list = ['flight_code', 'flight_route', 'airplane']
    form_excluded_columns = ['flight_schedules', 'tickets', 'inter_airports']


class MyView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(MyView):
    @expose("/")
    def __index__(self):
        logout_user()
        return redirect("/admin")


class StatsView(MyView):
    @expose("/")
    def __index__(self):
        return self.render("admin/stats.html")


admin = Admin(app, name='bookticket', template_mode='bootstrap4')

admin.add_view(FlightRouteView(FlightRoute, db.session))
admin.add_view(FlightView(Flight, db.session))
admin.add_view(StatsView(name="Report"))
admin.add_view(LogoutView(name="Log out"))
