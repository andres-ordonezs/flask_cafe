from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, PasswordField
from wtforms.validators import InputRequired, Email, Length, URL, Optional

#######################################
# Cafe form


class CafeForm(FlaskForm):
    """Form for adding/editing a Flask Cafe."""

    name = StringField(
        "Name",
        validators=[InputRequired()]
    )

    description = TextAreaField(
        "Description",
        validators=[Optional(), Length(min=10)]
    )

    url = StringField(
        "URL",
        validators=[Optional(), URL()])

    address = StringField(
        "Address",
        validators=[InputRequired()]
    )

    city_code = SelectField(
        "City",
        coerce=str
    )

    image = StringField(
        "Image",
        validators=[Optional(), URL(), Length(max=255)]
    )

#######################################
# User form


class SignupForm(FlaskForm):
    """ Form for signing up a user """

    username = StringField(
        "Username",
        validators=[InputRequired()]
    )

    first_name = StringField(
        "First Name",
        validators=[InputRequired()]
    )

    last_name = StringField(
        "Last Name",
        validators=[InputRequired()]
    )

    description = TextAreaField(
        "Description",
        validators=[Optional()]
    )

    email = StringField(
        "Email",
        validators=[InputRequired(), Email()]
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=6)]
    )

    image_url = StringField(
        "Image",
        validators=[Optional(), URL()]
    )


class LoginForm(FlaskForm):
    """ Form for logging in a user """

    username = StringField(
        "Username",
        validators=[InputRequired()]
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired()]
    )


class ProfileEditForm(FlaskForm):
    """ Form for editing a user's profile """

    first_name = StringField(
        "First Name",
        validators=[InputRequired()]
    )

    last_name = StringField(
        "Last Name",
        validators=[InputRequired()]
    )

    description = TextAreaField(
        "Description",
        validators=[Optional()]
    )

    email = StringField(
        "Email",
        validators=[InputRequired(), Email()]
    )

    image_url = StringField(
        "Image",
        validators=[Optional(), URL()]
    )
