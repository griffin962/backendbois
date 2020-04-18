from pathlib import Path

from flask import Flask, request, jsonify, g
from flask_cors import CORS, cross_origin
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_restful import Resource, Api

from klap4 import db
from klap4.db_entities import *
from klap4.services import *
from klap4.utils import *
from klap4.views import *


#TODO: Need to connect to DB in API in order for admin panel to work. Any idea why?
script_path = Path(__file__).absolute().parent
db.connect(script_path/".."/"test.db")
session = db.Session()


# Initial app configuration
app = Flask(__name__)
CORS(app)
api = Api(app)
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.secret_key = 'secret'
admin = Admin(app, name='KLAP4', template_mode='bootstrap3')
global_user = "test_user"

#TODO: Make custom model views for each model (like genre)
admin.add_view(GenreModelView(Genre, session))
admin.add_view(ArtistModelView(Artist, session))
admin.add_view(ModelView(Album, session))
admin.add_view(ModelView(Song, session))
admin.add_view(ModelView(AlbumReview, session))
admin.add_view(ModelView(AlbumProblem, session))
admin.add_view(ProgramModelView(Program, session))
admin.add_view(PlaylistModelView(Playlist, session))

'''@app.before_request
def initialize_request():
    g.db = db.Session()


@app.after_request
def cleanup_request():
    if "db" in g:
        g.db.close()'''


@app.route('/session', methods=['GET', 'POST'])
def user_session():
    if request.method == 'GET':
        return jsonify({"Login": True, "Username": "test_user"})
    if request.method == 'POST':
        username = request.get_json()['username']
        #Checks if user is in LDAP server against their password
        # If so, checks if they're in our database
        # If not, add them to the database
        return jsonify({"Login": True, "Username": username})


# Search route returns different lists based on what the user wants to search.
@app.route('/search/<category>', methods=['GET', 'POST'])
def search(category):
    if request.method == 'GET':
        if category == "artist":
            artist_list = search_artists("", "")
            return jsonify(artist_list)

        elif category == "album":
            album_list = list_new_albums()
            return jsonify(album_list)
        
        elif category == "program":
            program_list = search_programming("", "")
            return jsonify(program_list)


    elif request.method == 'POST':
        if category == "artist":
            genre = request.get_json()['genre']
            name = request.get_json()['name']
            artist_list = search_artists(genre, name)
            return jsonify(artist_list)

        elif category == "album":
            genre = request.get_json()['genre']
            artist_name = request.get_json()['artistName']
            name = request.get_json()['name']

            #TODO: make search fields for label, promoter, format, and is_new in future
            album_list = search_albums(genre, artist_name, name)
            return jsonify(album_list)
        
        elif category == "program":
            p_type = request.get_json()['programType']
            name = request.get_json()['name']
            program_list = search_programming(p_type, name)
            return jsonify(program_list)


# Display route will return different data based on resource type and ID
@app.route('/display/<category>/<id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def display(category, id):

    entity_list = []

    if request.method == 'GET':
        if category == "artist":
            artist = get_entity_from_tag(id)
            album_list = list_albums(id)

            entity_list.append(get_json(artist))
            formatted_list = []
            for item in album_list:
                obj = get_json(item)
                formatted_list.append(obj)
            entity_list.append(formatted_list)

            return jsonify(entity_list)
            #TODO: Get an album list

        elif category == "album":
            album = get_entity_from_tag(id)
            album_info = display_album(id)

            album_info.append(get_json(album))

            return jsonify(album_info)

            #TODO: Get a song list, album review list, and a list of problems


@app.route('/album/review/<id>', methods=['POST'])
def review_album(id):
    if request.method == 'POST':
        dj_id = request.get_json()['username']
        content = request.get_json()['content']
        review = add_review(id, dj_id, content)

        return "Added"


@app.route('/album/problem/<id>', methods=['POST'])
def report_album_problem(id):
    if request.method == 'POST':
        dj_id = request.get_json()['username']
        content = request.get_json()['content']
        problem = report_problem(id, dj_id, content)

        return "Added"


@app.route('/charts/<form>/<weeks>', methods=['GET'])
def get_new_charts(form, weeks):
    if request.method == 'GET':
        charts = generate_chart(form, weeks)
        charts = charts_format(charts)
        return jsonify(charts)


# Quickjump route for jumping straight to a resource based on ID
@app.route('/quickjump/<id>', methods=['GET'])
def quickjump(id):
    entity = get_json(get_entity_from_tag(id))

    #new_entity = { typ: "Artist", id: "AL2" }

    return jsonify(entity)


@app.route('/playlist', methods=['GET', 'POST', 'PUT', 'DELETE'])
def playlist():
    global global_user
    if request.method == 'GET':
        playlists = list_playlists(global_user)
        return jsonify(playlists)
    
    elif request.method == 'POST':
        dj_id = request.get_json()['username']
        p_name = request.get_json()['playlistName']
        show = request.get_json()['show']
        playlist = add_playlist(dj_id, p_name, show)

        return "Added"
    
    elif request.method == 'PUT':
        dj_id = request.get_json()['username']
        p_name = request.get_json()['playlistName']
        show = request.get_json()['show']
        playlist = update_playlist(dj_id, p_name, show)

        return "Updated"
    
    elif request.method == 'DELETE':
        dj_id = request.get_json()['username']
        p_name = request.get_json()['playlistName']
        delete_playlist(dj_id, p_name)

        return "Deleted"
