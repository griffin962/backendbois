from pathlib import Path

from flask import Flask, request, jsonify, g, make_response
from flask_cors import CORS, cross_origin
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_restful import Resource, Api
from flask_jwt_extended import (JWTManager, jwt_required, jwt_optional, create_access_token, 
                                get_jwt_identity, jwt_refresh_token_required, 
                                create_refresh_token, set_access_cookies, 
                                set_refresh_cookies, unset_jwt_cookies, get_jwt_claims)

from klap4 import db
from klap4.db_entities import *
from klap4.services import *
from klap4.utils import *
from klap4.views import *
from klap4.config import config


#TODO: Need to connect to DB in API in order for admin panel to work. Any idea why?
script_path = Path(__file__).absolute().parent
db.connect(script_path/".."/"test.db")
session = db.Session()


# Initial app configuration
app = Flask(__name__)
app.secret_key = 'secret'
app.config['FLASK_ADMIN_SWATCH'] = 'cyborg'
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False         # Set to True in production (for HTTPS)
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'

cors = CORS(app, resources={r"/*": {"origins": config.config()['clientOrigin']}}, supports_credentials=True)
api = Api(app)
jwt = JWTManager(app)
admin = Admin(app, name='KLAP4', template_mode='bootstrap3')

#TODO: Make custom model views for each model (like genre)
admin.add_view(GenreModelView(Genre, session))
admin.add_view(ArtistModelView(Artist, session))
admin.add_view(AlbumModelView(Album, session))
admin.add_view(ModelView(Song, session))
admin.add_view(ModelView(AlbumReview, session))
admin.add_view(ModelView(AlbumProblem, session))
admin.add_view(ProgramFormatModelView(ProgramFormat, session))
admin.add_view(ProgramModelView(Program, session))
admin.add_view(ProgramSlotModelView(ProgramSlot, session))
admin.add_view(PlaylistModelView(Playlist, session))
admin.add_view(PlaylistEntryModelView(PlaylistEntry, session))
admin.add_view(DJModelView(DJ, session))
'''
@app.before_request
def initialize_request():
    g.db = db.Session()


@app.after_request
def cleanup_request():
    if "db" in g:
        g.db.close()
'''

@jwt.user_claims_loader
def add_claims_to_access(user):
    return {'name': user.name, 'role': user.is_admin}

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id

@app.route('/token/auth', methods=['POST'])
def login():
    encoded_message = request.headers['Authorization']
    user_obj = decode_message(encoded_message)

    if ldap_login(user_obj):
        username = user_obj['username']
        name = 'Test User'
        is_admin = True
        user = check_user(username, name, is_admin)
        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)

        resp = jsonify({'login': True})
        set_access_cookies(resp, access_token)
        set_refresh_cookies(resp, refresh_token)
        return resp, 200
    else:
        return jsonify({"login": False}), 400

@app.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    user_roles = get_jwt_claims()
    user = check_user(current_user, user_roles['name'], user_roles['is_admin'])
    access_token = create_access_token(identity=user)

    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200


@app.route('/token/remove', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200


@app.route('/', methods=['GET'])
@jwt_optional
def display_user():
    current_user = get_jwt_identity()
    if current_user:
        return jsonify(logged_in_as=current_user), 200
    else:
        return jsonify(logged_in_as='Anonymous'), 200

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
@app.route('/display/<category>/<id>', methods=['GET'])
def display(category, id):

    entity_list = []

    if request.method == 'GET':
        if category == "artist":
            artist = get_json(get_entity_from_tag(id))
            album_list = list_albums(id)

            formatted_list = []
            for item in album_list:
                obj = get_json(item)
                formatted_list.append(obj)
            entity_list.append(formatted_list)

            artist_obj = {
                            "artist": artist,
                            "albums": entity_list[0]
            }

            return jsonify(artist_obj)

        elif category == "album":
            artist_id = decompose_tag(id)[0] + str(decompose_tag(id)[1])
            artist = get_json(get_entity_from_tag(artist_id))
            album = get_json(get_entity_from_tag(id))

            album_info = display_album(id)

            thingy = {
                        "artist": artist,
                        "album": album,
                        "reviews": album_info[0],
                        "problems": album_info[1],
                        "songs": album_info[2],
            }

            return jsonify(thingy)
        elif category == "programming":
            # Write stuff here, delete the `pass` when finished
            # Make a function in programming_services.py to access the database and stuff
            programming = display_program(id)
            obj = {
                    "programs": programming[0],
                    "program_slots": programming[1]
            }
            return jsonify(obj)
            #pass


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


@app.route('/charts/<form>', methods=['GET'])
def get_new_charts(form):
    if request.method == 'GET':
        charts = generate_chart(form)
        charts = charts_format(charts)
        return jsonify(charts)


# Quickjump route for jumping straight to a resource based on ID
@app.route('/quickjump/<id>', methods=['GET'])
def quickjump(id):
    try:
        entity = get_entity_from_tag(id)
        if type(entity) == Artist:
            typ = "artist"
        elif type(entity) == Album:
            typ = "album"
        else:
            return make_response(jsonify({"error": "Bad Request"}), 400)
    except:
        return make_response(jsonify({"error": "Not Found"}), 404)
    
    res = {
            "type": typ,
            "id": id
    }
    return jsonify(res)


@app.route('/playlist/<dj>', methods=['GET', 'POST', 'PUT', 'DELETE'])
#@jwt_protected
def playlist(dj):
    if request.method == 'GET':
        playlists = list_playlists(dj)
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

@app.route('/playlist/display/<dj>/<playlist_name>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def show_playlist(dj, playlist_name):
    if request.method == 'GET':
        playlist = display_playlist(dj, playlist_name)
        return jsonify(playlist)

    elif request.method == 'POST':
        index = request.get_json()['index']
        reference = request.get_json()['ref']
        new_entry = add_playlist_entry(dj, playlist_name, index, reference)
        return "Added"

    elif request.method == 'PUT':
        index = request.get_json()['index']
        ref = request.get_json()['ref']
        new_index = request.get_json()['newIndex']
        new_ref = request.get_json()['newRef']
        updated_entry = update_playlist_entry(dj, playlist_name, index, ref, new_index, new_ref)
        return "Updated"

    elif request.method == 'DELETE':
        index = request.get_json()['index']
        ref = request.get_json()['ref']
        delete_playlist_entry(dj, playlist_name, index, ref)
        return "Deleted"


@app.route('/programming/log', methods=['GET', 'POST'])
def programming_log():
    from datetime import datetime
    import time
    if request.method == 'GET':
        program_slots = get_program_slots()

        for slot in program_slots:
            slot['time'] = str(slot['time'])
    
        return jsonify(program_slots)