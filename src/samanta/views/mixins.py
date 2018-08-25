#!/usr/bin/env python
# -*- coding: utf-8 -*-


from django.views import View
from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _

from samanta.conf import settings


class ViewMixin(View):
    TEMPLATE = 'samanta/missing_template.html'
    TITLE = "No Title"

    def beautify_form(self, form, _fields=(), ignore_fields=()):
        """
        Formats the given form to use the class 'form-control' in all
        fields with the exception of the ignored ones.
        """

        fields = form.fields if not _fields else _fields
        use_fields = [f for f in fields if f not in ignore_fields]

        for field in use_fields:
            print(field)
            form.fields[field].widget.attrs['class'] = 'form-control'

    def render(self, request, context=None):
        """

        :param request: HttpRequest: request to be rendered
        :param context: dict: dictionary passing all the required context

        :return: HttpResponse

        """
        if context is None:
            context = {}
        context_ = {
            'title': self.TITLE
        }
        context_.update(context)
        return render(request, self.TEMPLATE, context_)


class TokenBasedView(ViewMixin):
    """General definition for processing token views. It care about the main
    process of validating and closing tokens
    """

    def process_token(self, request, user, token, token_manager):

        Token = token_manager.objects.filter(user=user, status=1).last()

        if not Token:
            messages.warning(request, _('Invalid link.'))
            return None

        elif not Token.is_old():
            messages.warning(request,
                             _('Token too old. Please request a new one.'))
            return None

        elif not Token.is_valid(token):
            messages.warning(request, _('Invalid link.'))
            return None

        # Deactivate token
        Token.close()
        return Token
