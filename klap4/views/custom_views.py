from flask_admin.contrib.sqla import ModelView

class GenreModelView(ModelView):
    column_display_pk = True
    form_columns = ('abbreviation', 'name', 'color')
