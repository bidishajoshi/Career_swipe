"""
app/extensions.py – Shared Flask extension instances.
Import from here everywhere to avoid circular imports.
"""

from extensions import db, migrate, mail
