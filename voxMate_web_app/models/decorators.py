import functools
from flask import session, redirect, url_for, flash, request, current_app
import requests
from time import sleep


def isLoggedIn(route):
    @functools.wraps(route)
    def wrapper(*args, **kwargs):

        if session.get("unverified_user_id"):
            flash("Please verify your email address", "danger")
            return redirect(url_for('users.verify'))
        
        if not session.get("user_id"):
            flash("Unauthorised, please login", "danger")
            return redirect(url_for("users.login"))
        
        return route(*args, **kwargs)
    return wrapper


def check_user_status(route):
    @functools.wraps(route)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        unverified_user_id = session.get("unverified_user_id")
        endpoint = request.endpoint  # more reliable with Blueprints
        # /register/verify or /register/get_code
        if endpoint in ["users.verify", "users.get_code"]:
            if user_id:
                flash("You are already logged in.", "info")
                return redirect(url_for("main.index"))
            elif not unverified_user_id:
                flash("Unauthorized, please login or register.", "danger")
                return redirect(url_for("users.login"))
            else:
                return route(*args, **kwargs)
        # /login or /register
        elif endpoint in ["users.login", "users.register"]:
            if user_id:
                flash("You are already logged in.", "info")
                return redirect(url_for("main.index"))
            elif unverified_user_id:
                flash("Please verify your email address.", "warning")
                return redirect(url_for("users.verify"))
            else:
                return route(*args, **kwargs)
        # All other routes
        return route(*args, **kwargs)
    return wrapper


def retry_api_request(max_retries=3, delay_seconds=1):
    """
    Decorator to retry failed API requests.
    Args:
        max_retries (int): Number of retry attempts (default: 3).
        delay_seconds (float): Delay between retries in seconds (default: 1).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs), None
                except (requests.HTTPError, requests.Timeout, requests.RequestException) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        sleep(delay_seconds)
            # If all retries failed, raise the last exception or return None
            return None, last_exception  # Or return a custom error response
        return wrapper
    return decorator


