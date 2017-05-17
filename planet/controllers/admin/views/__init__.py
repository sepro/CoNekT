from flask_admin import AdminIndexView, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user


class AdminBaseView(BaseView):
    def is_accessible(self):
        """
        Override to ensure the current user is an admin
        """
        return current_user.is_authenticated and current_user.is_administrator


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        """
        Override to ensure the current user is an admin
        """
        return current_user.is_authenticated and current_user.is_administrator


class MyModelView(ModelView):
    def is_accessible(self):
        """
        Override to ensure the current user is an admin
        """
        return current_user.is_authenticated and current_user.is_administrator

    def _get_endpoint(self, endpoint):
        """
        Override to rename views (and avoid clash with blueprints in the app itself)
        """
        if endpoint:
            return endpoint

        return '%s' % self.__class__.__name__.lower()


