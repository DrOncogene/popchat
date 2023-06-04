#!/usr/bin/env python3
"""utility functions for auth"""
import re


def validate_email(email: str) -> bool:
    """validate email"""
    email_regex = re.compile(r"""^[a-z0-9!#$%&'*+/=?^_`{|}~-]+
                            (?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@
                            (?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+\.
                            [a-z0-9](?:[a-z0-9-]*[a-z0-9])?$""", re.X)
    if email_regex.fullmatch(email) is not None:
        return True

    return False


def validate_username(username: str) -> bool:
    """validate username"""
    username_regex = re.compile(r"^[A-Za-z][A-Za-z0-9]{4,10}$")
    if username_regex.fullmatch(username) is not None:
        return True

    return False


def validate_password(password: str) -> bool:
    """validate password"""
    passwd_regex = re.compile(r"""^(?=.*[A-Za-z])
                                   (?=.*\d)
                                   [A-Za-z\d\.+-=#_%|&@]{7,16}$""", re.X)
    if passwd_regex.fullmatch(password) is not None:
        return True

    return False


def send_email(email: str, subject: str, message: str) -> None:
    """send email"""
    pass
