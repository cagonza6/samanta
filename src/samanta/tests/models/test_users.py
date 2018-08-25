from django.test import TestCase, override_settings
from django.db.utils import IntegrityError
from django.utils import timezone
from datetime import timedelta
from samanta import models
from samanta.conf import settings
User = models.SamUser


class Mixin(TestCase):

    def setUp(cls):
        cls.su = User.objects.get(id=1)
        cls.staff = User.objects.get(id=2)
        cls.user = User.objects.get(id=3)


class TestUserModel(Mixin):

    fixtures = ['users.json']

    def test_creation(self):
        # creator classes
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username="user", email="u@u.com", password='pswd',
                 is_staff=True)

    @override_settings(TOKEN_SPAN_VALIDITY=1)
    def test_ban(self):
        """
        Make sure that the ban  and un_ban function actually bans and unbans
        the user

        :return: None
        """

        future_ = timezone.now().date() + timedelta(
            days=(settings.TOKEN_SPAN_VALIDITY + 1))

        past_ = timezone.now().date() + timedelta(
            days=(settings.TOKEN_SPAN_VALIDITY - 1))

        user = self.su
        # in future
        user.ban_to(future_)
        user.refresh_from_db()
        self.assertTrue(user.is_banned)
        self.assertEqual(future_, user.unban_time)
        # remove ban
        user.unban()
        self.assertFalse(user.is_banned)
        # ban in the past
        user.ban_to(past_)
        user.refresh_from_db()
        self.assertFalse(user.is_banned)

    def test_full_name(self):
        name = self.su.get_full_name()
        self.assertEqual(name, 'super user')

    def test_manager_natural_key(self):
        """
        Ensure the user being case insensitive

        :return: None
        """
        u1 = User.objects.get_by_natural_key(self.staff.username.title())
        u2 = User.objects.get_by_natural_key(self.staff.username.lower())
        self.assertEqual(u1, u2)
        self.assertTrue(isinstance(u1, User))
