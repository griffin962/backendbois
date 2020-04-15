from pathlib import Path

from flask import Flask, request, jsonify, g
from flask_cors import CORS, cross_origin
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_restful import Resource, Api

from klap4 import db
from klap4.db_entities import *
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

admin.add_view(GenreModelView(Genre, session))
admin.add_view(ModelView(Artist, session))
admin.add_view(ModelView(Album, session))
admin.add_view(ModelView(Song, session))


'''@app.before_request
def initialize_request():
    g.db = db.Session()


@app.after_request
def cleanup_request():
    if "db" in g:
        g.db.close()'''


# Search route returns different lists based on what the user wants to search.
@app.route('/search/<category>', methods=['GET', 'POST'])
def search(category):
    if request.method == 'GET':
        if category == "artist":
            artist_list = search_artists("", "")

            formatted_list = []
            for item in artist_list:
                obj = get_json(item)
                formatted_list.append(obj)
            return jsonify(formatted_list)

        elif category == "album":
            album_list = search_albums("", "", "")

            formatted_list = []
            for item in album_list:
                obj = get_json(item)
                formatted_list.append(obj)
            return jsonify(formatted_list)


    elif request.method == 'POST':
        if category == "artist":
            genre = request.get_json()['genre']
            name = request.get_json()['name']
            artist_list = search_artists(genre, name)
            formatted_list = []
            for item in artist_list:
                obj = get_json(item)
                formatted_list.append(obj)
            return jsonify(formatted_list)

        elif category == "album":
            genre = request.get_json()['genre']
            artist_name = request.get_json()['artist_name']
            name = request.get_json()['name']

            #TODO: make search fields for label, promoter, format, and is_new in future
            album_list = search_albums(genre, artist_name, name)
            formatted_list = []
            for item in album_list:
                obj = get_json(item)
                formatted_list.append(obj)
            return jsonify(formatted_list)


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
            song_list = list_songs(id)
            review_list = list_reviews(id)
            problem_list = list_problems(id)

            entity_list.append(get_json(album))

            formatted_list = []
            for item in song_list:
                obj = get_json(item)
                formatted_list.append(obj)
            entity_list.append(formatted_list)

            formatted_list = []
            for item in review_list:
                obj = get_json(item)
                formatted_list.append(obj)
            entity_list.append(formatted_list)

            formatted_list = []
            for item in problem_list:
                obj = get_json(item)
                formatted_list.append(obj)
            entity_list.append(formatted_list)

            return jsonify(entity_list)

            #TODO: Get a song list, album review list, and a list of problems

@app.route('/post/<category>', methods=['GET', 'POST'])
def post(category):
    if request.method == 'GET':
        pass


    elif request.method == 'POST':
        if category == "review":
            pass
    
    return 'a'