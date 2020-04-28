from flask import request, jsonify
from flask_restful import Resource

from klap4.services.playlist_services import list_playlists, add_playlist, update_playlist, delete_playlist
from klap4.services.playlist_services import display_playlist_entries, add_playlist_entry, update_playlist_entry, delete_playlist_entry


class PlaylistAPI(Resource):
    def get(self, dj_id):
        playlists = list_playlists(dj_id)
        return jsonify(playlists)
    
    def post(self, dj_id):
        json_data = request.get_json(force=True)
        p_name = json_data['playlistName']
        show = json_data['show']
        playlist = add_playlist(dj_id, p_name, show)
        return jsonify(playlist)
    
    def put(self, dj_id):
        json_data = request.get_json(force=True)
        p_name = json_data['playlistName']
        show = json_data['show']
        new_name = json_data['newName']
        new_show = json_data['newShow']
        playlist = update_playlist(dj_id, p_name, show, new_name, new_show)
        return jsonify(playlist)
    
    def delete(self, dj_id):
        json_data = request.get_json(force=True)
        dj_id = json_data['username']
        p_name = json_data['playlistName']
        delete_playlist(dj_id, p_name)
        return "Deleted"


class PlaylistEntryAPI(Resource):
    def get(self, dj_id, p_name):
        playlist = display_playlist_entries(dj_id, p_name)
        return jsonify(playlist)
    
    def post(self, dj_id, p_name):
        json_data = request.get_json(force=True)
        entry = json_data['entry']
        new_entry = add_playlist_entry(dj_id, p_name, entry)
        return jsonify(new_entry)
    
    def put(self, dj_id, p_name):
        if 'entry' in request.get_json().keys() and 'newEntry' in request.get_json().keys():
            entry = request.get_json()['entry']
            new_entry = request.get_json()['newEntry']
            index = request.get_json()['index']
            update_playlist_entry(dj_id, p_name, index, entry, None, new_entry)
        elif 'newIndex' in request.get_json().keys():
            index = request.get_json()['index']
            new_index = request.get_json()['newIndex']
            update_playlist_entry(dj_id, p_name, index, None, new_index, None)
        else:
            return jsonify(error='Bad request'), 400
        return "Updated"
    
    def delete(self, dj_id, p_name):
        json_data = request.get_json(force=True)
        index = json_data['index']
        delete_playlist_entry(dj_id, p_name, index)
        return "Deleted"