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
                   Personal_Goal,
                   Photo,
                   db,
                   connect_to_db)

from helper import (get_performances_by_day,
                    get_weeks_workout_count)

from datetime import datetime

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

    user = User.query.filter_by(email=email).first()

    # Add user info to the session.
    session["user_id"] = user.user_id
    session["user_name"] = user.first_name

    # Set personal goal to 0 by default.
    personal_goal = Personal_Goal(user_id=user.user_id,
                                  date_iniciated=date.today(),
                                  personal_goal=0,
                                  )

    db.session.add(personal_goal)
    db.session.commit()

    flash("User %s added. Log your first workout!" % email)
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
    performance_rating = int(request.form["performance-rating"])

    # Set distance to None if no distance was entered to prevent db error.
    distance = request.form["distance"]
    if distance == "":
        distance = None

    distance_unit = request.form["distance-unit"].lower()
    description = request.form["description"]

    # Set workout_time to current date and time if no date or time were entered.
    workout_time = request.form["workout-time"]
    if workout_time == "":
        workout_time = datetime.now()

    new_workout = Workout(user_id=user_id,
                          exercise_type=exercise_type,
                          workout_time=workout_time,
                          performance_rating=performance_rating,
                          distance=distance,
                          distance_unit=distance_unit,
                          description=description,
                          )

    db.session.add(new_workout)
    db.session.commit()

    flash("Workout added!")
    return redirect("/friends")



@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")


@app.route('/users/<int:user_id>')
def user_profile(user_id):

    user_photo_obj = Photo.query.filter_by(user_id=user_id).first()
    if user_photo_obj is None:
        user_photo = "https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png"
    else:
        user_photo = user_photo_obj.photo_url

    user = User.query.filter_by(user_id=user_id).first()
    first_name = user.first_name

    # Returns a dictionary of the following dictionaries:
    # 1) workouts_by_day
    # 2) top_performances
    # 3) top_performance_ratio
    performance_by_day = get_performances_by_day(user_id)

    # Returns the number of workouts done since most recent Monday.
    workout_count = get_weeks_workout_count(user_id)

    # Returns most recently set personal goal.
    personal_goal = Personal_Goal.query\
                                 .filter_by(user_id=user_id)\
                                 .order_by(Personal_Goal.date_iniciated.desc())\
                                 .first()\
                                 .personal_goal

    # Prevents division by 0.
    if personal_goal == 0:
        personal_progress = 0
    else:
        personal_progress = (float(workout_count)/personal_goal)*100

    personal_progress_formatted = "{0:.0f}%".format(personal_progress)

    # Defines the max for the personal progress bar.
    personal_valuemax = max(personal_progress, 100)

    groups = [(1, "Group1", 4)]

    print performance_by_day

    return render_template("user-profile.html",
                           user_photo=user_photo,
                           first_name=first_name,
                           performance_by_day=json.dumps(performance_by_day),
                           workout_count=workout_count,
                           personal_goal=personal_goal,
                           personal_progress=personal_progress,
                           personal_progress_formatted=personal_progress_formatted,
                           personal_valuemax=personal_valuemax,
                           groups=groups,
                           )


@app.route('/groups/<int:group_id>')
def group_profile(group_id):

    group = Group.query.filter_by(group_id=group_id).first()
    group_name = group.group_name

    group_users = group.users

    goal = Goal.query.filter_by(group_id=group_id)\
                     .order_by(Goal.date_iniciated.desc())\
                     .first()

    user_id_user_name_workouts = []
    # 
    # Start with figuring out the logic for each user separately, ie on the
    # user_profile page and then implement it here
    # 
    # for user in group_users:


    return render_template("group-profile.html",
                           group_name=group_name,
                           )


@app.route('/friends')
def show_user_group_mates():
    """"""

    user_id = session.get('user_id')

    # my_friends = {group_id: {
    #                            group_name: "name",
    #                            members: {
    #                                      user_id: "name",
    #                                      }
    #                          }
    #               }

    my_friends = {}

    if my_friends == {}:
        return redirect("/users/{}".format(user_id))

    return render_template("my-friends.html")


@app.route('/join_group')
def join_new_group():
    pass


@app.route('/groups')
def show_user_groups():
    """Returns all groups the user """

    user_id = session.get('user_id')
    user = User.query.filter_by(user_id=user_id).first()
    first_name = user.first_name
    groups = []

    if 'user_id' in session:
        user_groups = user.groups

        for group in user_groups:
            groups.append((group.group_name, group.group_id))
    else:
        flash("Please login")
        return redirect("/login")

    return render_template("my-groups.html",
                           first_name=first_name,
                           groups=groups,
                           len_groups=len(groups),
                           )


@app.route('/update_personal_goal')
def update_p_goal():

    pass


@app.route('/update_group_goal')
def update_g_goal():
    
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