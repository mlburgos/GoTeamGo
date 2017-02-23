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

import plotly.plotly as py
import plotly.graph_objs as go

# import bcrypt

from flask import (Flask,
                   jsonify,
                   render_template,
                   redirect,
                   request,
                   flash,
                   session)



def get_performances_by_day(user_id):
    """Returns the count of 4 or 5 star workouts by day to which days tend to
    yield better performances

    """

    workouts = Workout.query.filter(Workout.user_id == user_id).all()
                                        # ((Workout.performance_rating == 4) |
                                        #  (Workout.performance_rating == 5))).all()

    workouts_by_day = {1: 0,
                       2: 0,
                       3: 0,
                       4: 0,
                       5: 0,
                       6: 0,
                       7: 0,
                       }

    top_performances = {1: 0,
                        2: 0,
                        3: 0,
                        4: 0,
                        5: 0,
                        6: 0,
                        7: 0,
                        }

    top_performance_ratio = {1: 0,
                             2: 0,
                             3: 0,
                             4: 0,
                             5: 0,
                             6: 0,
                             7: 0,
                             }

    for workout in workouts:
        day_of_week = workout.workout_time.isoweekday()

        workouts_by_day[day_of_week] += 1

        if workout.performance_rating >= 4:
            top_performances[day_of_week] += 1

    for day in top_performance_ratio:
        if workouts_by_day[day] > 0:
            top_performance_ratio[day] = float(top_performances[day])/workouts_by_day[day]

    print "workouts_by_day:", workouts_by_day
    print "top_performances:", top_performances
    print "top_performance_ratio:", top_performance_ratio

    return {"workouts_by_day": workouts_by_day,
            "top_performances": top_performances,
            "top_performance_ratio": top_performance_ratio,
            }


def hasher(password):
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    return hashed_password


def check_password(password, hashed):
    if bcrypt.checkpw(password, hashed):
        return True

    return False


def register_new_user(email, password, first_name, last_name):
    """"""

    from server import bcrypt

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

    # Add user info to the session.
    session["user_id"] = user.user_id
    session["user_name"] = user.first_name

    flash("User %s added. Log your first workout!" % email)


def user_login(email, password):
    """"""

    from server import bcrypt


    user = User.query.filter_by(email=email).first()

    hashed_password = user.password

    if not bcrypt.check_password_hash(hashed_password, password):
        flash("Incorrect password")
        return False

    session["user_id"] = user.user_id
    session["user_name"] = user.first_name

    admin_groups = GroupAdmin.by_user_id(user.user_id)

    session["is_admin"] = (len(admin_groups) != 0)

    flash("Logged in!")
    return True


def generate_seven_day_dict(start_date):
    """"""

    seven_day_dict = {}

    for i in xrange(7):
        days_to_add = datetime.timedelta(days=i)
        seven_day_dict[start_date + days_to_add] = 0

    return seven_day_dict


def generate_bar_graph(user_id):
    """"""

    today = datetime.date.today()

    # using regular .weekday() instead of .isoweekday() to get the number of
    # days since monday since monday = 0
    days_from_monday = datetime.timedelta(days=today.weekday())

    nearest_monday = today - days_from_monday

    days_49 = datetime.timedelta(days=49)

    eight_mondays_ago = nearest_monday - days_49

    user_workouts = Workout.query.filter(Workout.user_id == user_id,
                                         Workout.workout_time >= eight_mondays_ago,
                                         Workout.performance_rating >= 4)\
                                 .all()

    X_LABELS = ['Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday',
                ]

    eight_mondays = [(eight_mondays_ago + datetime.timedelta(days=7*i))
                     for i in xrange(8)]

    data = []

    for monday in eight_mondays:
        current_week = generate_seven_day_dict(monday)

        for workout in user_workouts:
            workout_date = workout.workout_time.date()
            if workout_date in current_week:
                current_week[workout_date] += 1

        if monday == nearest_monday:
            name = "Current Week"
        else:
            name = str(monday.month) + "/" + str(monday.day) + "/" + str(monday.year)

        trace = go.Bar(x=X_LABELS,
                       y=current_week.values(),
                       name=name,
                       )

        data.append(trace)

    return data


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


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app

    # bcrypt = Bcrypt(app)

    connect_to_db(app)

    # Only have this un-commented for initial load.
    db.create_all()

    print "Connected to DB."
