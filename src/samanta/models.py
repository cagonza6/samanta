
import hashlib
from datetime import timedelta

from django.utils import six
from django.db import models
from django.utils.translation import gettext as _
from django.utils import timezone
from django.contrib.auth.models import (AbstractUser, UserManager, Permission,
                                        ASCIIUsernameValidator,
                                        UnicodeUsernameValidator)
from django_countries.fields import CountryField

from samanta.core.hasher import Hasher
from . conf import settings
from . import constants


class Teams(models.Model):
    """Equivalent to the groups. It allows to have a secondary and independent
    group like relations. This structure does not have particular permission as
    the groups do. It works just as an extra label.
    """
    name = models.CharField(_('name'), max_length=80, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        blank=True,
    )

    class Meta:
        verbose_name = _('team')
        verbose_name_plural = _('teams')
        app_label = 'samanta'

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name, )


class SamUserManager(UserManager):
    """Special manager for the user model. It provides the connection to the
    configurations and pre made queries.
    """
    use_in_migrations = True

    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        Overrides the super method in order to deactivate the


        :param username: str: name of the user
        :param email: str: email of the user
        :param password: str: password for the new user
        :param extra_fields: dict: extra fields to be passed to the forms
        :return:
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', settings.AUTO_ACTIVATE)
        return self._create_user(username, email, password, **extra_fields)

    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class SamUser(AbstractUser):

    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    # redefinition for a shorter username
    username = models.CharField(
        _('username'), max_length=32, unique=True,
        help_text=_(
            'Required. 32 characters or fewer. Letters, digits and @/./+/-/_ '
            'only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    # Redefine to be unique
    email = models.EmailField(unique=True, verbose_name='email address')

    # Personal data
    date_of_birth = models.DateField(null=True, blank=True)
    location = CountryField(blank_label=_('Select'), blank=True)
    language = models.CharField(max_length=3, blank=True)
    gender = models.SmallIntegerField(choices=constants.Genders.tuples(),
                                      default=constants.Genders.NOTTELLING.id)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # Creation and updates
    activated_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    # Statuses
    is_active = models.BooleanField(default=False)
    # used to ban users
    unban_time = models.DateField(null=True, blank=True)

    # similar to groups
    teams = models.ManyToManyField(Teams, blank=True)

    USERNAME_FIELD = 'username'

    objects = SamUserManager()

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
        app_label = 'samanta'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        If non is set, return the username
        """
        if self.first_name or self.first_name:
            full_name = '%s %s' % (self.first_name, self.last_name)
            return full_name.strip()
        return self.username

    def gravatar(self, size=100):
        """ Calls the gravatar md5 hash of the users email. This is intended to
        be used in a img tag: ...<img src="{{user.gravatar}}">...

        :param size: size in px of the image to show
        :return: str: url to ask for the gravatar equivalent of the user

        """

        md5 = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        str_ = 'http://www.gravatar.com/avatar/{md5}?s={size}&d=identicon'

        return str_.format(md5=md5, size=size)

    def ban_to(self, until):
        """ Sets the ban over the user until the given date
        :param until: date: date to release the user
        :return: None
        """
        self.unban_time = until
        self.save(update_fields=['unban_time'])

    @property
    def is_banned(self):
        """Checks if the user is banned or not

        :return: Bool: True if the user is banned, False if not
        """
        # if ban date and in the future
        if self.unban_time:
            if self.unban_time > timezone.now().date():
                return True
            else:
                self.unban()
        return False

    def unban(self):
        """Removes the ban over the user

        :return: None
        """
        self.unban_time = None
        self.save(update_fields=['unban_time'])


# ============================== Tokens =======================================
class TokenModelManeger(models.Manager):
    """General Manager for the Token based models"""

    def close_old(self):
        """Closes all the tokens that are active and should not.
        The return value depends on the used DB engine.

        :return: int: amount of closed tokens.
        """
        threshold = timezone.now() - timedelta(
            days=settings.TOKEN_SPAN_VALIDITY)
        old = self.filter(date_lt=threshold,
                          status=constants.StatusActivity.ACTIVE.id)
        return old.update(status=constants.StatusActivity.INACTIVE.id)


class TokenBasedActivation(models.Model):
    """
    Base model to be extended in order to generate Activation token pages.
    """

    user = models.ForeignKey(SamUser, on_delete=models.CASCADE, null=False)
    """Token owner"""
    email = models.EmailField(null=False)
    """Email the Token was sent to"""
    token = models.CharField(max_length=64, null=False)
    salt = models.CharField(max_length=32, null=False)
    """Salt used to encrypt the sent digest"""
    date = models.DateTimeField(auto_now_add=True, null=False)
    """Creation date"""
    status = models.SmallIntegerField(null=False,
                                      choices=constants.StatusActivity.tuples(),
                                      default=constants.StatusActivity.ACTIVE.id)
    """Current status"""

    objects = TokenModelManeger()

    class Meta:
        abstract = True
        app_label = 'samanta'

    def is_old(self, autoclose=False):
        """Check if the token is older than the given validity
        :param: bool: If the token is too old, it will close it automatically
        :return: Bool: True if the token is valid, False if not.
        """
        if (timezone.now() - self.date).days < settings.TOKEN_SPAN_VALIDITY:
            return True
        if autoclose:
            self.close()
        return False

    def is_valid(self, token):
        """Checks the validity of the given token considering the stored data
        and what is sent to the user
        """

        hasher = Hasher()
        return hasher.check(self.token, self.salt, token)

    def close(self):
        """Closes the given token setting it inactive"""
        self.status = constants.StatusActivity.INACTIVE.id
        self.save(update_fields=['status'])


class UserCreationLog(TokenBasedActivation):
    """Used to validate the generation of new user and log of their creation"""
    pass


class PasswordRecoveryLog(TokenBasedActivation):
    """Used to validate the password recovery of the users """
    pass


class EmailChangeLog(TokenBasedActivation):
    """Used to validate the email change of the users"""
    pass
