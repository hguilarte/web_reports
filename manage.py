#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""

    # ✅ Set default settings module for Django project
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webreports.settings')

    try:
        # ✅ Import Django's command execution function
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure it is installed and "
            "available in your PYTHONPATH environment variable. Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # ✅ Execute the command-line utility
    execute_from_command_line(sys.argv)


# ✅ Ensure this script runs only when executed directly
if __name__ == '__main__':
    main()
