#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of the forms used by Maite. All these forms require the use of
the Maite user model: SamUser. Therefore, the method get_user_model() is not used.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext as _

from captcha.fields import CaptchaField

from .models import SamUser
from . conf import settings


class SamAuthenticationForm(AuthenticationForm):
    """Extension of the Django AuthenticationForm in order to consider the
     'is_active' attribute of the user"""

    error_messages = AuthenticationForm.error_messages.copy()
    error_messages['banned'] = 'Your account is banned until {until}'

    def confirm_login_allowed(self, user):
        """
        extends the confirm_login_allowed from django AuthenticationForm in
        order to provide further filters.
        Since the default for django is checking active, this form can allow to
        use any custom filter, such as ban times.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        :param user: SamUser: user to check to
        :return: None, it just raises excepions
        """
        # use default validations
        super(SamAuthenticationForm, self).confirm_login_allowed(user)
        if user.is_banned:
            raise forms.ValidationError(
                self.error_messages['banned'],
                code='banned',
                params={'until': user.unban_time}
            )


class SamUserCreationForm(UserCreationForm):
    """Custom creation form used to extend the functionalities of
    UserCreationForm by creating new fields and checks
    """

    error_messages = UserCreationForm.error_messages.copy()
    error_messages.update({
        'email_in_used': _('This email is already in use.'),
        'email_mismatch': _("The two email fields didn't match."),
        'email_in_use': _("The two email fields didn't match."),
        'username_in_use': _("This username is already taken."),
    })

    # is use captcha is required, add the field to the form
    if settings.USE_CAPTCHA:
        captcha = CaptchaField()

    # used for confirmation
    email2 = forms.EmailField(label=_("Confirm your Email"), max_length=254)

    # general tos check
    terms_of_service = forms.BooleanField(
        help_text=_("I read and accept the terms and conditions."),
        widget=forms.CheckboxInput(
            attrs={'class': 'radio-inline', 'id': 'terms_of_Service'})
    )

    def __init__(self, *args, **kwargs):
        super(SamUserCreationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = SamUser
        fields = ['username', 'email', 'email2', 'password1', 'password2',
                  'terms_of_service']
        if settings.USE_CAPTCHA:
            fields += ['captcha']

    def clean_email2(self):
        """Makes sure that the second mail matches the first one, in order to
        avoid user that made mistakes at login
        """
        email1 = self.cleaned_data.get("email")  # original
        email2 = self.cleaned_data.get("email2")  # confirmation

        # confirm email
        if email1 and email2 and email1 != email2:
            raise forms.ValidationError(
                self.error_messages['email_mismatch'],
                code='email_mismatch',
            )

        # unique email
        email1 = self.cleaned_data.get("email")
        if email1 and SamUser.objects.filter(email__iexact=email1).exists():
            raise forms.ValidationError(
                self.error_messages['email_in_used'],
                code='email_in_used',
            )

        return email2

    def clean_username(self):
        """Used to clean the username and ensure case sensitivity and
        uniqueness.
        """

        # ensure case insensitive
        username = self.cleaned_data.get('username')
        if username and SamUser.objects.filter(
                username__iexact=username).exists():
            raise forms.ValidationError(
                self.error_messages['username_in_use'],
                code='username_in_use',
            )

        return username


class ChangeEmailForm(forms.Form):
    """
    Used to allow the users to change their email. It requires password
    confirmation
    """
    error_messages = {
        'password_incorrect': _("The password you entered is incorrect. "
                                "Please try again."),
        'email_mismatch': _("The two email fields didn't match."),
        'same_email': _("The new email must not be your current email."),
        'email_in_use': _("This email is already in use. Please provide a "
                          "new one."),
    }

    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': ''}),
    )

    email_new = forms.EmailField(label=_("Email"), max_length=254,
                                 required=True)

    email_new2 = forms.EmailField(label=_("Email confirmation"),
                                  max_length=254, required=True)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangeEmailForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        """
        Validates that the given password is correct.
        """
        password = self.cleaned_data["password"]
        if not self.user.check_password(password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return password

    def clean_email_new2(self):
        """ Ensures the given email matches the confirmation

        :return: str: cleaned email confirmation

        """
        email_new = self.cleaned_data.get('email_new').lower()
        email_new2 = self.cleaned_data.get('email_new2').lower()

        # both present and the same
        if email_new and email_new2 and email_new != email_new2:
                raise forms.ValidationError(
                    self.error_messages['email_mismatch'],
                    code='email_mismatch',
                )
        # not repeated
        if email_new == self.user.email.lower():
            raise forms.ValidationError(
                self.error_messages['same_email'],
                code='same_email',
            )
        # uniqueness
        if SamUser.objects.filter(email__iexact=email_new).exclude(
                id=self.user.id).count() > 0:
            raise forms.ValidationError(
                self.error_messages['email_in_use'],
                code='email_in_use',
            )
        return email_new2

    @property
    def clean_mail(self):
        """Use to access the clean email from the outside tiwhout acessing the
        cleaned data

        :return: str or None: cleande email ot None if something fialed
        """
        return self.cleaned_data.get('email_new', None)


class SamUserEditForm(forms.ModelForm):
    """Form used to edit the users profile information"""

    def __init__(self, *args, **kwargs):
        super(SamUserEditForm, self).__init__(*args, **kwargs)

    class Meta:
        model = SamUser
        fields = ['date_of_birth', 'location', 'language', 'gender', 'avatar']


class PasswordRecoveryForm(forms.Form):
    """Single form used in the frontend for the recovery of the users password"""
    email = forms.EmailField(label=_("Email"), max_length=254)


class TokenConfirmationForm(forms.Form):
    """Base form for the confirmation of a token. It provides the base methods
    to validate the inputs.
    """

    error_messages = {
        'empty_token': _("empty_token."),
        'empty_hash': _("empty_hash."),
    }

    hashid = forms.CharField(widget=forms.HiddenInput(), required=True)
    token = forms.CharField(widget=forms.HiddenInput(), required=True)

    def __init__(self, *args, **kwargs):
        super(TokenConfirmationForm, self).__init__(*args, **kwargs)
        self.token_ = None
        self.hashid_ = None

    def clean_token(self):
        token = self.cleaned_data.get('token')

        if not token:
            raise forms.ValidationError(
                self.error_messages['empty_token'],
                code='empty_token',
            )
        self.token_ = token
        return token

    def clean_hashid(self):
        hashid = self.cleaned_data.get('hashid')

        if not hashid:
            raise forms.ValidationError(
                self.error_messages['empty_hash'],
                code='empty_hash',
            )
        self.hashid_ = hashid
        return hashid


class PasswordRecoveryChangeForm(SetPasswordForm):

    hashid = forms.CharField(widget=forms.HiddenInput(), required=True)
    token = forms.CharField(widget=forms.HiddenInput(), required=True)

    def clean_token(self):
        token = self.cleaned_data.get('token')
        return token

    def clean_hashid(self):
        token = self.cleaned_data.get('hashid')
        return token

