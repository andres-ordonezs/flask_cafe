"""Data models for Flask Cafe"""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from mapping import save_map


bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_USER_IMAGE_URL = ("/static/images/default-pic.png")

#######################################
# City model


class City(db.Model):
    """Cities for cafes."""

    __tablename__ = 'cities'

    code = db.Column(
        db.Text,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    state = db.Column(
        db.String(2),
        nullable=False,
    )

#######################################
# Cafe model


class Cafe(db.Model):
    """Cafe information."""

    __tablename__ = 'cafes'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    url = db.Column(
        db.Text,
        nullable=False,
    )

    address = db.Column(
        db.Text,
        nullable=False,
    )

    city_code = db.Column(
        db.Text,
        db.ForeignKey('cities.code'),
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        nullable=False,
        default="/static/images/default-cafe.jpg",
    )

    city = db.relationship("City", backref='cafes')

    def __repr__(self):
        return f'<Cafe id={self.id} name="{self.name}">'

    def get_city_state(self):
        """Return 'city, state' for cafe."""

        city = self.city
        return f'{city.name}, {city.state}'

    def get_state(self):
        """Return 'state' for cafe."""

        city = self.city
        return f'{city.state}'

    def get_cafe_map(self):
        """Returns map path for cafe"""

        path = save_map(self.id, self.address, self.city.name, self.city.state)

        return path

    def to_dict(self):
        """Serialize user to a dict of user info."""

        return {
            "id": self.id,
            "name": self.name
        }


#######################################
# User model

class User(db.Model):
    """User information."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.String(30),
        nullable=False,
        unique=True,
    )

    admin = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    email = db.Column(
        db.String(50),
        nullable=False,
    )

    first_name = db.Column(
        db.String(50),
        nullable=False,
    )

    last_name = db.Column(
        db.String(50),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    image_url = db.Column(
        db.String(255),
        nullable=False,
        default=DEFAULT_USER_IMAGE_URL
    )

    hashed_password = db.Column(
        db.String(100),
        nullable=False,
    )

    liked_cafes = db.relationship(
        "Cafe",
        secondary='likes',
        backref='liking_users'
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def get_full_name(self):
        """ Returns a string of “FIRSTNAME LASTNAME” """

        return (f"{self.first_name} {self.last_name}")

    def to_dict(self):
        """Serialize user to a dict of user info."""

        return {
            "id": self.id,
            "username": self.username,
            "admin": self.admin,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name
            # "liked_cafes": self.liked_cafes
        }

    @classmethod
    def register(
            cls,
            username,
            email,
            first_name,
            last_name,
            description,
            password,
            admin=True,
            image_url=DEFAULT_USER_IMAGE_URL,):
        """Sign up user.

        Hashes password and adds user to session.
        """

        hashed_pwd = bcrypt.generate_password_hash(
            password).decode('UTF-8')

        user = User(
            username=username,
            admin=admin,
            email=email,
            first_name=first_name,
            last_name=last_name,
            description=description,
            image_url=image_url,
            hashed_password=hashed_pwd,
        )

        db.session.add(user)

        return user

    @classmethod
    def authenticate(cls, username, password):
        """Searches for a user whose hashed password matches this password.
        If found, returns the user instance.

        If it can't find matching user (or if password is wrong), returns
        False.
        """

        user = cls.query.filter_by(username=username).one_or_none()

        if user:
            is_auth = bcrypt.check_password_hash(
                user.hashed_password, password)
            if is_auth:
                return user

        return False


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)

#######################################
# Likes model


class Like(db.Model):
    """Join table between users and cafes (the join represents a like)."""

    __tablename__ = 'likes'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        primary_key=True
    )

    cafe_id = db.Column(
        db.Integer,
        db.ForeignKey('cafes.id', ondelete='CASCADE'),
        nullable=False,
        primary_key=True
    )
