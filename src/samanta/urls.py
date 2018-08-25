"""maite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.utils.translation import gettext as _
from django.conf.urls import url, include
from django.contrib.auth.views import logout, login
from .forms import SamAuthenticationForm
from .views import account

urlpatterns = [

    url(r'^login/$', login,
        {'template_name': 'samanta/account/login.html',
         'authentication_form': SamAuthenticationForm,
         'redirect_field_name': 'redirect_to',
         'redirect_authenticated_user': True,
         'extra_context': {'title': _('Login')}
         },
        name='login'),
    url(r'^logout/$', logout,  {'next_page': '/'}, name='logout'),

    # Account creation
    url(r'^register/$', account.Register.as_view(), name='register'),
    url(r'^account/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]+)/$',
        account.AccountConfirm.as_view(), name='account_confirm'),
    url(r'^account/profile/', account.UserProfile.as_view(),
        name='user_profile'),

    # Account modifications
    url(r'^account/edit/', account.ProfileEdit.as_view(), name='profile_edit'),
    url(r'^email/change/$', account.EmailChange.as_view(), name='email_change'),
    url(r'^email/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>['
        r'0-9A-Za-z]+)/$', account.EmailChangeConfirm.as_view(),
        name='email_confirm'),
    url(r'^password_change/', account.PasswordChange.as_view(), name='password_change'),

    # Password
    url(r'^password/recover/$', account.PasswordRecoveryStart.as_view(),
        name='pwd_recover'),
    url(r'^password/recover/set/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]+)/$',
        account.PasswordRecoveryChange.as_view(),
        name='pwd_recover_change'),

    # 3rd party
    url(r'^captcha/', include('captcha.urls')),
]
