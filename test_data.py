
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

from datetime import datetime

from flask import (Flask,
                   )


from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)


# Improves runtime to generate the passwords upfront.
HASHED_PASSWORDS = [bcrypt.generate_password_hash("pswd" + str(i))
                    for i in range(1, 15 + 1)]


def add_sample_users(num):
    """"""

    # from server import bcrypt

    for i in range(1, num + 1):

        first_name = "User" + str(i)
        last_name = "Lname" + str(i)
        email = "User" + str(i) + "@gmail.com"
        hashed_password = HASHED_PASSWORDS[i - 1]

        new_user = User(first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=hashed_password,
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

    # Adding this to test the admin page
    new_group = Group(group_name="Group4",
                      )
    print new_group
    db.session.add(new_group)
    db.session.commit()


def assign_group_users(num):

    for i in range(1, num + 1):

        user_id = i
        group_id = (i % 3) + 1

        new_group_user = GroupUser(user_id=user_id,
                                   group_id=group_id,
                                   )
        print new_group_user
        db.session.add(new_group_user)
        db.session.commit()

    # Add User1 to group 1 as well for testing purposes.
    new_group_user1 = GroupUser(user_id=1,
                                group_id=1,
                                )

    # Add User3 to group 4 as well to test the admin page.
    new_group_user2 = GroupUser(user_id=3,
                                group_id=4,
                                )

    print new_group_user1
    print new_group_user2
    db.session.add(new_group_user1)
    db.session.add(new_group_user2)
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

    # Add User3 as admin for group 4 as well to test the admin page.
    new_group_admin4 = GroupAdmin(user_id=3,
                                  group_id=4,
                                  )

    print new_group_admin1
    print new_group_admin2
    print new_group_admin3
    print new_group_admin4

    db.session.add(new_group_admin1)
    db.session.add(new_group_admin2)
    db.session.add(new_group_admin3)
    db.session.add(new_group_admin4)
    db.session.commit()


def add_sample_workouts(num_workouts, num_users):
    """"""

    # January workouts
    for i in range(1, num_users + 1):
        for j in range(1, num_workouts + 1):

            hour = (j % 15) + 6
            user_id = i
            exercise_type = "run"
            workout_time = datetime(2017, 1, j, hour, 0)
            performance_rating = (j % 5) + 1
            distance = (j % 10) + 1
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

    # February workouts
    for i in range(1, num_users + 1):
        for j in range(1, 28 + 1):

            hour = (j % 15) + 6
            user_id = i
            exercise_type = "run"
            workout_time = datetime(2017, 1, j, hour, 0)
            performance_rating = (j % 5) + 1
            distance = (j % 10) + 1
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

    # March workouts
    for i in range(1, 7):
        for j in range(1, 8 + 1):

            hour = (j % 15) + 6
            user_id = i
            exercise_type = "run"
            workout_time = datetime(2017, 3, j, hour, 0)
            performance_rating = (j % 5) + 1
            distance = (j % 10) + 1
            distance_unit = "miles"

            new_workout = Workout(user_id=user_id,
                                  exercise_type=exercise_type,
                                  workout_time=workout_time,
                                  performance_rating=performance_rating,
                                  distance=distance,
                                  distance_unit=distance_unit,
                                  )

            if (j == 1) or (j == 8):
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


def add_sample_goals():

    # Defines the group_id: admin's user_id
    group_admin = {1: 3,
                   2: 1,
                   3: 2,
                   4: 3,
                   }

    # Defines the [Day component of datetime obj, goal in terms of number of
    # workouts].
    # The first two are set for mondays, and the third is a wednesday. I will be
    # implementing logic to have the wednesday goal declaration apply from the
    # most recent monday. In this case that will be 1/16/2017. I will also want
    # this goal to apply for all subsequent weeks until it is updated again.
    days_and_goals = {1: [2, 4],
                      2: [9, 8],
                      3: [18, 4],
                      }

    for day_and_goal in days_and_goals.values():
        for group in group_admin:
            group_id = group
            user_id = group_admin[group]
            date_iniciated = datetime(2017, 1, day_and_goal[0])
            goal = day_and_goal[1]

            new_goal = Goal(group_id=group_id,
                            user_id=user_id,
                            date_iniciated=date_iniciated,
                            goal=goal,
                            )

            print new_goal
            db.session.add(new_goal)
            db.session.commit()

    user1_goal = Personal_Goal(user_id=1,
                               date_iniciated=datetime(2017, 1, 1),
                               personal_goal=7,
                               )

    user2_goal = Personal_Goal(user_id=2,
                               date_iniciated=datetime(2017, 1, 1),
                               personal_goal=3,
                               )

    print "user1_goal:", user1_goal
    print "user2_goal:", user2_goal

    db.session.add(user1_goal)
    db.session.add(user2_goal)
    db.session.commit()

    for x in xrange(3, 15 + 1):
        user_goal = Personal_Goal(user_id=x,
                                  date_iniciated=datetime(2017, 1, 1),
                                  personal_goal=0,
                                  )

        print "user"+str(x)+"_goal:", user_goal

        db.session.add(user_goal)
        db.session.commit()


def add_my_photo():
    """Adds my photo to User1"""

    me = User.by_id(1)
    me.photo_url = "http://fellowship.hackbrightacademy.com/media/CACHE/images/students/IMG_0005/6259c4fbf765821b3b73f6a0964592f9.jpg"

    db.session.commit()


def add_sample_groups_pending_users():
    """"""

    pending_user_1 = GroupPendingUser(user_id=2,
                                      group_id=1,
                                      )
    pending_user_2 = GroupPendingUser(user_id=5,
                                      group_id=1,
                                      )
    pending_user_3 = GroupPendingUser(user_id=8,
                                      group_id=1,
                                      )
    pending_user_4 = GroupPendingUser(user_id=2,
                                      group_id=4,
                                      )
    print pending_user_1
    print pending_user_2
    print pending_user_3
    print pending_user_4

    db.session.add(pending_user_1)
    db.session.add(pending_user_2)
    db.session.add(pending_user_3)
    db.session.add(pending_user_4)
    db.session.commit()


