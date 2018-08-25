"""This file condenses all the possible constants included in the file. The
idea is not to hardcode anything
"""

from django.utils.translation import gettext as _
from cgm_tools.constants import LabeledEnum

APP_NAME = 'samantha'


class Genders(LabeledEnum):
    """Enumeration for the possible genders of the users"""
    NOTTELLING = (0, _('Not Telling'))
    FEMENINE = (1, _('Feminine'))
    MASCULINE = (2, _('Masculine'))
    OTHER = (3, _('Other'))


class StatusActivity(LabeledEnum):
    """General on/off status"""
    INACTIVE = (0, _('Inactive'))
    ACTIVE = (1, _('Active'))
