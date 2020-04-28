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
from klap4.resources import *
from klap4.config import config

from time import strptime, strftime

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
#admin.add_view(ModelView(Song, session))
#admin.add_view(AlbumReviewModelView(AlbumReview, session))
#admin.add_view(ModelView(AlbumProblem, session))
#admin.add_view(ProgramFormatModelView(ProgramFormat, session))
#admin.add_view(ProgramModelView(Program, session))
admin.add_view(ProgramSlotModelView(ProgramSlot, session))
admin.add_view(ProgramLogEntryModelView(ProgramLogEntry, session))
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
        return jsonify({"login": False}), 401

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


api.add_resource(ArtistListAPI, '/search/artist')
api.add_resource(ArtistAPI, '/display/artist/<string:ref>')
api.add_resource(AlbumListAPI, '/search/album')
api.add_resource(AlbumAPI, '/display/album/<string:ref>')
api.add_resource(ChartsAPI, '/charts/<string:form>/<int:weeks>')
api.add_resource(PlaylistAPI, '/playlist/<string:dj_id>')
api.add_resource(PlaylistEntryAPI, '/playlist/display/<string:dj_id>/<string:p_name>')

# Search route returns different lists based on what the user wants to search.
@app.route('/search/<category>', methods=['GET', 'POST'])
def search(category):

    if request.method == 'GET':
        if category == "program":
            program_list = search_programming("", "")
            return jsonify(program_list)


    elif request.method == 'POST':
        if category == "program":
            p_type = request.get_json()['programType']
            name = request.get_json()['name']
            program_list = search_programming(p_type, name)
            return jsonify(program_list)


# Display route will return different data based on resource type and ID
@app.route('/display/<category>/<id>', methods=['GET'])
def display(category, id):
    if request.method == 'GET':
        if category == "program":
            try:
                program = display_program(id)
                serialized_program = program.serialize()
                return jsonify(serialized_program)
            except:
                return jsonify(error='Not Found'), 404
        
        else:
            return jsonify(error='Not Found'), 404


@app.route('/album/review/<id>', methods=['POST'])
#@jwt_required
def review_album(id):
    if request.method == 'POST':
        dj_id = request.get_json()['dj_id']
        content = request.get_json()['content']
        try:
            review = add_review(id, dj_id, content)
        except:
            return jsonify(error='Bad request'), 400

        return "Added"


@app.route('/album/problem/<id>', methods=['POST'])
#@jwt_required
def report_album_problem(id):
    if request.method == 'POST':
        dj_id = request.get_json()['dj_id']
        content = request.get_json()['content']
        try:
            problem = report_problem(id, dj_id, content)
        except:
            return jsonify(error='Bad request'), 400

        return "Added"


# Quickjump route for jumping straight to a resource based on ID
@app.route('/quickjump/<ref>', methods=['GET'])
def quickjump(ref):
    try:
        entity = get_entity_from_tag(ref)
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
            "id": ref
    }
    return jsonify(res)


@app.route('/programming/log', methods=['GET', 'POST', 'PUT', 'DELETE'])
def programming_log():
    if request.method == 'GET':
        program_slots = get_program_slots()
        program_log_entries = get_program_log()

        thingy = {
                "program_slots": program_slots,
                "program_log_entries": program_log_entries
            }
    
        return jsonify(thingy)
    elif request.method == 'POST':
        program_type = request.get_json()['programType']
        program_name = request.get_json()['programName']
        slot_id = request.get_json()['slotId']
        dj_id = request.get_json()['djId']

        new_log = add_program_log(program_type, program_name, slot_id, dj_id)

        return jsonify(new_log.serialize())
    elif request.method == 'PUT':
        program_type = request.get_json()['programType']
        program_name = request.get_json()['programName']
        slot_id = request.get_json()['slotId']
        dj_id = request.get_json()['djId']
        new_name = request.get_json()['newName']

        update_program_log(program_type, program_name, slot_id, dj_id, new_name)
        return "Updated"
    elif request.method == 'DELETE':
        program_type = request.get_json()['programType']
        timestamp = request.get_json()['timestamp']
        dj_id = request.get_json()['djId']

        try:
            pyTime = strftime('%Y-%m-%d %H:%M:%S', strptime(timestamp, '%a, %d %b %Y %H:%M:%S GMT'))
            delete_program_log(program_type, pyTime, dj_id)
        except:
            delete_program_log(program_type, timestamp, dj_id)

        return "Deleted"