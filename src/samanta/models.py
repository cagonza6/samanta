
import hashlib
from django.utils import six
from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import (AbstractUser, UserManager, Permission,
                                        ASCIIUsernameValidator,
                                        UnicodeUsernameValidator)
from django_countries.fields import CountryField

from . conf import settings

GENDERS = (
    (0, _('Not Telling')),
    (1, _('Feminine')),
    (2, _('Masculine')),
)


class Teams(models.Model):
    name = models.CharField(_('name'), max_length=80, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        blank=True,
    )

    class Meta:
        verbose_name = _('team')
        verbose_name_plural = _('teams')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


class SamUserManager(UserManager):
    use_in_migrations = True

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', settings.AUTO_ACTIVATE)
        return self._create_user(username, email, password, **extra_fields)

    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


class SamUser(AbstractUser):

    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()
    # redefinition of shorter username
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
    # Redefine to have unique emails
    email = models.EmailField(unique=True, verbose_name='email address')

    # personal data
    date_of_birth = models.DateField(null=True, blank=True)
    location = CountryField(blank_label=_('Select'), blank=True)
    language = models.CharField(max_length=3, blank=True)
    gender = models.SmallIntegerField(choices=GENDERS, default=0)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # creation and updates
    activated_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    # users are inactive by default
    is_active = models.BooleanField(default=False)

    teams = models.ManyToManyField(Teams, blank=True)

    USERNAME_FIELD = 'username'

    objects = SamUserManager()

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
#        app_label = 'samanta'
#        db_table = 'sam_users'
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
        """ Calls the gravatar md5 hash of the users email

        :param size: size in px of the image to show
        :return: str: url to ask for the gravatar equivalent of the user

        """

        md5 = hashlib.md5(self.email.encode('utf-8')).hexdigest()

        str_ = 'http://www.gravatar.com/avatar/' + md5
        str_ += '?s=' + str(size) + '&d=identicon'

        return str_


# ============================== Tokens =======================================
class TokenBasedActivation(models.Model):
    user = models.ForeignKey(SamUser, on_delete=models.CASCADE, null=False)
    email = models.EmailField(null=False)
    token = models.CharField(max_length=64, null=False)
    salt = models.CharField(max_length=32, null=False)
    date = models.DateTimeField(auto_now_add=True, null=False)
    status = models.SmallIntegerField(null=False, default=1)

    class Meta:
        abstract = True


class UserCreationLog(TokenBasedActivation):
    pass


class PasswordRecoveryLog(TokenBasedActivation):
    pass


class EmailChangeLog(TokenBasedActivation):
    pass
