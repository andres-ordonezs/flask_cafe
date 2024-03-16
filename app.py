"""Flask App for Flask Cafe."""

from models import db, connect_db, Cafe, City, User, DEFAULT_USER_IMAGE_URL
from forms import (CafeForm, SignupForm, LoginForm, ProfileEditForm)
from sqlalchemy.exc import IntegrityError
import os

from flask import Flask, render_template, redirect, flash, session, jsonify, g, request
from flask_debugtoolbar import DebugToolbarExtension


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///flask_cafe')
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "shhhh")

if app.debug:
    app.config['SQLALCHEMY_ECHO'] = True

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)

#######################################
# auth & auth routes

CURR_USER_KEY = "curr_user"
NOT_LOGGED_IN_MSG = "You are not logged in."


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


#######################################
# homepage

@app.get("/")
def homepage():
    """Show homepage."""

    return render_template("homepage.html")


#######################################
# cafes


@app.get('/cafes')
def cafe_list():
    """Return list of all cafes."""

    cafes = Cafe.query.order_by('name').all()

    return render_template(
        'cafe/list.html',
        cafes=cafes,
        user=g.user
    )


@app.get('/cafes/<int:cafe_id>')
def cafe_detail(cafe_id):
    """Show detail for cafe."""

    liked_cafes = []
    cafe = Cafe.query.get_or_404(cafe_id)

    map_url = cafe.get_cafe_map()

    if g.user:
        liked_cafes = [c.id for c in g.user.liked_cafes]

    return render_template(
        'cafe/detail.html',
        cafe=cafe,
        user=g.user,
        liked_cafes=liked_cafes,
        map_url=map_url
    )


@app.route('/cafes/add', methods=["GET", "POST"])
def add_cafe():
    """Add a cafe:

    Show form if GET. If valid, add cafe and redirect to new cafe detail page.
    """

    form = CafeForm()

    cities = get_city_choices()

    form.city_code.choices = cities

    try:
        if form.validate_on_submit():
            name = form.name.data
            description = form.description.data
            url = form.url.data
            address = form.address.data
            city_code = form.city_code.data
            image_url = form.image.data

            cafe = Cafe(
                name=name,
                description=description,
                url=url,
                address=address,
                city_code=city_code,
                image_url=image_url
            )

            db.session.add(cafe)

            db.session.flush()

            cafe.get_cafe_map()

            db.session.commit()

            flash(f"{name} added", "success")

            return redirect(f"/cafes/{cafe.id}")

    except IntegrityError:
        return render_template("/cafe/add-form.html", form=form)

    return render_template("/cafe/add-form.html", form=form)


@app.route('/cafes/<int:cafe_id>/edit', methods=["GET", "POST"])
def edit_cafe(cafe_id):
    """ Edit a cafe:

    Show form if GET. If valid, edits cafe and redirect to cafe detail page.
    """

    cafe = Cafe.query.get_or_404(cafe_id)

    form = CafeForm(obj=cafe)

    cities = get_city_choices()

    form.city_code.choices = cities

    try:
        # breakpoint()
        if form.validate_on_submit():
            # breakpoint()
            cafe.name = form.name.data
            cafe.description = form.description.data
            cafe.url = form.url.data
            cafe.address = form.address.data
            cafe.city_code = form.city_code.data
            cafe.image_url = form.image.data or DEFAULT_USER_IMAGE_URL

            db.session.commit()

            flash(f"{cafe.name} edited", "info")

            return redirect(f"/cafes/{cafe.id}")

    except IntegrityError:
        db.session.rollback()

        # return render_template("/cafe/add-form.html", form=form)

    # breakpoint()
    return render_template("/cafe/edit-form.html", form=form, cafe=cafe)


def get_city_choices():
    """Get choices for cities' select field. Return list of cities"""

    cities = [(c.code, c.name) for c in City.query.all()]

    return cities


#######################################
# users

@app.get('/profile')
def show_profile():
    """ Show user's profile page """

    if not g.user:
        flash(NOT_LOGGED_IN_MSG, "danger")
        return redirect('/login')

    return render_template("/profile/detail.html", user=g.user)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    """ Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    do_logout()

    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.register(
                username=form.username.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                description=form.description.data,
                email=form.email.data,
                password=form.password.data,
                image_url=form.image_url.data or None,
                admin=True  # TODO: check this
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('/auth/signup-form.html', form=form)

        do_login(user)

        flash("You are signed up and logged in.", 'success')
        return redirect("/cafes")

    else:
        return render_template("/auth/signup-form.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Handles login and redirects to cafe list on success  """

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            form.username.data,
            form.password.data
        )

        if user:
            do_login(user)
            flash(f"Hello, {user.username}", "success")

            return redirect("/cafes")

        else:
            flash(f"Wrong username - password combination", "danger")
            return redirect("/cafes")

    else:

        return render_template("auth/login-form.html", form=form)


@app.post('/logout')
def logout():
    """ Handle logout of user and redirect to homepage. """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/cafes")

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/")


@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """Update profile for current user.

    Redirect to user page on success.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/profile")

    user = g.user
    form = ProfileEditForm(obj=user)

    if form.validate_on_submit():
        user.first_name = form.first_name.data,
        user.last_name = form.last_name.data,
        user.description = form.description.data,
        user.email = form.email.data,
        user.image_url = form.image_url.data or None,
        user.admin = True  # TODO: check this
        try:
            db.session.commit()
            flash("Profile edited", 'success')

            return redirect('/profile')

        except IntegrityError:
            flash("There was a problem editing the user", 'danger')
            return render_template(
                '/profile/edit-form.html',
                form=form,
                user=user)

    else:
        return render_template('/profile/edit-form.html', form=form)

#######################################
# liked cafes


@app.get('/api/likes')
def cafe_is_liked():
    """ Given cafe_id in the URL query string,
      figure out if the current user likes that cafe,
      and return JSON: {"likes": true|false} """

    user_id = int(request.args.get('userId'))
    cafe_id = int(request.args.get('cafeId'))

    likes = False

    user = User.query.get_or_404(user_id)

    if cafe_id in [c.id for c in user.liked_cafes]:
        likes = True

    return jsonify(likes=likes)


@app.post('/api/like')
def like_cafe():
    """ Given JSON e.g.{"cafe_id": 1}, make the current user like cafe #1 """

    data = request.json

    cafe_id = data['cafeId']
    user_id = data['userId']

    user = User.query.get_or_404(user_id)

    if not user:
        return jsonify(error="Not logged in")

    else:
        cafe = Cafe.query.get_or_404(cafe_id)
        user.liked_cafes.append(cafe)

        db.session.commit()

        return jsonify(liked=cafe_id)


@app.post('/api/unlike')
def unlike_cafe():
    """ Given JSON e.g.{"cafe_id": 1}, make the current user like cafe #1 """

    data = request.json

    cafe_id = data['cafeId']
    user_id = data['userId']

    user = User.query.get_or_404(user_id)

    if not user:
        return jsonify(error="Not logged in")

    else:
        cafe = Cafe.query.get_or_404(cafe_id)
        user.liked_cafes.remove(cafe)

        db.session.commit()

        return jsonify(unliked=cafe_id)

#######################################
# 404 page


@app.errorhandler(404)
def page_not_found(error):
    """ Return 404 page """

    return render_template('/404.html'), 404
