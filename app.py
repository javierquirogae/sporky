import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, MessageForm, ProfileEditForm
from models import db, connect_db, User, Message, Likes

CURR_USER_KEY = "curr_user"

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///sporky'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"


debug = DebugToolbarExtension(app)


@app.route("/")
def root():
    """Homepage."""

    return redirect("/")



@app.route("/playlists", methods=["GET"])
def show_all_playlists():
    """Return a list of playlists."""

    playlists = Playlist.query.all()
    return render_template("playlists.html", playlists=playlists)


@app.route("/playlists/<int:playlist_id>")
def show_playlist(playlist_id):
    """Show detail on specific playlist."""
    playlist = Playlist.query.get_or_404(playlist_id)
    songs = playlist.song
    return render_template("playlist.html", playlist=playlist,songs=songs)
  


@app.route("/playlists/add", methods=["GET"])
def show_playlist_form():
    """Show add-playlist form:"""
    return render_template("new_playlist.html", form=PlaylistForm())
  

@app.route("/playlists/add", methods=["POST"])
def add_playlist():
    """Handle add-playlist form:"""
    form = PlaylistForm()
    name = form.name.data
    description = form.description.data
    new_playlist = Playlist(name=name, description=description)
    db.session.add(new_playlist)
    db.session.commit()
    return redirect("/playlists")



@app.route("/songs", methods=["GET"])
def show_all_songs():
    """Show list of songs."""
    songs = Song.query.all()
    return render_template("songs.html", songs=songs)


@app.route("/songs/<int:song_id>", methods=["GET"])
def show_song(song_id):
    """return a specific song"""
    song = Song.query.get_or_404(song_id)
    return render_template("song.html", song=song)


@app.route("/songs/add", methods=["GET"])
def add_song_form():
    """Show add-song form:"""
    return render_template("new_song.html", form=SongForm())

@app.route("/songs/add", methods=["POST"])
def add_song():
    """Handle add-song form:"""
    form = SongForm()
    title = form.title.data
    artist= form.artist.data
    new_song = Song(title=title, artist=artist)
    db.session.add(new_song)
    db.session.commit()
    return redirect("/songs")



@app.route("/playlists/<int:playlist_id>/add-song", methods=["GET"])
def add_song_to_playlist_form(playlist_id):
    """Show Add a playlist form."""

    playlist = Playlist.query.get_or_404(playlist_id)
    form = NewSongForPlaylistForm()

    curr_on_playlist = [s.id for s in playlist.song]
    form.song.choices = (db.session.query(Song.id, Song.title)
                        .filter(Song.id.notin_(curr_on_playlist))
                        .all())

    return render_template("add_song_to_playlist.html",
                            playlist=playlist,
                            form=form)


@app.route("/playlists/<int:playlist_id>/add-song", methods=["POST"])
def add_song_to_playlist(playlist_id):
    """Add a playlist and redirect to list."""

    form = NewSongForPlaylistForm()
    song=form.song.data
    song_id = ""
    for c in song:
        if c.isdigit():
            song_id = song_id + c
    int_song_id = int(song_id)
    print(int_song_id)
    print('*'*100)
    print(type(int_song_id))
    playlist_song = PlaylistSong(song_id=int_song_id, playlist_id=playlist_id)
    db.session.add(playlist_song)
    db.session.commit()

    return redirect(f"/playlists/{playlist_id}")
