from flask import Flask, request, jsonify
# from sptoyt import *
from flask_cors import CORS

from sptoyt import final

app = Flask("WINGMAN")
CORS(app)

data = {
    "spotify_link": None,
    "yt_name": None,
    "yt_desc": None
}


@app.route('/spotify-link', methods=['POST'])
def spotify_link():
    spotify_link = request.json.get('spotify_link')
    if not spotify_link:
        return jsonify({"error": "Spotify playlist link is required"}), 400

    data['spotify_link'] = spotify_link
    return jsonify({"message": "Spotify playlist link received successfully", "spotify_link": spotify_link})


@app.route('/yt-name', methods=['POST'])
def yt_name():
    yt_name = request.json.get('yt_name')
    if not yt_name:
        return jsonify({"error": "YouTube playlist name is required"}), 400

    data['yt_name'] = yt_name
    return jsonify({"message": "YouTube playlist name received successfully", "yt_name": yt_name})


@app.route('/yt-desc', methods=['POST'])
def yt_desc():
    yt_desc = request.json.get('yt_desc')
    if not yt_desc:
        return jsonify({"error": "YouTube playlist description is required"}), 400

    data['yt_desc'] = yt_desc
    return jsonify({"message": "YouTube playlist description received successfully", "yt_desc": yt_desc})


# @app.route('/submit', methods=['GET'])
# def submit():
#     if not all(data.values()):
#         return jsonify({"error": "All fields are required before submission"}), 400
#
#     return jsonify({
#         "message": "Submission successful",
#         "data": data
#     })

@app.route('/submit', methods=['GET'])
def submit():
    if not all(data.values()):
        return jsonify({"error": "All fields are required before submission"}), 400

    save() 
    return jsonify({
        "message": "Submission successful",
        "data": data
    })


def save():
    with open('info.txt', 'w') as f:
        f.write(f"{data['spotify_link']}\n")
        f.write(f"{data['yt_name']}\n")
        f.write(f"{data['yt_desc']}\n")
    final()

if __name__ == '__main__':
    app.run(host='localhost', port=6969)
    save()

