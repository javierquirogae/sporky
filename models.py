"""Models for SPORKY app."""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class Saved(db.Model):
    """Saved recipes."""

    __tablename__ = 'saves' 

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    recipe_id = db.Column(
        db.Integer,
        nullable=False,
        unique=True,
    )

    used = db.Column(
        db.Boolean,
        nullable=False,
    )

    rating = db.Column(
        db.Integer,
        nullable=True,
        default=0,
    )        

    notes = db.Column(
        db.Text,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    @classmethod
    def add_like(cls, recipe_id, used, rating, notes, user_id):
        """Add a like to a recipe."""
        save = Saved(
            recipe_id=recipe_id,
            used=used,
            rating=rating,
            notes=notes,
            user_id=user_id,
        )

        db.session.add(save)

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    saves = db.relationship(
        'Saved',
        backref='user',
        cascade='all, delete-orphan',
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def saved_recipes(self):
        """Return all recipes saved by this user."""
        return Saved.query.filter_by(user_id=self.id).all()

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.
        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()
        try:
            
            if user:
                is_auth = bcrypt.check_password_hash(user.password, password)
                if is_auth:
                    return user
        except:
            return False




def connect_db(app):
    """Connect this database to provided Flask app.
    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
