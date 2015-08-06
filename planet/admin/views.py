from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import AdminIndexView

from flask.ext.login import current_user

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated() and current_user.is_administrator()

class MyModelView(ModelView):
    def _get_endpoint(self, endpoint):
        """
        Override to rename views (and avoid clash with blueprints in the app itself)
        """
        if endpoint:
            return endpoint

        return '%s' % self.__class__.__name__.lower()

class SpeciesAdminView(MyModelView):

    def is_accessible(self):
        return current_user.is_authenticated() and current_user.is_administrator()

    def create_model(self, form):
        model = self.model(form.code.data,
                           form.name.data,
                           form.ncbi_tax_id.data,
                           form.pubmed_id.data,
                           form.project_page.data,
                           form.color.data,
                           form.highlight.data)
        form.populate_obj(model)
        self.session.add(model)
        self._on_model_change(form, model, True)
        self.session.commit()
        return True

