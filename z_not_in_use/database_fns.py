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


def add_new_user(email,
                 password,
                 first_name,
                 last_name,
                 ):
    """"""

    new_user = User(email=email,
                    password=hashed_password,
                    first_name=first_name,
                    last_name=last_name,
                    )

    db.session.add(new_user)
    db.session.commit()
