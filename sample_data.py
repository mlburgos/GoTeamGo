from model import User, GroupUser, Group, GroupAdmin, Goal, Workout, Like, db, connect_to_db
from datetime import datetime
import math
import random

def add_sample_users(num):
    """"""

    for i in range(1, num + 1):

        first_name = "User" + str(i)
        last_name = "Lname" + str(i)
        email = "User" + str(i) + "@gmail.com"
        password = "pswd" + str(i)

        new_user = User(first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password,
                        )

        print new_user
        db.session.add(new_user)
        db.session.commit()


def add_sample_groups(num):
    """"""

    for i in range(1, num + 1):

        group_name = "Group" + str(i)

        new_group = Group(group_name=group_name,
                          )

        print new_group
        db.session.add(new_group)
        db.session.commit()


def assign_group_users(num):

    for i in range(1, num + 1):

        user_id = i
        group_id = (i % groups_to_add) + 1
        approved = True

        new_group_user = GroupUser(user_id=user_id,
                                   group_id=group_id,
                                   approved=approved,
                                   )
        print new_group_user
        db.session.add(new_group_user)
        db.session.commit()


def assign_group_admins(num):
    """Manually created this to ensure that the user_id and group_id match

    This will break if you change the number of groups_to_add"""

    new_group_admin1 = GroupAdmin(user_id=3,
                                  group_id=1,
                                  )
    new_group_admin2 = GroupAdmin(user_id=1,
                                  group_id=2,
                                  )
    new_group_admin3 = GroupAdmin(user_id=2,
                                  group_id=3,
                                  )

    print new_group_admin1
    print new_group_admin2
    print new_group_admin3

    db.session.add(new_group_admin1)
    db.session.add(new_group_admin2)
    db.session.add(new_group_admin3)
    db.session.commit()


def add_sample_workouts(num_workouts, num_users):
    """"""

    for i in range(1, num_users + 1):
        for j in range(1, num_workouts + 1):

            hour = random.randint(6, 22)
            user_id = i
            exercise_type = "run"
            workout_time = datetime(2017, 1, j, hour, 0)
            performance_rating = random.randint(1, 5)
            distance = random.randint(1, 10)
            distance_unit = "miles"

            new_workout = Workout(user_id=user_id,
                                  exercise_type=exercise_type,
                                  workout_time=workout_time,
                                  performance_rating=performance_rating,
                                  distance=distance,
                                  distance_unit=distance_unit,
                                  )

            if (j == 1) or (j == num_workouts):
                print new_workout

            db.session.add(new_workout)
            db.session.commit()


def add_sample_likes(num_workouts, num_users):
    """User1 is liking every fifth workout that is in the db."""

    for j in range(1, num_users*num_workouts + 1):
        if j % 5 == 0:
            new_like = Like(workout_id=j,
                            user_id=1,
                            )

            if (j % 15 == 0):
                print new_like

            db.session.add(new_like)
            db.session.commit()


if __name__ == '__main__':

    from server import app

    connect_to_db(app)

    users_to_add = 15
    groups_to_add = users_to_add/5
    workouts_to_add = 30

    add_sample_users(users_to_add)
    add_sample_groups(groups_to_add)
    assign_group_users(users_to_add)
    assign_group_admins(users_to_add)
    add_sample_workouts(workouts_to_add, users_to_add)
    add_sample_likes(workouts_to_add, users_to_add)
