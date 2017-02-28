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
                    get_weeks_workouts,
                    )

from flask import (Flask,
                   jsonify,
                   )

from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)


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

    def test_register_new_user(self):

        email = "bob@gmail.com"
        password = "bob1"
        first_name = "bob"
        last_name = "robert"

        user = register_new_user(email,
                                 password,
                                 first_name,
                                 last_name,
                                 )

        assert user.email == "bob@gmail.com"

        hashed_password = user.password
        assert bcrypt.check_password_hash(hashed_password, password)

        assert user.first_name == "bob"
        assert user.last_name == "robert"

        personal_goal = Personal_Goal.get_current_goal_by_user_id(user.user_id)

        assert personal_goal == 0

    def test_verify_email(self):

        existing_email = "fake"

        existing_email_respose = {'existence': True,
                                  'msg': "Email already in system. Login or try a different email."
                                  }

        assert verify_email(existing_email) == existing_email_respose

        non_existing_email = "fake@gmail.com"

        non_existing_email_respose = {'existence': False,
                                      'msg': 'Email not found. Please try again, or register as a new user.'
                                      }

        assert verify_email(non_existing_email) == non_existing_email_respose

    def test_verify_login(self):

        # Test case: email and password are correct.
        existing_email = "User1@gmail.com"
        password = "pswd1"

        existing_email_respose = {'existence': True,
                                  'msg': "Email already in system. Login or try a different email."
                                  }

        assert verify_login(existing_email, password) == existing_email_respose

        # Test case: email is incorrect.
        non_existing_email = "fake@gmail.com"

        non_existing_email_respose = {'existence': False,
                                      'msg': 'Email not found. Please try again, or register as a new user.'}

        assert verify_login(non_existing_email, password) == non_existing_email_respose

        # Test case: email is correct BUT password is incorrect.
        incorrect_password = "wrong"

        incorrect_password_response = {'existence': False,
                                       'msg': 'Incorrect password. Please try again.'}

        assert verify_login(existing_email, incorrect_password) == incorrect_password_response

    def test_verify_password(self):
        
        user = User.by_id(1)
        
        # Test case: correct password
        password = "pswd1"

        verify_password(user, password)



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

