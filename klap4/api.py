from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api

from klap4 import db

app = Flask(__name__)
CORS(app)
api = Api(app)


# Login route will authenticate using LDAP server to see if user's login is correct
@app.route('/login', methods=['POST'])
def login():
    username = request.get_json()['username']
    return 'a'


# Search route returns different lists based on what the user wants to search.
@app.route('/search/<type>', methods=['POST'])
def search(type):
    if type == "artist":
        genre = request.get_json()['genre']
        name = request.get_json()['name']
        # Search database for artists with matching name and/or genre, return list of IDs and names that match
        id = 1
        name = "Haha"
        record = dict(id=id, name=name)
        return jsonify(record)
    elif type == "album":
        genre = request.get_json()['genre']
        name = request.get_json()['name']
        # Search database for artists with matching name and/or genre, return list of IDs and names that match
        id = 1
        name = "Haha"
        record = dict(id=id, name=name)
        return jsonify(record)
    elif type == "programming":
        genre = request.get_json()['genre']
        name = request.get_json()['name']
        # Search database for artists with matching name and/or genre, return list of IDs and names that match
        id = 1
        name = "Haha"
        record = dict(id=id, name=name)
        return jsonify(record)

# On an artist page, return the ID, name, and list of albums (album objects)
@app.route('/display/artist/<id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def artist_page(id):
    if request.method == 'GET':
        name = 'DEFAULT_NAME'
        album_list = ['Album1, Album2, Album3']

        record = dict(id=id, results=[name, album_list])
        return jsonify(record)

        
#Display id, artist_id, name, letter/key, songlist, date_entered, missing, 
# search_slug,...
@app.route('/display/album/<id>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def album_page(id):
    if request.method == 'GET':
        name = 'DEFAULT_NAME'
        record = dict(id=id, results=name)

        return jsonify(record)


if __name__ == "__main__":
    db.connect("test.db")
    app.run(debug=True)

