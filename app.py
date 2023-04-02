import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import RegisterForm, LoginForm, Favorites
from models import db, connect_db, User, Saved

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
            image_url=form.image_url.data or User.image_url.default.arg,
        )
        db.session.commit()

    except IntegrityError:
        flash("Username already taken", 'danger')
        return render_template('signup.html', form=form)

    do_login(user)

    return redirect("/")



@app.route('/save_recipe/<int:recipe_id>',methods=["GET"])
def save_recipe_form(recipe_id):
    form = Favorites()
    return render_template('save.html', form=form, recipe_id=recipe_id)






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
        flash("Recipe already saved", 'danger')
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
        flash("Recipe saved", 'success')

    return redirect("/favorites")

@app.route('/favorites',methods=["GET"] )
def show_favorites_list():
    if g.user:
        user = User.query.get_or_404(session[CURR_USER_KEY])
        likes = (Saved
                .query
                .filter(Saved.user_id == user.id)
                .limit(100)
                .all())
        for like in likes:
            print(like.recipe_id)
        return render_template('favorites.html', user=user, likes=likes)
    else:
        return redirect("/login")
    

@app.route('/saved_recipe_detail/<int:recipe_id>',methods=["GET"])
def show_recipe_detail(recipe_id):
    return render_template('detail.html', recipe_id=recipe_id)