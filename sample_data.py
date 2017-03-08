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

from datetime import datetime, date, timedelta

import math

import random

from flask import (Flask,
                   jsonify,
                   render_template,
                   redirect,
                   request,
                   flash,
                   session)


from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

MONICA_PIC = "http://fellowship.hackbrightacademy.com/media/CACHE/images/students/IMG_0005/6259c4fbf765821b3b73f6a0964592f9.jpg"


BATMAN_URL = 'https://mi-od-live-s.legocdn.com/r/www/r/catalogs/-/media/catalogs/characters/dc/mugshots/mugshot%202016/76061_1to1_mf_batman_336.png?l.r2=-798905063'

# Improves runtime to generate the passwords upfront.
HASHED_PASSWORDS = [bcrypt.generate_password_hash("pswd" + str(i))
                    for i in range(1, 15 + 1)]


FIRST_NAMES = ['Monica',
               'Bobby',
               'Bruce',
               'Lauren',
               'Ray',
               'Jess',
               'Rachel',
               'Signe',
               'Billy',
               'Evan',
               'Sam',
               'Jen',
               'Rick',
               'David',
               'Kianu',
               ]

LAST_NAMES = ['Burgos',
              'Dickerson',
              'Wayne',
              'Roberts',
              'Pritchett',
              'Ziai',
              'Applestein',
              'Pritchett',
              'Johnson',
              'Dickerson',
              'Wayne',
              'Roberts',
              'Pritchett',
              'Ziai',
              'Applestein',
              ]

# photos
squinty_guy = "https://images.pexels.com/photos/101584/pexels-photo-101584.jpeg?w=940&h=650&auto=compress&cs=tinysrgb"
ginger_serious_lady = "https://images.pexels.com/photos/27411/pexels-photo-27411.jpg?w=940&h=650&auto=compress&cs=tinysrgb"
bearded_blue_eyes = "https://images.pexels.com/photos/119705/pexels-photo-119705.jpeg?w=940&h=650&auto=compress&cs=tinysrgb"
shades_guy = "https://images.pexels.com/photos/108048/pexels-photo-108048.jpeg?h=350&auto=compress&cs=tinysrgb"
man_eating_burger = "https://images.pexels.com/photos/78225/pexels-photo-78225.jpeg?h=350&auto=compress&cs=tinysrgb"
jumping_canyon = "https://images.pexels.com/photos/6496/man-person-jumping-desert.jpg?h=350&auto=compress&cs=tinysrgb"
cute_smile = "https://images.pexels.com/photos/91227/pexels-photo-91227.jpeg?h=350&auto=compress&cs=tinysrgb"
guy_with_hat = "https://images.pexels.com/photos/173295/pexels-photo-173295.jpeg?h=350&auto=compress&cs=tinysrgb"
zen_guy = "https://images.pexels.com/photos/107868/pexels-photo-107868.jpeg?h=350&auto=compress&cs=tinysrgb"
canoe_lady = "https://images.pexels.com/photos/24486/pexels-photo-24486.jpg?h=350&auto=compress&cs=tinysrgb"
weight_lifter = "https://images.pexels.com/photos/17840/pexels-photo.jpg?h=350&auto=compress&cs=tinysrgb"
guy_with_lake = "https://images.pexels.com/photos/9692/pexels-photo.jpeg?h=350&auto=compress&cs=tinysrgb"
superman = "https://images.pexels.com/photos/38630/bodybuilder-weight-training-stress-38630.jpeg?h=350&auto=compress&cs=tinysrgb"
guy_tongue_out = "https://images.pexels.com/photos/45882/man-crazy-funny-dude-45882.jpeg?w=940&h=650&auto=compress&cs=tinysrgb"

PHOTOS = [MONICA_PIC,
          squinty_guy,
          BATMAN_URL,
          ginger_serious_lady,
          guy_tongue_out,
          shades_guy,
          man_eating_burger,
          jumping_canyon,
          cute_smile,
          guy_with_hat,
          zen_guy,
          canoe_lady,
          weight_lifter,
          guy_with_lake,
          superman,
          ]


def add_sample_users(num):
    """"""

    for i in range(1, num + 1):

        email = "User" + str(i) + "@gmail.com"
        hashed_password = HASHED_PASSWORDS[i - 1]

        new_user = User(first_name=FIRST_NAMES[i - 1],
                        last_name=LAST_NAMES[i - 1],
                        email=email,
                        password=hashed_password,
                        photo_url=PHOTOS[i - 1],
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
        group_id = (i % groups_to_add) + 1

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

    for i in range(1, num_users + 1):
        for j in range(1, 31 + 1):

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

            if (j == 1) or (j == 31):
                print new_workout

            db.session.add(new_workout)
            db.session.commit()

    # February workouts
    for i in range(1, num_users + 1):
        for j in range(1, 28 + 1):

            hour = random.randint(6, 22)
            user_id = i
            exercise_type = "run"
            workout_time = datetime(2017, 2, j, hour, 0)
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

    today = date.today()

    for i in range(1, 7):
        for j in range(1, today.day + 1):

            hour = random.randint(6, 22)
            user_id = i
            exercise_type = "run"
            workout_time = datetime(2017, today.month, j, hour, 0)
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

            if (j == 1) or (j == today.day + 1):
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


# def add_my_photo():
#     """Adds my photo to User1"""

#     me = User.by_id(1)
#     me.photo_url = "http://fellowship.hackbrightacademy.com/media/CACHE/images/students/IMG_0005/6259c4fbf765821b3b73f6a0964592f9.jpg"

#     db.session.commit()


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


def rename_user3():
    user3 = User.by_id(3)

    user3.first_name = "Bruce"
    user3.last_name = "Wayne"
    user3.photo_url = BATMAN_URL

    print user3
    db.session.commit()


def give_user3_personal_goals():
    """add goal of 6 to user3 as of 1/1
    """

    user3_goal = Personal_Goal(user_id=3,
                               date_iniciated=date(day=2, month=1, year=2017),
                               personal_goal=6,
                               )

    db.session.add(user3_goal)
    db.session.commit()

def rename_groups_1_and_4():
    group1 = Group.by_id(1)
    group4 = Group.by_id(4)

    group1.group_name = "Can't Beat Our Runtime"
    group4.group_name = "So QewL"

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
    add_sample_goals()
    # add_my_photo()
    add_sample_groups_pending_users()
    rename_user3()
    give_user3_personal_goals()
    rename_groups_1_and_4()
