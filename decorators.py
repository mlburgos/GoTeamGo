from flask import (flash,
                   session,
                   redirect,
                   )

from functools import wraps


def login_required(f):
    """Decorator that will prevent the user from accessing certain
    routes if they are not logged in.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" in session:
            return f(*args, **kwargs)
        else:
            flash("Please login to access this page.")
            return redirect('/login')

    return wrapper


def logout_required(f):
    """Decorator that will prevent the user from accessing certain
    routes (for example /login) if they are logged in.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return f(*args, **kwargs)
        else:
            flash("Please logout to access this page.")
            return redirect('/users/{}'.format(session.get('user_id')))

    return wrapper


def admin_required(f):
    """Decorator that will prevent non-admins from accessing the approve_to_group
    routes
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if "is_admin":
            return f(*args, **kwargs)
        else:
            flash("Sorry, this page is for admin only.")
            user_id = session.get('user_id')
            return redirect("/users/{}".format(user_id))

    return wrapper
