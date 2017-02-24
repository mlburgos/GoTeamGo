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
                   GroupPendingUser,
                   Goal,
                   Workout,
                   Like,
                   Personal_Goal,
                   db,
                   connect_to_db)

from helper import (verify_password,
                    register_new_user,
                    verify_login,
                    verify_email,
                    get_historical_workout_types_and_units,
                    get_user_profile_data,
                    get_weeks_workouts,
                    get_users_top_workouts,
                    calc_progress,
                    get_groups_and_current_goals,
                    get_group_profile_data,
                    get_friends_data,
                    verify_group_name_exists_helper,
                    handle_join_new_group_helper,
                    show_user_groups_helper,
                    handle_update_photo_helper,
                    handle_update_personal_goal_helper,
                    verify_group_name_is_unique_helper,
                    get_admin_groups_and_pending,
                    handle_new_group_helper,
                    handle_approve_to_group_helper,
                    get_admin_groups_and_members,
                    handle_remove_from_group_helper,
                    get_groups_you_can_leave,
                    get_admin_pending_count,
                    generate_bar_graph,
                    update_group_goal_helper,
                    handle_update_group_goal_helper,
                    )


from decorators import (login_required,
                        logout_required,
                        admin_required,
                        )

from datetime import datetime, date

import json

import plotly.plotly as py
import plotly.graph_objs as go

# from flask_bcrypt import Bcrypt

app = Flask(__name__)
# bcrypt = Bcrypt(app)

# Need to modify this later
app.secret_key = "SECRET_KEY"

# Prevent undefined variables from failing silently.
app.jinja_env.undefined = StrictUndefined


@app.route('/login')
@logout_required
def homepage():

    return render_template("user-login.html")
    # return render_template("user-login2.html")


@app.route('/login', methods=['POST'])
@logout_required
def handle_login():
    """Process Login"""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]

   # Returns user object.
    user = User.by_email(email)

    if not verify_password(user, password):
        flash("Incorrect password")
        return redirect("/login")

    # Returns a list of the group ids for which the user is an admin.
    admin_groups = GroupAdmin.by_user_id(user.user_id)

    session["user_id"] = user.user_id
    session["user_name"] = user.first_name

    session["is_admin"] = (len(admin_groups) != 0)

    flash("Logged in!")

    return redirect("/")


@app.route('/register')
@logout_required
def registration():

    return render_template("user-registration.html")


@app.route('/register', methods=['POST'])
@logout_required
def register_process():
    """Process registration."""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]
    first_name = request.form["first-name"]
    last_name = request.form["last-name"]

    user = register_new_user(email,
                             password,
                             first_name,
                             last_name,
                             )

    # Add user info to the session.
    session["user_id"] = user.user_id
    session["user_name"] = user.first_name

    flash("Welcome, %s! Log your first workout!" % first_name)

    return redirect("/")


@app.route('/verify_email_existence.json', methods=['POST'])
def verify_email_existence():
    """Verify email existence.
    Used to prevent multiple accounts for the same email address, and used to
    verify the account exists in the login process.
    """
    email = request.form["email"]

    return verify_email(email)


@app.route('/verify_email_and_pswd.json', methods=['POST'])
def verify_email_and_password():
    """Verify email existence and confirms password
    """
    email = request.form["email"]
    password = request.form.get("password")

    return verify_login(email, password)


@app.route('/')
@login_required
def new_workout():
    """Workout form."""

    user_id = session.get("user_id")

    types_units = get_historical_workout_types_and_units(user_id)

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
    return redirect("/login")


@app.route('/users/<int:user_id>')
@login_required
def user_profile(user_id):

    session_user_id = session.get('user_id')

    return render_template("user-profile.html",
                           user_info=get_user_profile_data(user_id, session_user_id),
                           )


@app.route('/groups/<int:group_id>')
@login_required
def group_profile(group_id):

    user_id = session.get('user_id')

    group_data = get_group_profile_data(group_id,
                                        user_id,
                                        )

    return render_template("group-profile.html",
                           group_name=group_data['group_name'],
                           workouts_for_board=group_data['workouts_for_board'],
                           group_goal=group_data['group_goal'],
                           group_id=group_data['group_id'],
                           is_group_admin=group_data['is_group_admin'],
                           users_full_info=group_data['users_full_info'],
                           )


@app.route('/friends')
@login_required
def freinds():

    user_id = session.get('user_id')
    friends_data = get_friends_data(user_id)

    if friends_data['has_friends']:
        return render_template("my-friends.html",
                               friends_full_info=friends_data['friends_full_info'],
                               workouts_for_board=friends_data['workouts_for_board'],
                               )

    flash("You're not currently connected to anyone.")
    return redirect("/users/{}".format(session.get('user_id')))


@app.route('/join_group')
@login_required
def join_new_group():

    user_id = session.get("user_id")

    return render_template("join-group.html",
                           user_id=user_id,
                           )


@app.route('/verify_group_name_exists.json', methods=['POST'])
def verify_group_name_exists():
    """Verify the requested group name exists.
    """

    return verify_group_name_exists_helper()


@app.route('/join_group', methods=['POST'])
@login_required
def handle_join_new_group():

    user_id = session.get('user_id')

    requested_group = request.form.get("group-name")

    handle_join_new_group_helper(user_id,
                                requested_group,
                                )

    flash("Request sent.")

    return redirect("/users/{}".format(session.get('user_id')))


@app.route('/groups')
@login_required
def show_user_groups():
    """Returns all groups of which the user is a member"""

    user_id = session.get('user_id')

    groups_data = show_user_groups_helper(user_id)

    return render_template("my-groups.html",
                           first_name=groups_data['first_name'],
                           groups=groups_data['groups'],
                           len_groups=len(groups_data['groups']),
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
    new_photo_url = request.form.get("photo-url")

    handle_update_photo_helper(user_id,
                               new_photo_url,
                               )

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

    handle_update_personal_goal_helper(user_id,
                                       personal_goal,
                                       )

    return redirect("/users/{}".format(user_id))


@app.route('/new_group')
@login_required
def create_new_group():

    user_id = session.get('user_id')

    return render_template("group-registration.html",
                           user_id=user_id,
                           )


@app.route('/verify_group_name_is_unique.json', methods=['POST'])
def verify_group_name_is_unique():
    """Verify group name uniqueness.
    """

    group_name = request.form["group_name"]

    return verify_group_name_is_unique_helper(group_name)


@app.route('/new_group', methods=['POST'])
@login_required
def handle_new_group():

    user_id = session.get('user_id')

    group_name = request.form.get("group-name")
    group_goal = request.form.get("group-goal")

    handle_new_group_helper(user_id,
                            group_name,
                            group_goal,
                            )

    return redirect("/users/{}".format(user_id))


@app.route('/approve_to_group')
@login_required
@admin_required
def approve_to_group():

    user_id = session.get('user_id')

    # Returns a dictionary of lists of tuples of info on the users pending
    # approval:
    # {group_name: [(user_id, user_name, pending_id),
    #               ],
    # }
    # ex: {Group1: [(1, "User1 Lname1", 1)]}
    admin_groups = get_admin_groups_and_pending(user_id)

    return render_template("admin.html",
                           user_id=user_id,
                           admin_groups=admin_groups,
                           )


@app.route('/approve_to_group', methods=['POST'])
@login_required
@admin_required
def handle_approve_to_group():
    """Receives a list of approved pending users, adds them to GroupUser, and
    deletes them from GroupPendingUser.
    """

    user_id = session.get('user_id')
    approved_pending_ids = request.form.getlist('check')

    handle_approve_to_group_helper(user_id,
                                   approved_pending_ids,
                                   )

    return redirect("/users/{}".format(user_id))


@app.route('/remove_from_group')
@login_required
@admin_required
def remove_from_group():

    user_id = session.get('user_id')

    # Returns a dictionary of lists of tuples of info on the users in each group:
    # {group_name: [(user_id, user_name, group_user_id),
    #               ],
    # }
    # ex: {Group1: [(1, "User1 Lname1", 1)]}
    admin_groups = get_admin_groups_and_members(user_id)

    return render_template("admin-remove.html",
                           user_id=user_id,
                           admin_groups=admin_groups,
                           )


@app.route('/remove_from_group', methods=['POST'])
@login_required
@admin_required
def handle_remove_from_group():
    """Recieves a list of approved pending users, adds them to GroupUser, and
    deletes them from GroupPendingUser.
    """

    user_id = session.get('user_id')
    remove_group_user_ids = request.form.getlist('check')

    handle_remove_from_group_helper(user_id,
                                    remove_group_user_ids,
                                    )

    return redirect("/users/{}".format(user_id))


@app.route('/leave_group')
@login_required
def leave_group():

    user_id = session.get('user_id')

    # Returns a dictionary of lists of tuples of info on the users in each group:
    # {group_name: [(user_id, user_name, group_user_id),
    #               ],
    # }
    # ex: {Group1: [(1, "User1 Lname1", 1)]}
    leavable_groups = get_groups_you_can_leave(user_id)

    return render_template("leave-group.html",
                           user_id=user_id,
                           leavable_groups=leavable_groups,
                           )


@app.route('/leave_group', methods=['POST'])
@login_required
def handle_leave_group():
    """Recieves a list of approved pending users, adds them to GroupUser, and
    deletes them from GroupPendingUser.
    """

    user_id = session.get('user_id')
    remove_group_user_ids = request.form.getlist('check')

    handle_remove_from_group_helper(user_id,
                                    remove_group_user_ids,
                                    )

    return redirect("/users/{}".format(user_id))


@app.route('/update_group_goal/<int:group_id>')
@login_required
@admin_required
def update_group_goal(group_id):

    user_id = session.get('user_id')

    updated_info = update_group_goal_helper(group_id,
                                            user_id,
                                            )

    return render_template("update-group-goal.html",
                           user_id=user_id,
                           group_name=updated_info['group_name'],
                           group_id=group_id,
                           group_goal=updated_info['group_goal'],
                           )


@app.route('/update_group_goal/<int:group_id>', methods=['POST'])
@login_required
@admin_required
def handle_update_group_goal(group_id):

    user_id = session.get('user_id')

    group_goal = request.form.get("group-goal")

    handle_update_group_goal_helper(group_id,
                                    user_id,
                                    group_goal,
                                    )

    return redirect("/groups/{}".format(group_id))


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