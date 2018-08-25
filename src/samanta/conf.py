"""
General configurations, it contains all the settings that can be imported
within the app and correspond to the fall back for those configurations
"""
import django.conf


class AppSettings(object):
    """
    A holder for app-specific default settings that allows overriding via
    the project's settings.
    """

    def __getattribute__(self, attr):
        if attr == attr.upper():
            try:
                return getattr(django.conf.settings, attr)
            except AttributeError:
                pass
        return super(AppSettings, self).__getattribute__(attr)


class Settings(AppSettings):

    AUTO_ACTIVATE = False
    """If True newly created will have the status active by default"""

    USE_CAPTCHA = True
    """If True, simple captcha will be used with the register forms"""

    DEFAULT_MAIL_LANG = 'en'  # english
    """Default language to send the emails if the user has not selected any"""

    EMAIL_HOST_USER = 'app@app.com'
    """Email to contact the app"""

    APP_NAME = 'Samanta'
    """Name of the application"""

    MAIL_TEMPLATES_FOLDER = 'samanta/emails/'
    """Default folder to hold the email templates"""

    TEAM_NAME = 'Samanta Team'
    """Name of the team signing the emails"""

    TOKEN_SPAN_VALIDITY = 7
    """Amount of days that a token will valid to be used"""

settings = Settings()
