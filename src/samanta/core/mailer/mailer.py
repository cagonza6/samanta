#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from ...conf import settings


class SamantaMailer:
    """
    This class is meant to send predefined emails following
    predetermined templates as normal plain text emails. It provides the
    methods to send:
      * activation email
      * recovery email
      * and email change email

    """

    TEAM_NAME = settings.TEAM_NAME
    TEMPLATES_FOLDER = settings.MAIL_TEMPLATES_FOLDER

    def __init__(self, site_name, domain):
        self.site_name = site_name
        self.site_domain = domain

    def build_context(self, context):
        full = {
            'help_mail': settings.EMAIL_HOST_USER,
            'team_name': self.TEAM_NAME,
            'site_name': self.site_name,
            'domain': self.site_domain
        }
        full.update(context)
        return full

    def _send_mail(self, subject, from_email, to_, message_txt, message_html):

        if not message_html and not message_txt:
            raise ValueError("At least one of both contents must be given: "
                             "Plain text ot Html")

        # make it is always iterable
        if type(to_) not in (list, tuple):
            to_ = [to_]

        msg = EmailMultiAlternatives(subject, message_txt, from_email, to_)

        if message_html:
            msg.attach_alternative(message_html, "text/html")

        try:
            msg.send()
            return True
        except Exception as e:
            print(e)
        return False

    def send_templated_mail(self, subject, from_email, to_, context_, lang,
                            template_txt_file=None, template_html_file=None):

        contex = self.build_context(context_)
        if not template_html_file and not template_txt_file:
            raise ValueError("At least one of both templates must be given: "
                             "Plain text ot Html")

        template_txt_file = os.path.join(self.TEMPLATES_FOLDER, lang, template_txt_file)
        text_content = render_to_string(template_txt_file, context=contex)

        if template_html_file:
            template_html = os.path.join(self.TEMPLATES_FOLDER, lang, template_html_file)
            html_content = render_to_string(template_html, context=contex)
        else:
            html_content = False

        return self._send_mail(subject, from_email, to_, text_content,
                               html_content)


class EmailSender(SamantaMailer):

    def activation_email(self, to_, context, lang=settings.DEFAULT_MAIL_LANG):

        subject = 'Account activation'
        from_email = settings.EMAIL_HOST_USER
        template_txt = 'account_new.txt'
        template_html = 'account_new.html'

        return self.send_templated_mail(subject, from_email, to_, context,
                                        lang, template_txt, template_html)

    def recovery_email(self, to_, context, lang=settings.DEFAULT_MAIL_LANG):

        subject = 'Password recovery'
        from_email = settings.EMAIL_HOST_USER
        template_txt = 'password_reset.txt'
        template_html = 'password_reset.html'

        return self.send_templated_mail(subject, from_email, to_, context, lang,
                                        template_txt, template_html)

    def change_email_email(self, to_, context, lang=settings.DEFAULT_MAIL_LANG):

        subject = 'Password recovery'
        from_email = settings.EMAIL_HOST_USER
        template_txt = 'email_change.txt'
        template_html = 'email_change.html'

        return self.send_templated_mail(subject, from_email, to_, context,
                                        lang, template_txt, template_html)
