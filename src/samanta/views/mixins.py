#!/usr/bin/env python
# -*- coding: utf-8 -*-


from django.views import View
from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _

from ..core.hasher import Hasher
from ..conf import settings


class ViewMixin(View):
    TEMPLATE = 'samanta/missing_template.html'
    TITLE = "No Title"

    def render(self, request, context=None):
        if context is None:
            context = {}
        context_ = {
            'title': self.TITLE
        }
        context_.update(context)
        return render(request, self.TEMPLATE, context_)


class TokenBasedView(ViewMixin):

    def process_token(self, request, user, token, token_manager, commit=True):

        Token = token_manager.objects.filter(user=user, status=1).last()

        if not Token:
            messages.warning(request, _('Invalid link.'))
            return None

        delta = (timezone.now() - Token.date).days < settings.TOKEN_SPAN_VALIDITY

        if not delta:
            messages.warning(request, _('Token too old. Please request a '
                                        'nre one.'))
            return None

        hasher = Hasher()
        is_valid = hasher.check(Token.token, Token.salt, token)

        if not is_valid:
            messages.warning(request, _('Invalid link.'))
            return None

        # Deactivate token
        Token.status = 0
        if commit:
            Token.save()

        return Token
