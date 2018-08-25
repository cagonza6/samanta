
from django.utils.translation import gettext as _
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import PasswordChangeForm

from . mixins import ViewMixin, TokenBasedView
from ..forms import SamUserCreationForm, ChangeEmailForm, SamUserEditForm
from ..forms import PasswordRecoveryForm, PasswordRecoveryChangeForm, TokenConfirmationForm
from .helpers import send_register_email, send_changemail_email, send_recover_email
from .. models import UserCreationLog, SamUser, EmailChangeLog, PasswordRecoveryLog


class Register(ViewMixin):
    """Genereal view for the user registration"""

    TEMPLATE = 'samanta/account/register.html'
    TITLE = _('Register')

    def get(self, request):
        """Process the get requests"""

        form = SamUserCreationForm()
        self.beautify_form(form, ignore_fields=('terms_of_service',))

        context = {'form': form}
        return self.render(request, context)

    def post(self, request):
        """Process the post requests"""

        form = SamUserCreationForm(request.POST)
        self.beautify_form(form, ignore_fields=('terms_of_service',))

        context = {'form': form}

        if not form.is_valid():
            messages.warning(request, _('Please check the provided data.'))

            return self.render(request, context)

        user = form.save()
        send_register_email(request, user)
        messages.success(request, _('Your Account has being created. We will '
                                    'send you an e-mail with the instructions '
                                    'to activate it.'))

        return redirect('login')


class AccountConfirm(TokenBasedView):

    TEMPLATE = 'samanta/account/activate.html'
    TITLE = 'Activate account'

    def get(self, request, uidb64='', token=''):

        if request.user.is_authenticated:
            messages.warning(request, _("You are already authenticated"))
            return redirect('home')

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = SamUser.objects.get(id=uid)
        except:
            messages.warning(request, _("We could not find the account you "
                                        "are trying to activate."))
            return redirect('home')

        result = self.process_token(request, user, token, UserCreationLog)

        if not result:
            redirect('home')

        user.is_active = True
        user.activated_at = timezone.now()
        user.save()
        messages.success(request, _('Congratulations your account has is now '
                                    'active and you can  log in.'))

        return redirect('login')


@method_decorator(login_required, name='dispatch')
class UserProfile(ViewMixin):

    TEMPLATE = 'samanta/account/profile.html'
    TITLE = "User profile"

    def get(self, request):
        return self.render(request)


@method_decorator(login_required, name='dispatch')
class EmailChange(ViewMixin):
    TEMPLATE = 'samanta/account/email_change.html'
    TITLE = 'Email change'

    def get(self, request):
        form = ChangeEmailForm(request.user)
        self.beautify_form(form)

        return self.render(request, {'form': form})

    def post(self, request):

        user = request.user
        form = ChangeEmailForm(user, request.POST)
        self.beautify_form(form)

        if not form.is_valid():
            messages.warning(request, 'Please correct the information below.')
            return self.render(request, {'form': form})

        send_changemail_email(request, user, form.clean_mail)
        messages.success(request, _('We sent an email wit a confirmation '
                                    'link to the new email with instructions '
                                    'to make the change.'))

        return self.render(request, {'form': form})


class EmailChangeConfirm(TokenBasedView):

    def get(self, request, uidb64, token):

        if not request.user.is_authenticated:
            messages.warning(request, "You need to be logged in to use the "
                                      "change email feature")
            return redirect('home')

        if not uidb64 or not token:
            messages.warning(request, "Invalid link")
            return redirect('home')

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = SamUser.objects.get(id=uid)
        except:
            messages.warning(request, "Invalid link")
            return redirect('home')

        Token = self.process_token(request, user, token, EmailChangeLog)

        if not Token:
            return redirect('home')

        user.email = Token.email
        user.save()
        Token.save()

        messages.success(request, "Your email has been successfully changed.")

        return redirect('home')


@method_decorator(login_required, name='dispatch')
class PasswordChange(ViewMixin):
    TEMPLATE = 'samanta/account/password_change.html'
    TITLE = 'Password change'
    PASSWORD_CHANGE_FORM = PasswordChangeForm

    def get(self, request):
        form = self.PASSWORD_CHANGE_FORM(request.user)
        self.beautify_form(form)

        return self.render(request, {'form': form})

    def post(self, request):

        form = self.PASSWORD_CHANGE_FORM(request.user, request.POST)
        self.beautify_form(form)

        if form.is_valid():
            form.save()
            messages.success(request, 'Your password was successfully '
                                      'updated! you can not log in.')
            return redirect('user_profile')
        else:
            messages.error(request, 'Please correct the error below.')

        return self.render(request, {'form': form})


@method_decorator(login_required, name='dispatch')
class ProfileEdit(ViewMixin):

    TEMPLATE = 'samanta/account/user_edit.html'
    TITLE = "Edit profile"
    USER_EDIT_FORM = SamUserEditForm

    def get(self, request):
        form = self.USER_EDIT_FORM(instance=request.user)
        self.beautify_form(form)

        return self.render(request, {'form': form})

    def post(self, request):

        form = self.USER_EDIT_FORM(request.POST, instance=request.user)
        self.beautify_form(form)

        if form.is_valid():
            form.save()
            return redirect('user_profile')

        return self.render(request, {'form': form})


class PasswordRecoveryStart(ViewMixin):
    TEMPLATE = 'samanta/account/password_recover.html'
    TITLE = "Password recovery"
    PASWORD_RECOVERY_FORM = PasswordRecoveryForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')

        form = self.PASWORD_RECOVERY_FORM()
        self.beautify_form(form)

        context = {'form': form}
        return self.render(request, context)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('home')

        form = self.PASWORD_RECOVERY_FORM(request.POST)

        context = {
            'form': form
        }

        if not form.is_valid():
            return self.render(request, context)

        email = form.cleaned_data['email']
        user = SamUser.objects.filter(email=email).first()

        # just if the user was found actually send the email
        if user:
            send_recover_email(request, user)
        # the message is always shown in otder to not say if the account
        # exists or not
        messages.success(request, "An email was sent to your account in "
                                  "order to recorver it. Please follow the "
                                  "instructions in that email.")
        return redirect('home')


class PasswordRecoveryChange(TokenBasedView):
    TEMPLATE = 'samanta/account/password_set_new.html'
    TITLE = "Password recovery"
    PASSWORD_RECOVERY_FORM = PasswordRecoveryChangeForm

    def get(self, request, uidb64, token):

        if request.user.is_authenticated:
            messages.warning(request, "You are already authenticated")
            return redirect('home')

        if not uidb64 or not token:
            messages.warning(request, "Invalid link")
            return redirect('home')

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = SamUser.objects.get(id=uid)
        except:
            messages.warning(request, "Invalid link")
            return redirect('home')

        is_valid = self.process_token(request, user, token, PasswordRecoveryLog)

        if not is_valid:
            return redirect('home')

        form = self.PASSWORD_RECOVERY_FORM(user, initial={'hashid': uidb64,
                                                          'token': token
                                                          })
        self.beautify_form(form)

        context = {'form': form,
                   'hashid': uidb64,
                   'token': token
                   }

        return self.render(request, context)

    def post(self, request):

        if request.user.is_authenticated:
            messages.warning(request, "You are already authenticated")
            return redirect('home')

        form_token = TokenConfirmationForm(request.POST)
        if not form_token.is_valid():
            messages.warning(request, "The link seems to be invalid.")

        token = form_token.token_
        hashid = form_token.hashid_

        # if the link is valid, get the user with the given id
        try:
            uid = force_text(urlsafe_base64_decode(hashid))
            user = SamUser.objects.get(id=uid)
        except:
            messages.warning(request, "Invalid link")
            return redirect('home')

        # open the token related to that user
        Token = self.process_token(request, user, token, PasswordRecoveryLog)

        if not Token:
            messages.warning(request, "Password problems")

        # form to change the password. This form provides extra fields for
        # the token and the id. It is an extension of
        # django.contrib.auth.forms.SetPasswordForm
        form = PasswordRecoveryChangeForm(user, request.POST)

        if not form.is_valid():
            messages.warning(request, "There are error in the provided data."
                                      "Please chech it.")
            return self.render(request, {'form': form})

        # if everithing ok, deactivate the token and update the user
        form.save()
        Token.save()

        messages.success(request, "Your password has been changed. Please "
                                  "try to login..")
        return redirect('login')

