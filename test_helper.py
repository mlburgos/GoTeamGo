from unittest import TestCase

import unittest

from server import app

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

from test_data import (add_sample_users,
                       add_sample_groups,
                       assign_group_users,
                       assign_group_admins,
                       add_sample_workouts,
                       add_sample_likes,
                       add_sample_goals,
                       add_my_photo,
                       add_sample_groups_pending_users,
                       )

from helper import (register_new_user,
                    verify_email,
                    verify_login,
                    verify_password,
                    get_historical_workout_types_and_units,
                    get_admin_pending_count,
                    get_navbar_data,
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
                    update_group_goal_helper,
                    handle_update_group_goal_helper,
                    )

from results_for_tests import (get_user_profile_matching_session_id_is_admin_result,
                               get_user_profile_mismatching_session_id_is_admin_result,
                               get_users_top_workouts_results,
                               get_weeks_workouts_results,
                               )

from flask import (Flask,
                   jsonify,
                   )

from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)


INCORRECT_PASSWORD = "wrong"
NON_EXISTANT_EMAIL = "fake@gmail.com"

TEST_EMAIL = "bob@gmail.com"
TEST_PASSWORD = "bob1"
TEST_FIRST_NAME = "bob"
TEST_LAST_NAME = "robert"

class TestsThatDontNeedAFreshDB(TestCase):

    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all tests."""

        # Connect to test database
        connect_to_db(app, "postgresql:///test_go_team_go")

        # Create tables and add sample data
        db.create_all()
        add_sample_users(15)
        add_sample_groups(3)
        assign_group_users(15)
        assign_group_admins(15)
        add_sample_workouts(30, 15)
        add_sample_likes(30, 15)
        add_sample_goals()
        add_my_photo()
        add_sample_groups_pending_users()

    @classmethod
    def tearDownClass(cls):
        """Do after all tests."""

        db.session.close()
        db.drop_all()

    # def test_register_new_user(self):

    #     email = TEST_EMAIL
    #     password = TEST_PASSWORD
    #     first_name = TEST_FIRST_NAME
    #     last_name = TEST_LAST_NAME

    #     user = register_new_user(email,
    #                              password,
    #                              first_name,
    #                              last_name,
    #                              )

    #     assert user.email == "bob@gmail.com"

    #     hashed_password = user.password
    #     assert bcrypt.check_password_hash(hashed_password, password)

    #     assert user.first_name == "bob"
    #     assert user.last_name == "robert"

    #     personal_goal = Personal_Goal.get_current_goal_by_user_id(user.user_id)

    #     assert personal_goal == 0

    # def test_verify_email(self):

    #     existing_email = "User1@gmail.com"

    #     existing_email_respose = {'existence': True,
    #                               'msg': "Email already in system. Login or try a different email."
    #                               }

    #     assert verify_email(existing_email) == existing_email_respose

    #     # Test case: email is not in the database.
    #     non_existing_email_respose = {'existence': False,
    #                                   'msg': 'Email not found. Please try again, or register as a new user.'
    #                                   }

    #     assert verify_email(NON_EXISTANT_EMAIL) == non_existing_email_respose

    # def test_verify_login(self):

    #     # Test case: email and password are correct.
    #     existing_email = "User1@gmail.com"
    #     password = "pswd1"

    #     existing_email_respose = {'existence': True,
    #                               'msg': "Email already in system. Login or try a different email."
    #                               }

    #     assert verify_login(existing_email, password) == existing_email_respose

    #     # Test case: email is incorrect.
    #     non_existing_email_respose = {'existence': False,
    #                                   'msg': 'Email not found. Please try again, or register as a new user.'}

    #     assert verify_login(NON_EXISTANT_EMAIL, password) == non_existing_email_respose

    #     # Test case: email is correct BUT password is incorrect.

    #     incorrect_password_response = {'existence': False,
    #                                    'msg': 'Incorrect password. Please try again.'}

    #     assert verify_login(existing_email, INCORRECT_PASSWORD) == incorrect_password_response

    # def test_verify_password(self):

    #     user = User.by_id(1)

    #     # Test case: correct password
    #     password = "pswd1"

    #     assert verify_password(user, password) is True

    #     # Test case: incorrect password

    #     assert verify_password(user, INCORRECT_PASSWORD) is False

    # def test_get_historical_workout_types_and_units(self):

    #     user_id = 1
    #     assert get_historical_workout_types_and_units(user_id) == [(u'run', u'miles')]

    # def test_get_admin_pending_count(self):

    #     assert get_admin_pending_count(user_id=1) == 0

    #     assert get_admin_pending_count(user_id=3) == 4

    # def test_get_navbar_data(self):

    #     # Test case: verifying structure of return data
    #     assert get_navbar_data(1, False) == {'groups': [(u'Group1', 1),
    #                                                     (u'Group2', 2)
    #                                                     ],
    #                                          'pending_approval': 0
    #                                          }

    # def test_get_user_profile_data(self):

    #     # Test case 1: the current user is viewing their profile and is_admin

    #     user_id = 1
    #     session_user_id = 1
    #     is_admin = True

    #     assert get_user_profile_data(user_id, session_user_id, is_admin) == get_user_profile_matching_session_id_is_admin_result

    #     # Test case 2: the current user is viewing someone else's profile and is_admin
    #     mismatching_session_user_id = 2

    #     assert get_user_profile_data(user_id, mismatching_session_user_id, is_admin) == get_user_profile_mismatching_session_id_is_admin_result

    #     # Test case 3: the current user is viewing their profile and is not is_admin

    #     is_admin = False

    #     assert get_user_profile_data(user_id, session_user_id, is_admin) == get_user_profile_matching_session_id_is_admin_result

    #     # Test case 4: the current user is viewing someone else's profile and is not is_admin

    #     assert get_user_profile_data(user_id, mismatching_session_user_id, is_admin) == get_user_profile_mismatching_session_id_is_admin_result

    # def test_get_weeks_workouts(sefl):

    #     user_id = 1
    #     # change the result to a string because the format of the instance _repr_
    #     # doesn't read well in python
    #     assert str(get_weeks_workouts(user_id)) == get_weeks_workouts_results

    # def test_get_users_top_workouts(self):

    #     user_ids = [1, 2, 3]
    #     assert get_users_top_workouts(user_ids) == get_users_top_workouts_results

    # def test_calc_progress(self):

    #     assert calc_progress(workout_count=4, goal=10) == [40.0, '40%']

    #     assert calc_progress(workout_count=0, goal=10) == [0.0, '0%']

    #     assert calc_progress(workout_count=4, goal=0) == [0, 0]

    # def test_get_groups_and_current_goals(self):

    #     assert get_groups_and_current_goals(user_id=1) == [[1, u'Group1', 4], [2, u'Group2', 4]]

    #     assert get_groups_and_current_goals(user_id=2) == [[3, u'Group3', 4]]

    #     assert get_groups_and_current_goals(user_id=3) == [[1, u'Group1', 4], [4, u'Group4', 4]]

    def function():
        
        print "get_group_profile_data(group_id, user_id):", get_group_profile_data(group_id, user_id)

    def function():
        
        get_friends_data(user_id)

    def function():
        
        verify_group_name_exists_helper(group_id)

    def function():
        
        handle_join_new_group_helper(user_id, requested_group)

    def function():
        
        show_user_groups_helper(user_id)

    def function():
        handle_update_photo_helper(user_id, new_photo_url)


# class TestsThatNeedAFreshDB(TestCase):

#     def setUp(self):
#         """Stuff to do before every test."""

#         # Connect to test database
#         connect_to_db(app, "postgresql:///test_go_team_go")

#         # Create tables and add sample data
#         db.create_all()
#         add_sample_users(15)
#         add_sample_groups(3)
#         assign_group_users(15)
#         assign_group_admins(15)
#         add_sample_workouts(30, 15)
#         add_sample_likes(30, 15)
#         add_sample_goals()
#         add_my_photo()
#         add_sample_groups_pending_users()

#     def tearDown(self):
#         """Do at end of every test."""

#         db.session.close()
#         db.drop_all()


if __name__ == "__main__":
    unittest.main()

