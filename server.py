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
                   db,
                   connect_to_db)

from helper import (get_performances_by_day,
                    get_weeks_workout_count,
                    get_groups_and_current_goals,
                    calc_progress,
                    )

from datetime import datetime, date

import json

from functools import wraps


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


def login_required(f):
    """Decorator that will verify that prevent the user from accessing certain
    routes if they are not logged in.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" in session:
            return f(*args, **kwargs)
        else:
            flash("Please login to access this page.")
            return redirect('/login')

    return wrapper


@app.route('/register')
def registration():

    return render_template("user-registration.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables and test validity
    email = request.form["email"]
    password = request.form["password"]

    # Get remaining form variables
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


@app.route('/verify-email.json', methods=['POST'])
def verify():
    """Verify email uniqueness and password consistency.
    """

    email = request.form["email"]

    # Test for email uniqueness
    email_check = User.query.filter_by(email=email).all()
    if email_check != []:
        return_data = {'success': False, 'msg': "Email already in system. Login or try a different email."}
        return jsonify(return_data)

    return jsonify({'success': True, 'msg': ''})


@app.route('/')
@login_required
def new_workout():
    """Workout form."""

    user_id = session.get("user_id")

    # Get all previously logged workout types
    distinct_workouts = Workout.query.with_entities(Workout.exercise_type.distinct(), Workout.distance_unit)

    types_units = distinct_workouts.filter_by(user_id=user_id).all()
    print "types_units:", types_units

    return render_template("new-workout-form.html",
                           types_units=types_units,
                           )


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
@login_required
def user_profile(user_id):

    user = User.by_id(user_id)
    first_name = user.first_name
    user_photo = user.photo_url

    # Returns a dictionary of dictionaies:
    # {
    #  "workouts_by_day" = {1: 0, ..., 7: 0},
    #  "top_performances" = {1: 0, ..., 7: 0},
    #  "top_performance_ratio" = {1: 0, ..., 7: 0}
    #  }
    performance_by_day = get_performances_by_day(user_id)

    # Returns the number of workouts done since most recent Monday.
    workout_count = get_weeks_workout_count(user_id)

    # Returns most recently set personal goal.
    personal_goal = Personal_Goal.get_current_goal_by_user_id(user_id)

    personal_progress, personal_progress_formatted = calc_progress(workout_count, personal_goal)

    # Defines the max for the personal progress bar.
    personal_valuemax = max(personal_progress, 100)

    # Returns a list of lists of the form:
    # [[group_id, group_name, goal]
    # ex: [[1, "Group1", 4]]
    groups = get_groups_and_current_goals(user_id)

    # Extends groups to include progress toward group goal and formatted progress.
    # [[group_id, group_name, goal, progress, formatted_progress]
    # ex: [[1, "Group1", 4, 0.50, "50%"]]
    full_group_info = [group + calc_progress(workout_count, group[2])
                       for group in groups]

    return render_template("user-profile.html",
                           user_photo=user_photo,
                           first_name=first_name,
                           performance_by_day=json.dumps(performance_by_day),
                           workout_count=workout_count,
                           personal_goal=personal_goal,
                           personal_progress=personal_progress,
                           personal_progress_formatted=personal_progress_formatted,
                           personal_valuemax=personal_valuemax,
                           full_group_info=full_group_info,
                           )


@app.route('/groups/<int:group_id>')
@login_required
def group_profile(group_id):

    group = Group.by_id(group_id)
    group_name = group.group_name

    group_users = group.users

    group_goal = Goal.get_current_goal(group_id)

    users_full_info = []

    for user in group_users:
        name = user.first_name + " " + user.last_name
        # Returns the number of workouts done since most recent Monday.
        workout_count = get_weeks_workout_count(user.user_id)
        progress, progress_formatted = calc_progress(workout_count, group_goal)

        users_full_info.append([user.user_id,
                                name,
                                user.photo_url,
                                workout_count,
                                progress,
                                progress_formatted
                                ])

    print users_full_info

    return render_template("group-profile.html",
                           group_name=group_name,
                           group_goal=group_goal,
                           users_full_info=users_full_info,
                           )


@app.route('/friends')
@login_required
def show_user_group_mates():
    """"""

    user_id = session.get('user_id')
    user = User.by_id(user_id)

    groups = user.groups

    friends = []

    for group in groups:
        members = group.users
        for member in members:
            if member.user_id != user_id and member not in friends:
                friends.append(member)

    unique_friends = set(friends)

    friends_full_info = []

    for friend in unique_friends:
        name = friend.first_name + " " + friend.last_name

        # Returns the number of workouts done since most recent Monday.
        workout_count = get_weeks_workout_count(friend.user_id)

        # Returns most recently set personal goal.
        personal_goal = Personal_Goal.get_current_goal_by_user_id(friend.user_id)

        progress, progress_formatted = calc_progress(workout_count, personal_goal)

        friends_full_info.append([friend.user_id,
                                  name,
                                  friend.photo_url,
                                  workout_count,
                                  personal_goal,
                                  progress,
                                  progress_formatted
                                  ])

    print "friends_full_info:", friends_full_info

    # Try to alphebetize friends
    # alphabetical_friends_full_info = sorted(friends_full_info,
    #                                         key=lambda friend: friend[2]
    #                                         )

    # print "alphabetical_friends_full_info:", alphabetical_friends_full_info

    if friends_full_info == []:
        return redirect("/users/{}".format(user_id))

    return render_template("my-friends.html",
                           friends_full_info=friends_full_info,
                           )


@app.route('/join_group')
@login_required
def join_new_group():
    pass


@app.route('/groups')
@login_required
def show_user_groups():
    """Returns all groups the user """

    if 'user_id' in session:
        user_id = session.get('user_id')
        user = User.by_id(user_id)
        first_name = user.first_name
        user_groups = user.groups

        groups = [(group.group_name,
                   group.group_id,
                   )
                  for group in user_groups
                  ]

    else:
        flash("Please login")
        return redirect("/login")

    return render_template("my-groups.html",
                           first_name=first_name,
                           groups=groups,
                           len_groups=len(groups),
                           )


@app.route('/update_photo')
@login_required
def update_photo():

    user_id = session.get("user_id")

    return render_template("update-photo.html",
                           user_id=user_id,
                           )


@app.route('/update_photo', methods=['POST'])
@login_required
def handle_update_photo():
    """Updates the users phto in the db."""

    user_id = session.get('user_id')

    user = User.by_id(user_id)

    user.photo_url = request.form.get("photo-url")

    db.session.commit()

    return redirect("/users/{}".format(user_id),
                    )


@app.route('/update_personal_goal')
@login_required
def update_personal_goal():

    user_id = session.get('user_id')

    personal_goal = Personal_Goal.get_current_goal_by_user_id(user_id)

    return render_template("update-personal-goal.html",
                           user_id=user_id,
                           personal_goal=personal_goal,
                           )


@app.route('/update_personal_goal', methods=['POST'])
@login_required
def handle_update_personal_goal():

    user_id = session.get('user_id')

    personal_goal = request.form.get("personal-goal")

    new_goal = Personal_Goal(user_id=user_id,
                             date_iniciated=datetime.now(),
                             personal_goal=personal_goal,
                             )

    db.session.add(new_goal)
    db.session.commit()

    return redirect("/users/{}".format(user_id),
                    )

@app.route('/update_group_goal')
@login_required
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