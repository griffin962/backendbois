from flask import Flask, request, jsonify, g
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api

from sqlalchemy.sql.expression import and_

from klap4 import db
from klap4.db_entities import *

app = Flask(__name__)
CORS(app)
api = Api(app)


@app.before_request
def initialize_request():
    g.db = db.Session()


@app.after_request
def cleanup_request():
    if "db" in g:
        g.db.close()


# Search route returns different lists based on what the user wants to search.
@app.route('/search/<category>', methods=['GET', 'POST'])
def search(category):
    if category == "artist":
        genre = request.get_json()['genre']
        name = request.get_json()['name']
        # Search database for artists with matching name and/or genre, return list of IDs and names that match
        id = 1
        name = "Haha"
        record = dict(id=id, name=name)
        return jsonify(record)

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
            record = dict(album=album, songs=song_list)
        else:
            pass

    return 'a'