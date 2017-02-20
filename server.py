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

from helper import (get_performances_by_day,
                    get_weeks_workouts,
                    get_groups_and_current_goals,
                    calc_progress,
                    get_admin_groups_and_pending,
                    get_admin_groups_and_members,
                    get_groups_you_can_leave,
                    get_admin_pending_count,
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

    admin_groups = GroupAdmin.by_user_id(user.user_id)

    session["is_admin"] = (len(admin_groups) != 0)

    flash("Logged in")
    return redirect("/")


def login_required(f):
    """Decorator that will prevent the user from accessing certain
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


def admin_required(f):
    """Decorator that will prevent non-admins from accessing the approve_to_group
    routes
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if "is_admin":
            return f(*args, **kwargs)
        else:
            flash("Sorry, this page is for admin only.")
            user_id = session.get('user_id')
            return redirect("/users/{}".format(user_id))

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


@app.route('/verify_email.json', methods=['POST'])
def verify_email():
    """Verify email uniqueness.
    """

    email = request.form["email"]

    # Test for email uniqueness
    email_check = User.query.filter_by(email=email).all()
    if email_check is not None:
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

    is_my_profile = False

    if user_id == session.get('user_id'):
        is_my_profile = True

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

    # Returns the workouts done since most recent Monday.
    workouts = get_weeks_workouts(user_id)
    workout_count = len(workouts)

    workouts_for_board = [(workout.exercise_type,
                           workout.workout_time,
                           workout.performance_rating,
                           workout.distance,
                           workout.distance_unit,
                           workout.description,
                           )
                          for workout in workouts]


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

    pending_approval = 0
    if session.get('is_admin'):
        pending_approval = get_admin_pending_count(user_id)

    return render_template("user-profile.html",
                           is_my_profile=is_my_profile,
                           user_photo=user_photo,
                           first_name=first_name,
                           performance_by_day=json.dumps(performance_by_day),
                           workout_count=workout_count,
                           personal_goal=personal_goal,
                           personal_progress=personal_progress,
                           personal_progress_formatted=personal_progress_formatted,
                           personal_valuemax=personal_valuemax,
                           full_group_info=full_group_info,
                           workouts_for_board=workouts_for_board,
                           pending_approval=pending_approval,
                           )


@app.route('/groups/<int:group_id>')
@login_required
def group_profile(group_id):

    group = Group.by_id(group_id)
    group_name = group.group_name

    group_users = group.users

    group_goal = Goal.get_current_goal(group_id)

    user_id = session.get('user_id')
    is_group_admin = (group_id in GroupAdmin.by_user_id(user_id))
    print "is_group_admin:", is_group_admin

    users_full_info = []

    for user in group_users:
        name = user.first_name + " " + user.last_name

        # Returns the workouts done since most recent Monday.
        workouts = get_weeks_workouts(user_id)
        workout_count = len(workouts)

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
                           group_id=group_id,
                           is_group_admin=is_group_admin,
                           users_full_info=users_full_info,
                           )


@app.route('/friends')
@login_required
def show_user_group_mates():
    """"""

    user_id = session.get('user_id')
    user = User.by_id(user_id)

    groups = user.groups


    # Abstract this away to a get_friends helper method
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

        # Returns the workouts done since most recent Monday.
        workouts = get_weeks_workouts(friend.user_id)
        workout_count = len(workouts)

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

    ###########################################################################
    # Try to alphebetize friends
    # alphabetical_friends_full_info = sorted(friends_full_info,
    #                                         key=lambda friend: friend[2]
    #                                         )

    # print "alphabetical_friends_full_info:", alphabetical_friends_full_info
    ###########################################################################

    if friends_full_info == []:
        return redirect("/users/{}".format(user_id))

    return render_template("my-friends.html",
                           friends_full_info=friends_full_info,
                           )


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

    group_name = request.form["group_name"]

    # Test for group name uniqueness
    name_check = Group.by_name(group_name=group_name)
    if name_check is None:
        return_data = {'success': False, 'msg': "Group name does not exist. Please verify the name and try again."}
        return jsonify(return_data)

    return jsonify({'success': True, 'msg': ''})


@app.route('/join_group', methods=['POST'])
@login_required
def handle_join_new_group():

    user_id = session.get('user_id')

    requested_group = request.form.get("group-name")

    group_id = Group.by_name(requested_group).group_id

    new_group_pending_user = GroupPendingUser(user_id=user_id,
                                              group_id=group_id,
                                              )

    db.session.add(new_group_pending_user)
    db.session.commit()

    flash("Request sent.")
    return redirect("/users/{}".format(user_id))


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

    # Test for group name uniqueness
    name_check = Group.by_name(group_name=group_name)
    if name_check is not None:
        return_data = {'success': False, 'msg': "Name already in system. Please try a different name."}
        return jsonify(return_data)

    return jsonify({'success': True, 'msg': ''})


@app.route('/new_group', methods=['POST'])
@login_required
def handle_new_group():

    user_id = session.get('user_id')

    group_name = request.form.get("group-name")
    group_goal = request.form.get("group-goal")

    new_group = Group(group_name=group_name,
                      )

    db.session.add(new_group)
    db.session.commit()

    group = Group.by_name(group_name)
    group_id = group.group_id

    new_group_user = GroupUser(user_id=user_id,
                               group_id=group_id,
                               approved=True,
                               )

    new_group_admin = GroupAdmin(group_id=group_id,
                                 user_id=user_id,
                                 )

    new_goal = Goal(group_id=group_id,
                    user_id=user_id,
                    date_iniciated=datetime.now(),
                    goal=group_goal,
                    )

    db.session.add(new_group_user)
    db.session.add(new_group_admin)
    db.session.add(new_goal)
    db.session.commit()

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
    """Recieves a list of approved pending users, adds them to GroupUser, and
    deletes them from GroupPendingUser.
    """

    user_id = session.get('user_id')
    approved_pending_ids = request.form.getlist('check')

    for pending_id in approved_pending_ids:
        pending_user = GroupPendingUser.by_id(pending_id)
        pending_user_id = pending_user.user_id
        group_id = pending_user.group_id

        new_member = GroupUser(user_id=pending_user_id,
                               group_id=group_id,
                               )

        db.session.add(new_member)
        db.session.commit()

        db.session.delete(pending_user)
        db.session.commit()

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

    for pending_id in remove_group_user_ids:
        user_pending_removal = GroupUser.by_id(pending_id)

        db.session.delete(user_pending_removal)
        db.session.commit()

    return redirect("/users/{}".format(user_id))


@app.route('/leave_group')
@login_required
def leave_group():

    user_id = session.get('user_id')
    print "user_id:", user_id

    # Returns a dictionary of lists of tuples of info on the users in each group:
    # {group_name: [(user_id, user_name, group_user_id),
    #               ],
    # }
    # ex: {Group1: [(1, "User1 Lname1", 1)]}
    leavable_groups = get_groups_you_can_leave(user_id)

    print "leavable_groups:", leavable_groups

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

    for pending_id in remove_group_user_ids:
        user_pending_removal = GroupUser.by_id(pending_id)
        print "user_pending_removal:", user_pending_removal

        db.session.delete(user_pending_removal)
        db.session.commit()

    return redirect("/my_profile".format(user_id))


@app.route('/update_group_goal/<int:group_id>')
@login_required
@admin_required
def update_group_goal(group_id):

    user_id = session.get('user_id')

    if user_id not in GroupAdmin.by_group_id(group_id):
        flash("Sorry, only admins for this group can update the group's goal.")
        return redirect('/groups/<int:group_id>')

    group_goal = Goal.get_current_goal(group_id)

    group_name = Group.by_id(group_goal).group_name

    return render_template("update-group-goal.html",
                           group_name=group_name,
                           group_id=group_id,
                           group_goal=group_goal,
                           )


@app.route('/update_group_goal/<int:group_id>', methods=['POST'])
@login_required
@admin_required
def handle_update_group_goal(group_id):

    user_id = session.get('user_id')

    group_goal = request.form.get("group-goal")

    new_goal = Goal(group_id=group_id,
                    user_id=user_id,
                    date_iniciated=datetime.now(),
                    goal=group_goal,
                    )

    db.session.add(new_goal)
    db.session.commit()

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