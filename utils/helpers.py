"""
utils/helpers.py – Common utility helper functions.
"""


def allowed_file(filename, allowed):
    """Check if a file extension is in the allowed set."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed
