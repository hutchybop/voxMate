import functools
from flask import session, redirect, url_for


def isLoggedIn(route):
    @functools.wraps(route)
    def wrapper(*args, **kwargs):
        if session.get("_id") is None:
            return redirect(url_for("users.login"))
        
        return route(*args, **kwargs)
    return wrapper
