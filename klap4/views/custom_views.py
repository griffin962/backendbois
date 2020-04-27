from flask_admin.contrib.sqla import ModelView

class GenreModelView(ModelView):
    column_list=['abbreviation', 'name', 'color']
    form_columns = ('abbreviation', 'name', 'color')


class ArtistModelView(ModelView):
    column_list=['name', 'genre_abbr', 'number']
    form_columns = ('genre', 'name', 'number')


class AlbumModelView(ModelView):
    column_list=['name', 'artist', 'genre_abbr', 'date_added', 'missing', 'format_bitfield']
    form_columns = ('genre', 'artist', 'letter', 'name', 'date_added', 'missing', 'format_bitfield', 'label_id', 'promoter_id') 


class ProgramFormatModelView(ModelView):
    column_display_pk = True
    form_columns = ['type', 'description']


class ProgramModelView(ModelView):
    column_display_pk = True
    form_columns = ('program_format', 'name', 'duration', 'months')


class ProgramSlotModelView(ModelView):
    column_display_pk = True
    form_columns = ('program_format', 'day', 'time')


class ProgramLogEntryModelView(ModelView):
    column_display_pk = True
    form_columns = ('program_format', 'program_name', 'program_slot', 'timestamp', 'dj')


class PlaylistModelView(ModelView):
    column_display_pk = True
    form_columns = ('dj_id', 'name', 'show')


class PlaylistEntryModelView(ModelView):
    column_display_pk = True
    form_columns = ('dj_id', 'playlist_name', 'index', 'reference_type', 'reference', 'entry')

class DJModelView(ModelView):
    column_display_pk = True
    form_columns = ('id', 'name', 'is_admin')