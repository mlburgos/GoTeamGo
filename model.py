
"""Models and database functions for final project."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# import sample_data

db = SQLAlchemy()


class User(db.Model):
    """User of GoTeamGo website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True,
                        )
    first_name = db.Column(db.String(64),
                           nullable=False,
                           )
    last_name = db.Column(db.String(64),
                          nullable=False,
                          )
    email = db.Column(db.String(64),
                      nullable=False,
                      unique=True,
                      )
    password = db.Column(db.String(64),
                         nullable=False,
                         )
    photo_url = db.Column(db.String(600),
                          nullable=False,
                          default="https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png",
                          )

    # Defining relationships.
    groups = db.relationship("Group",
                             secondary="groups_users",
                             )

    admin_groups = db.relationship("Group",
                                   secondary="groups_admins",
                                   )

    workouts = db.relationship("Workout")

    goals = db.relationship("Goal")

    personal_goals = db.relationship("Personal_Goal")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)

    @classmethod
    def by_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def get_name_by_id(cls, user_id):
        user = cls.query.filter_by(user_id=user_id).first()
        return user.first_name + " " + user.last_name


class GroupUser(db.Model):
    """Serves as an association table between User and Group."""

    __tablename__ = "groups_users"

    group_user_id = db.Column(db.Integer,
                              autoincrement=True,
                              primary_key=True,
                              )
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'),
                        nullable=False,
                        )
    group_id = db.Column(db.Integer,
                         db.ForeignKey('groups.group_id'),
                         nullable=False,
                         )

    @classmethod
    def by_id(cls, group_user_id):
        return cls.query.filter_by(group_user_id=group_user_id).first()

    @classmethod
    def by_group_id(cls, group_id):
        """Returns a list of tuples of user ids and their group_user_id who are
        in the group.
        """

        members = cls.query.filter_by(group_id=group_id).all()
        return [(member.user_id,
                 member.group_user_id,
                 )
                for member in members
                ]

    @classmethod
    def by_user_id(cls, user_id):
        """Returns a list of tuples group ids and group_user_id for which the
        user is a member.
        """

        groups = cls.query.filter_by(user_id=user_id).all()
        return [(group.group_id, group.group_user_id) for group in groups]

    @classmethod
    def by_user_id_dict(cls, user_id):
        """Returns a dict of group_id: group_user_id for which the
        user is a member.
        """

        groups = cls.query.filter_by(user_id=user_id).all()

        result = {}
        for group in groups:
            result[group.group_id] = group.group_user_id

        return result


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<GroupUser user_id=%s group_id=%s>"\
               % (self.user_id, self.group_id)


class GroupPendingUser(db.Model):
    """Serves as an association table between User and Group."""

    __tablename__ = "groups_pending_users"

    pending_id = db.Column(db.Integer,
                           autoincrement=True,
                           primary_key=True,
                           )
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'),
                        nullable=False,
                        )
    group_id = db.Column(db.Integer,
                         db.ForeignKey('groups.group_id'),
                         nullable=False,
                         )

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<GroupPendingUser pending_id=%s user_id=%s group_id=%s>"\
               % (self.pending_id, self.user_id, self.group_id)

    @classmethod
    def by_id(cls, pending_id):
        return cls.query.filter_by(pending_id=pending_id).first()

    @classmethod
    def by_group_id(cls, group_id):
        """Returns a list of tuples of user ids and their pending_id who are
        pending approval to join the group.
        """

        pendings = cls.query.filter_by(group_id=group_id).all()
        return [(pending.user_id,
                 pending.pending_id,
                 )
                for pending in pendings
                ]


class Group(db.Model):
    """Organize users into groups"""

    __tablename__ = "groups"

    group_id = db.Column(db.Integer,
                         autoincrement=True,
                         primary_key=True,
                         )
    group_name = db.Column(db.String(64),
                           nullable=False,
                           unique=True,
                           )

    # Defining relationships.
    users = db.relationship("User",
                            secondary="groups_users",
                            )

    admins = db.relationship("User",
                             secondary="groups_admins",
                             )

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Group group_id=%s group_name=%s>"\
               % (self.group_id, self.group_name)

    @classmethod
    def by_id(cls, group_id):
        return cls.query.filter_by(group_id=group_id).first()

    @classmethod
    def by_name(cls, group_name):
        return cls.query.filter_by(group_name=group_name).first()


class GroupAdmin(db.Model):
    """Serves as an association table between Group and User.

    Keep track of who the administrators are for each group.

    Admin's have the power to change their group's goal and approve new members
    to join.
    Allows for groups to have multiple admins and users to serve as admins in
    multiple groups.
    """

    __tablename__ = "groups_admins"

    group_admin_id = db.Column(db.Integer,
                               autoincrement=True,
                               primary_key=True,
                               )
    group_id = db.Column(db.Integer,
                         db.ForeignKey('groups.group_id'),
                         nullable=False,
                         )
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'),
                        nullable=False,
                        )

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<GroupAdmin group_admin_id=%s group_id=%s user_id=%s>"\
               % (self.group_admin_id,
                  self.group_id,
                  self.user_id,
                  )

    @classmethod
    def by_user_id(cls, user_id):
        """Returns a list of the group ids for which the user is an admin.
        """

        groups = cls.query.filter_by(user_id=user_id).all()
        return [group.group_id for group in groups]

    @classmethod
    def by_group_id(cls, group_id):
        """Returns a list of the group admin user_ids for the admins of the group.
        """

        groups = cls.query.filter_by(group_id=group_id).all()
        return [group.user_id for group in groups]

    @classmethod
    def get_group_names_by_user_id(cls, user_id):
        """Returns a list of tuples of group ids and group names for which the
        user is an admin.
        """

        group_ids = cls.by_user_id(user_id)
        return [(group_id,
                 Group.by_id(group_id).group_name,
                 )
                for group_id in group_ids
                ]

    @classmethod
    def get_group_names_by_user_id_dict(cls, user_id):
        """Returns a dict of group_id: group_user_id for which the
        user is a member.
        """

        group_ids = cls.by_user_id(user_id)

        result = {}
        for group_id in group_ids:
            result[group_id] = Group.by_id(group_id).group_name

        return result


class Goal(db.Model):
    """Define and update group goals

    Keeps record of historical goals.
    """

    __tablename__ = "goals"

    goal_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True,
                        )
    group_id = db.Column(db.Integer,
                         db.ForeignKey('groups.group_id'),
                         nullable=False,
                         )
    # This user_id represents the user that SET the goal, not the user to whom
    # the goal corresponds. It corresponds to all the users in the group to
    # which the goal corresponds.
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'),
                        nullable=False,
                        )
    date_iniciated = db.Column(db.DateTime,
                               nullable=False,
                               )
    goal = db.Column(db.Integer,
                     nullable=False,
                     )

    # Defining relationships.
    users = db.relationship("User")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Goal group_id=%s date_iniciated=%s goal=%s>"\
               % (self.group_id, self.date_iniciated, self.goal)

    @classmethod
    def by_id(cls, goal_id):
        return cls.query.filter_by(goal_id=goal_id).first()

    @classmethod
    def get_current_goal(cls, group_id):
        return cls.query\
                  .filter_by(group_id=group_id)\
                  .order_by(Goal.date_iniciated.desc())\
                  .first()\
                  .goal


class Personal_Goal(db.Model):
    """Define and update personal goals

    Keeps record of personal goals.
    """

    __tablename__ = "personal_goals"

    personal_goal_id = db.Column(db.Integer,
                                 autoincrement=True,
                                 primary_key=True,
                                 )
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'),
                        nullable=False,
                        )
    date_iniciated = db.Column(db.DateTime,
                               nullable=False,
                               )
    personal_goal = db.Column(db.Integer,
                              nullable=False,
                              )

    # Defining relationships.
    user = db.relationship("User")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Personal_Goal user_id=%s date_iniciated=%s personal_goal=%s>"\
               % (self.user_id, self.date_iniciated, self.personal_goal)

    @classmethod
    def by_id(cls, personal_goal_id):
        return cls.query.filter_by(personal_goal_id=personal_goal_id).first()

    @classmethod
    def get_current_goal_by_user_id(cls, user_id):
        return cls.query\
                  .filter_by(user_id=user_id)\
                  .order_by(Personal_Goal.date_iniciated.desc())\
                  .first()\
                  .personal_goal


class Workout(db.Model):
    """Log workouts"""

    __tablename__ = "workouts"

    workout_id = db.Column(db.Integer,
                           autoincrement=True,
                           primary_key=True,
                           )
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'),
                        nullable=False,
                        )
    exercise_type = db.Column(db.String(64),
                              nullable=False,
                              )
    workout_time = db.Column(db.DateTime,
                             nullable=False,
                             )
    performance_rating = db.Column(db.Integer,
                                   nullable=False,
                                   )
    distance = db.Column(db.Float,
                         nullable=True,
                         )
    distance_unit = db.Column(db.String(10),
                              nullable=True,
                              )
    description = db.Column(db.String(150),
                            nullable=True,
                            )

    # Defining relationships.
    user = db.relationship("User")

    likes = db.relationship("Like")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Workout workout_id=%s user_id=%s workout_time=%s exercise_type=%s>"\
               % (self.workout_id,
                  self.user_id,
                  self.workout_time,
                  self.exercise_type,
                  )

    @classmethod
    def by_id(cls, workout_id):
        return cls.query.filter_by(workout_id=workout_id).first()



class Like(db.Model):
    """"Like teammates' workouts"""

    __tablename__ = "likes"

    like_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True,
                        )
    workout_id = db.Column(db.Integer,
                           db.ForeignKey('workouts.workout_id'),
                           nullable=False,
                           )
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'),
                        nullable=False,
                        )

    # Defining relationships.
    workout = db.relationship("Workout")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Like like_id=%s workout_id=%s user_id=%s>"\
               % (self.like_id, self.workout_id, self.user_id)

    @classmethod
    def by_id(cls, like_id):
        return cls.query.filter_by(like_id=like_id).first()


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our database.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///go_team_go'
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app

    connect_to_db(app)

    # Only have this un-commented for initial load.
    db.create_all()

    print "Connected to DB."
