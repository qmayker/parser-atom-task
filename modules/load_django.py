"""
Django initialization module.
Sets up Django environment for modules that need database access.
Must be imported before using Django models.
"""

import os
import sys

from django import setup

sys.path.append(r"E:\projects\parser_project\parser_project")
os.environ["DJANGO_SETTINGS_MODULE"] = "parser_project.settings"

setup()
