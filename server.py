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

from helper import (user_login,
                    register_new_user,
                    verify_email,
                    get_historical_workout_types_and_units,
                    submit_new_workout,
                    get_user_profile_data,
                    get_weeks_workouts,
                    get_users_top_workouts,
                    calc_progress,
                    get_groups_and_current_goals,
                    get_group_profile_data,
                    get_friends_data,
                    verify_group_name_exists_helper,
                    get_admin_groups_and_pending,
                    get_admin_groups_and_members,
                    get_groups_you_can_leave,
                    get_admin_pending_count,
                    generate_bar_graph,
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

    if user_login():
        return redirect("/")

    return redirect("/login")


@app.route('/register')
@logout_required
def registration():

    return render_template("user-registration.html")


@app.route('/register', methods=['POST'])
@logout_required
def register_process():
    """Process registration."""

    register_new_user()

    return redirect("/")


@app.route('/verify_email_existence.json', methods=['POST'])
def verify_email_existence():
    """Verify email existence.
    Used to prevent multiple accounts for the same email address, and used to
    verify the account exists in the login process.
    """

    return verify_email()


@app.route('/')
@login_required
def new_workout():
    """Workout form."""

    types_units = get_historical_workout_types_and_units()

    return render_template("new-workout-form.html",
                           types_units=types_units,
                           )


@app.route('/', methods=['POST'])
def handle_new_workout():
    """Process new workout."""

    submit_new_workout()

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

    return render_template("user-profile.html",
                           user_info=get_user_profile_data(user_id),
                           )


@app.route('/groups/<int:group_id>')
@login_required
def group_profile(group_id):

    group_data = get_group_profile_data(group_id)

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

    friends_data = get_friends_data()

    if friends_data['has_friends']:
        return render_template("my-friends.html",
                               friends_full_info=friends_data['friends_full_info'],
                               workouts_for_board=friends_data['workouts_for_board'],
                               )

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
    """Receives a list of approved pending users, adds them to GroupUser, and
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

    for pending_id in remove_group_user_ids:
        user_pending_removal = GroupUser.by_id(pending_id)

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
                           user_id=user_id,
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