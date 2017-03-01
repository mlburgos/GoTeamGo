from model import (User,
                   GroupUser,
                   GroupPendingUser,
                   Group,
                   GroupAdmin,
                   Goal,
                   Workout,
                   Like,
                   Personal_Goal,
                   db,
                   connect_to_db)

import datetime

import plotly.graph_objs as go

from flask import (Flask,
                   request,
                   )

from graph_functions import generate_bar_graph

# import database_fns

from flask_bcrypt import Bcrypt

bcrypt_app = Flask(__name__)
bcrypt = Bcrypt(bcrypt_app)


COLOR_SCHEME = ['#B3E9FE', '#73D8FF', '#3AC9FF', '#07BAFF']


def hash_password(password):
    return bcrypt.generate_password_hash(password)


def register_new_user(email, password, first_name, last_name):
    """Creates a new user and sets a default personal goal of 0.
    """

    hashed_password = bcrypt.generate_password_hash(password)

    new_user = User(email=email,
                    password=hashed_password,
                    first_name=first_name,
                    last_name=last_name,
                    )

    db.session.add(new_user)
    db.session.commit()

    user = User.query.filter_by(email=email).first()

    # Set personal goal to 0 by default.
    personal_goal = Personal_Goal(user_id=user.user_id,
                                  date_iniciated=datetime.date.today(),
                                  personal_goal=0,
                                  )

    db.session.add(personal_goal)
    db.session.commit()

    return user


def verify_email(email):
    """Verify email existence.
    Used to prevent multiple accounts for the same email address, and used to
    verify the account exists in the login process.
    """

    # Test for email existence
    email_check = User.query.filter_by(email=email).all()

    if email_check == []:
        return {'existence': False,
                'msg': 'Email not found. Please try again, or register as a new user.'
                }

    return {'existence': True,
            'msg': "Email already in system. Login or try a different email."
            }


def verify_login(email, password):
    """Verify email existence, and if that passes, it verifies the password.

    """

    # Test for email existence
    email_check = User.query.filter_by(email=email).all()

    if email_check == []:
        return {'existence': False,
                'msg': 'Email not found. Please try again, or register as a new user.'}

    user = email_check[0]

    hashed_password = user.password

    if not bcrypt.check_password_hash(hashed_password, password):
        return {'existence': False,
                'msg': 'Incorrect password. Please try again.'}

    return {'existence': True,
            'msg': "Email already in system. Login or try a different email."}


def verify_password(user, password):
    """
    """

    hashed_password = user.password

    if not bcrypt.check_password_hash(hashed_password, password):
        return False

    return True


def get_historical_workout_types_and_units(user_id):
    """Returns all distinct types of workouts the user has previously entered
    as well as the distance units.

    >>> get_historical_workout_types_and_units()
    [(u'run', u'miles')]
    """

    # Get all previously logged workout types
    distinct_workouts = Workout.query\
                               .with_entities(Workout.exercise_type.distinct(),
                                              Workout.distance_unit,
                                              )

    return distinct_workouts.filter_by(user_id=user_id).all()


def get_admin_pending_count(user_id):
    """ Returns a count of the users pending approval into groups for which the
    user is an admin:
    """

    # Returns a list of the group ids for which the user is an admin.
    admin_groups = GroupAdmin.by_user_id(user_id)

    pending_users = GroupPendingUser.query\
                                    .filter(GroupPendingUser.group_id
                                                            .in_(admin_groups))\
                                    .all()

    return len(pending_users)


def get_navbar_data(user_id, is_admin):
    """Returns all groups of which the user is a member"""

    user = User.by_id(user_id)
    user_groups = user.groups

    groups = [(group.group_name,
               group.group_id,
               )
              for group in user_groups
              ]

    pending_approval = 0
    if is_admin:
        pending_approval = get_admin_pending_count(user_id)

    return {'groups': groups,
            'pending_approval': pending_approval,
            }


def get_user_profile_data(user_id, session_user_id, is_admin):
    is_my_profile = False

    if user_id == session_user_id:
        is_my_profile = True

    user = User.by_id(user_id)
    first_name = user.first_name
    user_photo = user.photo_url

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

    group_ids = [group[0] for group in groups]

    # Extends groups to include progress toward group goal and formatted progress.
    # [[group_id, group_name, goal, progress, formatted_progress]
    # ex: [[1, "Group1", 4, 0.50, "50%"]]
    full_group_info = [group + calc_progress(workout_count, group[2])
                       for group in groups]

    pending_approval = 0
    if is_admin:
        pending_approval = get_admin_pending_count(user_id)

    by_day_grouped_layout = go.Layout(
        title='Workouts by Day <br> <i>4 and 5 star performances by day</i>',
        barmode='grouped',
        legend=dict(orientation="h",
                    font=dict(
                        # family='sans-serif',
                        # size=12,
                        # color='#000',
                        )
                    ),
        yaxis=dict(
            title='# of Workouts',
            showgrid=False,
            ticks='outside',
        ),
        yaxis2=dict(
            title="% of Top Workouts",
            showgrid=False,
            ticks='outside',
            range=[0, 110],
            titlefont=dict(
                color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
            ),
            overlaying='y',
            side='right'),
        )

    by_hour_grouped_layout = go.Layout(
        title='Workouts by Hour <br> <i>4 and 5 star performances by day</i>',
        barmode='grouped',
        legend=dict(orientation="h",
                    font=dict(
                        # family='sans-serif',
                        # size=12,
                        # color='#000',
                        )
                    ),
        yaxis=dict(
            title='# of Workouts',
            showgrid=False,
            ticks='outside',
        ),
        yaxis2=dict(
            title="% of Top Workouts",
            showgrid=False,
            ticks='outside',
            range=[0, 110],
            titlefont=dict(
                color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
            ),
            overlaying='y',
            side='right'),
        )

    by_day_data_grouped, by_hour_data_grouped = generate_bar_graph(user_id)

    eight_week_data_by_day = by_day_data_grouped['eight_week_data']
    four_week_data_by_day = by_day_data_grouped['four_week_data']

    eight_week_by_day_fig = go.Figure(data=eight_week_data_by_day, layout=by_day_grouped_layout)
    four_week_by_day_fig = go.Figure(data=four_week_data_by_day, layout=by_day_grouped_layout)

    eight_week_data_by_hour = by_hour_data_grouped['eight_week_data']
    four_week_data_by_hour = by_hour_data_grouped['four_week_data']

    eight_week_by_hour_fig = go.Figure(data=eight_week_data_by_hour, layout=by_hour_grouped_layout)
    four_week_by_hour_fig = go.Figure(data=four_week_data_by_hour, layout=by_hour_grouped_layout)

    return {'is_my_profile': is_my_profile,
            'user_photo': user_photo,
            'first_name': first_name,
            'workout_count': workout_count,
            'personal_goal': personal_goal,
            'personal_progress': personal_progress,
            'personal_progress_formatted': personal_progress_formatted,
            'personal_valuemax': personal_valuemax,
            'full_group_info': full_group_info,
            'workouts_for_board': workouts_for_board,
            'pending_approval': pending_approval,
            'user_id': user_id,
            'group_ids': group_ids,
            'eight_week_by_day_fig': eight_week_by_day_fig,
            'four_week_by_day_fig': four_week_by_day_fig,
            'eight_week_by_hour_fig': eight_week_by_hour_fig,
            'four_week_by_hour_fig': four_week_by_hour_fig,
            }

################################################################################
# Supporting functions for get_user_profile_data


def get_weeks_workouts(user_id):
    """Returns the workouts done by a user in the week up to the current day.

    If today is a Thursday, it will count the workouts logged over the 4 day span
    from Monday to Thursday.
    """

    today = datetime.date.today()

    # using regular .weekday() instead of .isoweekday() to get the number of
    # days since monday since monday = 0
    days_from_monday = datetime.timedelta(days=today.weekday())

    nearest_monday = today - days_from_monday

    user_workouts = Workout.query.filter(Workout.user_id == user_id,
                                         Workout.workout_time >= nearest_monday)\
                                 .all()

    return user_workouts


def get_users_top_workouts(user_ids):
    """Returns the workouts done by a group of users in the week up to the
    current day. Only returns workouts with performance_rating >= 4.

    If today is a Thursday, it will count the workouts logged over the 4 day span
    from Monday to Thursday for members in the list of user_ids if they rated
    them a 4 or 5.
    """

    today = datetime.date.today()

    # using regular .weekday() instead of .isoweekday() to get the number of
    # days since monday since monday = 0
    days_from_monday = datetime.timedelta(days=today.weekday())

    nearest_monday = today - days_from_monday

    workouts = Workout.query.filter(Workout.user_id.in_(user_ids),
                                    Workout.workout_time >= nearest_monday,
                                    Workout.performance_rating >= 4)\
                            .all()

    workouts_for_board = [(workout.exercise_type,
                           workout.workout_time,
                           workout.performance_rating,
                           workout.distance,
                           workout.distance_unit,
                           workout.description,
                           User.get_name_by_id(workout.user_id),
                           )
                          for workout in workouts]

    return workouts_for_board

# End of supporting functions specifically for get_user_profile_data
################################################################################


def calc_progress(workout_count, goal):
    """Prevents division by 0 in calculating percent of goal accomplished.
    """

    if goal == 0:
        return [0, 0]
    else:
        progress = (float(workout_count)/goal)*100
        return [progress, "{0:.0f}%".format(progress)]


def get_groups_and_current_goals(user_id):
    """ Returns a list of tuples of the form:

    [(group_id, group_name, goal)]

    ex: [(1, "Group1", 4)]
    """

    user_groups = User.by_id(user_id).groups

    return [[group.group_id,
             group.group_name,
             Goal.get_current_goal(group.group_id),
             ]
            for group in user_groups]


def get_group_profile_data(group_id, user_id):
    """"""

    group = Group.by_id(group_id)
    group_name = group.group_name

    group_users = group.users

    group_users_ids = [user.user_id for user in group_users]
    workouts_for_board = get_users_top_workouts(group_users_ids)

    group_goal = Goal.get_current_goal(group_id)

    is_group_admin = (group_id in GroupAdmin.by_user_id(user_id))

    users_full_info = []

    for user in group_users:
        name = user.first_name + " " + user.last_name
        current_user_id = user.user_id

        # Returns the workouts done since most recent Monday.
        workouts = get_weeks_workouts(current_user_id)
        workout_count = len(workouts)

        progress, progress_formatted = calc_progress(workout_count, group_goal)

        users_full_info.append([user.user_id,
                                name,
                                user.photo_url,
                                workout_count,
                                progress,
                                progress_formatted
                                ])

    return {'group_name': group_name,
            'workouts_for_board': workouts_for_board,
            'group_goal': group_goal,
            'group_id': group_id,
            'is_group_admin': is_group_admin,
            'users_full_info': users_full_info,
            }


def get_friends_data(user_id):
    """"""


    user = User.by_id(user_id)

    groups = user.groups

    if groups == []:
        return {'has_friends': False}

    # Abstract this away to a get_friends helper method
    friends = []

    for group in groups:
        members = group.users
        for member in members:
            if member.user_id != user_id and member not in friends:
                friends.append(member)

    if friends == []:
        return {'has_friends': False}

    me_and_friends = [user] + friends

    me_and_friends_ids = [friend.user_id for friend in me_and_friends]
    workouts_for_board = get_users_top_workouts(me_and_friends_ids)

    friends_full_info = []
    for friend in me_and_friends:
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

    ###########################################################################
    # Try to alphebetize friends
    # alphabetical_friends_full_info = sorted(friends_full_info,
    #                                         key=lambda friend: friend[2]
    #                                         )

    # print "alphabetical_friends_full_info:", alphabetical_friends_full_info
    ###########################################################################

    return {'has_friends': True,
            'friends_full_info': friends_full_info,
            'workouts_for_board': workouts_for_board,
            }


def verify_group_name_exists_helper():
    """Verify the requested group name exists.
    """

    group_name = request.form["group_name"]

    # Test for group name uniqueness
    name_check = Group.by_name(group_name=group_name)
    if name_check is None:
        return {'success': False, 'msg': "Group name does not exist. Please verify the name and try again."}

    return {'success': True, 'msg': ''}


def handle_join_new_group_helper(user_id, requested_group):

    group_id = Group.by_name(requested_group).group_id

    new_group_pending_user = GroupPendingUser(user_id=user_id,
                                              group_id=group_id,
                                              )

    db.session.add(new_group_pending_user)
    db.session.commit()


def show_user_groups_helper(user_id):
    """Returns all groups of which the user is a member"""

    user = User.by_id(user_id)
    first_name = user.first_name
    user_groups = user.groups

    groups = [(group.group_name,
               group.group_id,
               )
              for group in user_groups
              ]

    return {'first_name': first_name,
            'groups': groups,
            }



def handle_update_photo_helper(user_id, new_photo_url):
    """Updates the users photo in the db."""

    user = User.by_id(user_id)
    user.photo_url = new_photo_url

    db.session.commit()


def handle_update_personal_goal_helper(user_id, personal_goal):
    """Updates the users personal goal in the db."""

    new_goal = Personal_Goal(user_id=user_id,
                             date_iniciated=datetime.datetime.now(),
                             personal_goal=personal_goal,
                             )

    db.session.add(new_goal)
    db.session.commit()


def verify_group_name_is_unique_helper(group_name):
    """Verify group name uniqueness.
    """

    # Test for group name uniqueness
    name_check = Group.by_name(group_name=group_name)
    if name_check is not None:
        return {'success': False, 'msg': "Name already in system. Please try a different name."}

    return {'success': True, 'msg': ''}


def get_admin_groups_and_pending(user_id):
    """ Returns a dictionary of lists of tuples of info on the users pending
    approval:

    {group_name: [(user_id, user_name, pending_user_id),
                   ],
     }

    ex: {Group1: [(1, "User1 Lname1", 1)]}
    """

    # Returns a list of tuples of group ids and group names for which the user
    # is an admin.
    admin_groups = GroupAdmin.get_group_names_by_user_id(user_id)

    pending = {}

    for group_id, group_name in admin_groups:
        # Returns a list of tuples of the form:
        # [(user_id, pending_id)]
        # where the pending_id is the id for GroupPendingUser
        pending_users = GroupPendingUser.by_group_id(group_id)

        if pending_users:
            full_pending_users = [(pending_user_id,
                                   User.get_name_by_id(pending_user_id),
                                   pending_id,
                                   )
                                  for pending_user_id, pending_id in pending_users
                                  ]
            pending[group_name] = full_pending_users

    return pending


def handle_new_group_helper(user_id, group_name, group_goal):

    new_group = Group(group_name=group_name,
                      )

    db.session.add(new_group)
    db.session.commit()

    group = Group.by_name(group_name)
    group_id = group.group_id

    new_group_user = GroupUser(user_id=user_id,
                               group_id=group_id,
                               )

    new_group_admin = GroupAdmin(group_id=group_id,
                                 user_id=user_id,
                                 )

    new_goal = Goal(group_id=group_id,
                    user_id=user_id,
                    date_iniciated=datetime.datetime.now(),
                    goal=group_goal,
                    )

    db.session.add(new_group_user)
    db.session.add(new_group_admin)
    db.session.add(new_goal)
    db.session.commit()


def handle_approve_to_group_helper(user_id, approved_pending_ids):
    """Receives a list of approved pending users, adds them to GroupUser, and
    deletes them from GroupPendingUser.
    """

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



def get_admin_groups_and_members(user_id):
    """ Returns a dictionary of lists of tuples of info on the users in each
    group:

    {group_name: [(user_id, user_name, group_user_id),
                   ],
     }

    ex: {Group1: [(1, "User1 Lname1", 1)]}
    """

    # Returns a list of tuples of group ids and group names for which the user
    # is an admin.
    admin_groups = GroupAdmin.get_group_names_by_user_id(user_id)

    members = {}

    for group_id, group_name in admin_groups:
        # Returns a list of tuples of the form:
        # [(user_id, group_user_id)]
        # where the group_user_id is the id for GroupUser
        current_users = GroupUser.by_group_id(group_id)

        if current_users:
            full_current_users = [(member_user_id,
                                   User.get_name_by_id(member_user_id),
                                   group_user_id,
                                   )
                                  for member_user_id, group_user_id in current_users
                                  if member_user_id != user_id
                                  ]
            members[group_name] = full_current_users

    return members


def handle_remove_from_group_helper(user_id, remove_group_user_ids):
    """Recieves a list of approved pending users, adds them to GroupUser, and
    deletes them from GroupPendingUser.
    """

    for pending_id in remove_group_user_ids:
        user_pending_removal = GroupUser.by_id(pending_id)

        db.session.delete(user_pending_removal)
        db.session.commit()


def get_groups_you_can_leave(user_id):
    """ Returns a dictionary of group_name: group_user_id for each group which
    the user is a member but not an admin.

    {group_name: group_user_id,
     }

    ex: {Group1: 1}
    """

    # Returns a list of tuples of group ids and group names for which the user
    # is an admin.
    admin_groups = GroupAdmin.get_group_names_by_user_id_dict(user_id)

    admin_group_ids = admin_groups.keys()

    # Returns a list of tuples group ids and group_user_id for which the user
    # is a member.
    # all_group_user_ids = GroupUser.by_user_id(user_id)

    # Returns a dict of group_id: group_user_id for which the user is a member.
    all_group_user_ids = GroupUser.by_user_id_dict(user_id)

    # get all group objects to which the user belongs.
    all_groups = User.by_id(user_id).groups

    groups_user_can_leave = {}

    for group in all_groups:
        if group.group_id not in admin_groups.keys():
            groups_user_can_leave[group.group_name] = all_group_user_ids[group.group_id]

    return groups_user_can_leave


def update_group_goal_helper(group_id, user_id):

    group_goal = Goal.get_current_goal(group_id)

    group_name = Group.by_id(group_goal).group_name

    return {'group_name': group_name,
            'group_goal': group_goal,
            }


def handle_update_group_goal_helper(group_id, user_id, group_goal):

    new_goal = Goal(group_id=group_id,
                    user_id=user_id,
                    date_iniciated=datetime.now(),
                    goal=group_goal,
                    )

    db.session.add(new_goal)
    db.session.commit()


##############################################################################

if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app

    connect_to_db(app)

    # Only have this un-commented for initial load.
    db.create_all()

    print "Connected to DB."
