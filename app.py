import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import RegisterForm, LoginForm, Favorites
from models import db, connect_db, User, Saved

CURR_USER_KEY = "curr_user"

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://seaotsudaxmbqu:9059baa106ec77b79200c5dded8468463cb24e461408e2a1d026a8690ac83fc6@ec2-34-202-127-5.compute-1.amazonaws.com:5432/d1v13vp90lc305'
# (os.environ.get(
#     'postgres://seaotsudaxmbqu:9059baa106ec77b79200c5dded8468463cb24e461408e2a1d026a8690ac83fc6@ec2-34-202-127-5.compute-1.amazonaws.com:5432/d1v13vp90lc305', 
#     'postgresql:///sporky'))

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sporky'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/login', methods=["GET"])
def login_form():
    """Login page."""

    form = LoginForm()
    return render_template('login.html', form=form)



@app.route('/login', methods=["POST"])
def login():
    """Handle user login."""

    form = LoginForm()
    try:
        if User.authenticate(form.username.data, form.password.data):
            user = User.authenticate(form.username.data, form.password.data)
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")
        else:
            flash("Invalid credentials.", 'danger')
            return redirect("/")
    except ValueError:
        flash("Invalid credentials.", 'danger')
        return redirect("/")


@app.route('/logout', methods=['GET'])
def logout():
    """Handle logout of user."""
    
    user = User.query.get_or_404(session[CURR_USER_KEY])
    do_logout()
    flash(f"Goodbye, {user.username}!", "info")
    return redirect('/login')




@app.route("/")
def root():
    """Homepage."""
    if g.user:
        return render_template("index.html")
    else:
        return redirect("/login")



@app.route('/signup', methods=["GET"])
def signup_form():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = RegisterForm()
    return render_template('signup.html', form=form)
    

@app.route('/signup', methods=["POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = RegisterForm()
    try:
        user = User.signup(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data,
        )
        db.session.commit()

    except IntegrityError:
        flash("Username already taken", 'danger')
        return render_template('signup.html', form=form)

    do_login(user)

    return redirect("/")


@app.route('/save_recipe/<int:recipe_id>',methods=["POST"] )
def save_recipe(recipe_id):
    saved_id_list = []
    user = User.query.get_or_404(session[CURR_USER_KEY])
    form = Favorites()
    likes = (Saved
                .query
                .filter(Saved.user_id == user.id)
                .limit(100)
                .all())
    for like in likes:
        saved_id_list.append(like.recipe_id)
    if recipe_id in saved_id_list:
        flash("Recipe was already in favorites list !", 'danger')
        return redirect("/favorites")
    else:
        Saved.add_like(
            user_id=session[CURR_USER_KEY],
            recipe_id=recipe_id,
            used=form.used.data,
            rating=form.rating.data,
            notes=form.notes.data
            )
        db.session.commit()
        flash("Recipe added to favorites", 'warning')

    return redirect("/favorites")

@app.route('/favorites',methods=["GET"] )
def show_favorites_list():
    count = 0
    if g.user:
        user = User.query.get_or_404(session[CURR_USER_KEY])
        likes = (Saved
                .query
                .filter(Saved.user_id == user.id)
                .limit(100)
                .all())
        count = len(likes)
        for like in likes:
            print(like.recipe_id)
            print(like.rating)
            print(type(like.rating))
        return render_template('favorites.html', user=user, likes=likes, count=count)
    else:
        return redirect("/login")
    

@app.route('/saved_recipe_detail/<int:recipe_id>',methods=["GET"])
def show_recipe_detail(recipe_id):
    if g.user:
        return render_template('detail.html', recipe_id=recipe_id)
    else:
        return redirect("/login")


@app.route('/delete_recipe/<int:recipe_id>',methods=["POST"] )
def delete_recipe(recipe_id):
    user = User.query.get_or_404(session[CURR_USER_KEY])
    Saved.query.filter(Saved.recipe_id == recipe_id, Saved.user_id == user.id).delete()
    db.session.commit()
    flash("Recipe removed from favorites", 'warning')
    return redirect("/favorites")


@app.route('/edit_recipe/<int:recipe_id>',methods=["get"] )
def edit_recipe_form(recipe_id):
    user = User.query.get_or_404(session[CURR_USER_KEY])
    saved_recipe = Saved.query.filter(Saved.recipe_id == recipe_id, Saved.user_id == user.id).first()
    form = Favorites(obj=saved_recipe)
    
    return render_template('edit.html', form=form, saved_recipe=saved_recipe)


@app.route('/edit_recipe/<int:recipe_id>',methods=["POST"] )
def edit_recipe(recipe_id):
    user = User.query.get_or_404(session[CURR_USER_KEY])
    recipe = Saved.query.filter(Saved.recipe_id == recipe_id, Saved.user_id == user.id).first()
    form = Favorites(obj=recipe)
    recipe.used = form.used.data
    recipe.rating = form.rating.data
    recipe.notes = form.notes.data

    db.session.commit()
    flash("Recipe edited", 'info')
    return redirect("/favorites")