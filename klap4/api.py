from flask import Flask, request, jsonify, g
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api

from sqlalchemy.sql.expression import and_

from klap4 import db
from klap4.db_entities import *

app = Flask(__name__)
CORS(app)
api = Api(app)


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
    if request.method == 'GET':
        if category == "artist":
            artist = get_entity_from_tag(id)
            return jsonify(get_json(artist))

        elif category == "album":
            album = get_entity_from_tag(id)
            song_list = album.songs
            return jsonify(get_json(album))
        else:
            pass
    

    elif request.method == 'POST':
        if category == "artist":
            pass
        elif category == "album":
            pass
        else:
            pass
    

    elif request.method == 'PUT':
        pass


    elif request.method == 'DELETE':
        pass

    return 'a'