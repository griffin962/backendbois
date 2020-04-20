from flask_admin.contrib.sqla import ModelView

class GenreModelView(ModelView):
    column_display_pk = True
    form_columns = ('abbreviation', 'name', 'color')


class ArtistModelView(ModelView):
    column_list=['name', 'genre_abbr', 'number']
    form_columns = ('genre', 'name')


class AlbumModelView(ModelView):
    column_list=['name', 'artist', 'genre_abbr', 'date_added', 'missing', 'format_bitfield']


class ProgramModelView(ModelView):
    column_display_pk = True
    form_columns = ('type', 'name', 'description')


class PlaylistModelView(ModelView):
    column_display_pk = True
    form_columns = ('dj_id', 'name', 'show')