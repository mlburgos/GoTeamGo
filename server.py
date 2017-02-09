from jinja2 import StrictUndefined

from flask import (Flask,
                   jsonify,
                   render_template,
                   redirect,
                   request,
                   flash,
                   session)

from flask_debugtoolbar import DebugToolbarExtension

from model import (User,
                   GroupUser,
                   Group,
                   GroupAdmin,
                   Goal,
                   Workout,
                   Like,
                   Photo,
                   db,
                   connect_to_db)

from helper import best_day

import json

app = Flask(__name__)

# Need to modify this later
app.secret_key = "ABC"

# Prevent undefined variables from failing silently.
app.jinja_env.undefined = StrictUndefined


@app.route('/login')
def homepage():

    return render_template("user-login.html")


@app.route('/login', methods=['POST'])
def handle_login():
    """Process Login"""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("Email address not found")
        return redirect("/")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/")

    session["user_id"] = user.user_id
    session["user_name"] = user.first_name

    flash("Logged in")
    return redirect("/")


@app.route('/register')
def registration():

    return render_template("user-registration.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]
    first_name = request.form["first-name"]
    last_name = request.form["last-name"]

    new_user = User(email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    )

    db.session.add(new_user)
    db.session.commit()

    flash("User %s added." % email)
    return redirect("/")


@app.route('/')
def new_workout():
    """Workout form."""

    if 'user_id' in session:
        user_id = session.get("user_id")

        # Get all previously logged workout types
        distinct_workouts = Workout.query.with_entities(Workout.exercise_type.distinct(), Workout.distance_unit)

        types_units = distinct_workouts.filter_by(user_id=user_id).all()

        print "types_units:", types_units
        return render_template("new-workout-form.html",
                               types_units=types_units,
                               )
    else:
        return redirect("/login")


@app.route('/', methods=['POST'])
def handle_new_workout():
    """Process new workout."""

    # Get user_id from session
    user_id = session.get("user_id")

    # Get form variables
    exercise_type = request.form["exercise-type"].lower()

    workout_time = request.form["workout-time"]
    performance_rating = request.form["performance-rating"]
    distance = request.form["distance"]
    distance_unit = request.form["distance-unit"].lower()
    description = request.form["description"]

    new_user = User(user_id=user_id,
                    exercise_type=exercise_type,
                    workout_time=workout_time,
                    performance_rating=performance_rating,
                    distance=distance,
                    distance_unit=distance_unit,
                    description=description,
                    )

    db.session.add(new_user)
    db.session.commit()

    flash("User %s added." % email)
    return redirect("/users/<int:user_id>")


@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")


@app.route('/users/<user_id>')
def user_profile(user_id):

    user_photo_obj = Photo.query.filter_by(user_id=user_id).first()
    if user_photo_obj is None:
        user_photo = ""
    else:
        user_photo = user_photo_obj.photo_url

    user = User.query.filter_by(user_id=user_id).first()
    first_name = user.first_name

    # Returns a dictionary of the following dictionaries:
    # 1) workouts_by_day
    # 2) top_performances
    # 3) top_performance_ratio
    performance_by_day = best_day(user_id)

    print performance_by_day

    return render_template("user-profile.html",
                           user_photo=user_photo,
                           first_name=first_name,
                           performance_by_day=json.dumps(performance_by_day),
                           )


@app.route('/groups/<int:group_id>')
def group_profile(group_id):
    pass


@app.route('/group_mates')
def show_user_group_mates():
    pass


@app.route('/groups')
def show_user_groups():
    pass


##############################################################################
# Helper functions



##############################################################################


if __name__ == "__main__":
    # Set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)



    app.run(port=5000, host='0.0.0.0')