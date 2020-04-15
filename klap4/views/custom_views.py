from flask_admin.contrib.sqla import ModelView

class GenreModelView(ModelView):
    column_display_pk = True
    form_columns = ('abbreviation', 'name', 'color')


class ProgramModelView(ModelView):
    column_display_pk = True
    form_columns = ('program_type', 'name', 'description')


class PlaylistModelView(ModelView):
    column_display_pk = True
    form_columns = ('dj_id', 'playlist_name', 'show')