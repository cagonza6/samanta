from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site

from samanta.core.mailer.mailer import EmailSender
from samanta.core.hasher import Hasher
from samanta.models import UserCreationLog, EmailChangeLog, PasswordRecoveryLog


class TokenMailBuilder:
    hasher = Hasher()

    def __init__(self, log_model):
        self.log_model = log_model

    def create_log(self, user, digest, salt):
        # deactivates any previous token. Just in case
        self.log_model.objects.filter(user=user).update(status=0)
        log = self.log_model(user=user, email=user.email, token=digest,
                             salt=salt)
        return log


def _build_log(user, log_model):
    builder = TokenMailBuilder(log_model)
    token, digest, salt = builder.hasher.secure_set()
    log = builder.create_log(user, digest, salt)

    return log, token


def _site_information(request):
    current_site = get_current_site(request)
    name = current_site.name
    domain = current_site.domain

    return name, domain


def _build_context(user, token, use_https):
    context = {
        'uidb64': urlsafe_base64_encode(force_bytes(user.id)),
        'user': user,
        'token': token,
        'protocol': 'https' if use_https else 'http',
    }
    return context


def send_register_email(request, user, use_https=False):

    site_name, site_domain = _site_information(request)
    log, token = _build_log(user, UserCreationLog)

    context = _build_context(user, token, use_https)

    Mailer = EmailSender(site_name, site_domain)
    result = Mailer.activation_email(user.email, context)
    if result:
        log.save()
    return result


def send_changemail_email(request, user, newemail, use_https=False):

    site_name, site_domain = _site_information(request)
    log, token = _build_log(user, EmailChangeLog)
    log.email = newemail

    context = _build_context(user, token, use_https)

    Mailer = EmailSender(site_name, site_domain)
    result = Mailer.change_email_email(newemail, context)
    if result:
        log.save()
    return result


def send_recover_email(request, user, use_https=False):

    site_name, site_domain = _site_information(request)
    log, token = _build_log(user, PasswordRecoveryLog)

    context = _build_context(user, token, use_https)

    Mailer = EmailSender(site_name, site_domain)
    result = Mailer.recovery_email(user.email, context)
    if result:
        log.save()
    return result
