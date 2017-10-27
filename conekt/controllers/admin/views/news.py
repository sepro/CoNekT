from conekt.controllers.admin.views import MyModelView


class NewsAdminView(MyModelView):
    """
    News view in admin page, specifies what is available in CRUD
    """
    form_columns = ('message', 'posted_by', 'posted')

    can_create = True
