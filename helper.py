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

import datetime


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


def get_weeks_workout_count(user_id):
    """Counts the number of workouts done by a user in the week up to the current
    day.

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

    return len(user_workouts)


def calc_progress(workout_count, goal):
    """Prevents division by 0 in calculating percent of goal accomplished.
    """

    if goal == 0:
        return 0
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


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app

    connect_to_db(app)

    # Only have this un-commented for initial load.
    db.create_all()

    print "Connected to DB."
