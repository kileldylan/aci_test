import re
from datetime import datetime, timedelta
from unittest import expectedFailure
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import LoginAttempt


class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='reset-user',
            email='reset@example.com',
            password='OriginalPass123!',
        )
        self.reset_url = reverse('auth_app:password_reset')

    def request_reset_link(self):
        response = self.client.post(self.reset_url, {'email': self.user.email})
        self.assertRedirects(response, reverse('auth_app:password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)

        match = re.search(r'/reset/([^/]+)/([^/\s]+)', mail.outbox[0].body)
        self.assertIsNotNone(match, 'Reset email did not contain a reset URL')
        uidb64, token = match.groups()
        return reverse(
            'auth_app:password_reset_confirm',
            kwargs={'uidb64': uidb64, 'token': token},
        )

    def test_reset_request_sends_email_with_reset_link(self):
        reset_link = self.request_reset_link()

        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertIn(reset_link, mail.outbox[0].body)

    def test_reset_link_expires(self):
        reset_link = self.request_reset_link()

        with patch.object(
            default_token_generator,
            '_now',
            return_value=datetime.now() + timedelta(days=4),
        ):
            response = self.client.get(reset_link)

        self.assertContains(response, 'invalid or has expired')

    def test_reset_link_sets_new_password(self):
        reset_link = self.request_reset_link()
        response = self.client.get(reset_link, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Choose a new password')

        response = self.client.post(
            response.request['PATH_INFO'],
            {
                'new_password1': 'ReplacementPass123!',
                'new_password2': 'ReplacementPass123!',
            },
        )

        self.assertRedirects(
            response,
            reverse('auth_app:password_reset_complete'),
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('ReplacementPass123!'))

    @expectedFailure
    def test_password_change_page_returns_ok_after_submission(self):
        reset_link = self.request_reset_link()
        response = self.client.get(reset_link, follow=True)

        response = self.client.post(
            response.request['PATH_INFO'],
            {
                'new_password1': 'ReplacementPass123!',
                'new_password2': 'ReplacementPass123!',
            },
        )

        self.assertEqual(response.status_code, 200)


@override_settings(
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher']
)
class LoginRateLimitTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='login-user',
            email='login@example.com',
            password='testpass123',
        )
        self.login_url = reverse('auth_app:login')
        self.dashboard_url = reverse('auth_app:dashboard')

    def post_login(self, email, password):
        return self.client.post(
            self.login_url,
            {'username': email, 'password': password},
        )

    def test_valid_email_login_redirects_to_dashboard(self):
        response = self.post_login('login@example.com', 'testpass123')

        self.assertRedirects(response, self.dashboard_url)

    def test_five_case_insensitive_failures_lock_email_with_generic_error(self):
        for attempt in range(5):
            email = (
                'login@example.com'
                if attempt % 2 == 0
                else 'LOGIN@example.com'
            )
            response = self.post_login(email, 'wrong-password')
            self.assertEqual(response.status_code, 200)

        response = self.post_login('LOGIN@example.com', 'testpass123')

        self.assertContains(response, 'Invalid email or password')
        self.assertEqual(
            LoginAttempt.objects.filter(
                email__iexact='login@example.com'
            ).count(),
            5,
        )

    def test_lockout_expires_after_fifteen_minutes(self):
        for _ in range(5):
            self.post_login('login@example.com', 'wrong-password')

        after_lockout = timezone.now() + timedelta(minutes=15, seconds=1)
        with patch('auth_app.views.timezone.now', return_value=after_lockout):
            response = self.post_login('login@example.com', 'testpass123')

        self.assertRedirects(response, self.dashboard_url)
        self.assertTrue(
            LoginAttempt.objects.filter(
                user=self.user,
                success=True,
            ).exists()
        )

    def test_successful_login_resets_failed_attempt_count(self):
        for _ in range(4):
            self.post_login('login@example.com', 'wrong-password')

        self.assertRedirects(
            self.post_login('login@example.com', 'testpass123'),
            self.dashboard_url,
        )

        for _ in range(4):
            self.post_login('login@example.com', 'wrong-password')

        response = self.post_login('login@example.com', 'testpass123')

        self.assertRedirects(response, self.dashboard_url)

    def test_unknown_email_and_wrong_password_use_same_error(self):
        wrong_password = self.post_login('login@example.com', 'wrong-password')
        unknown_email = self.post_login('unknown@example.com', 'wrong-password')

        self.assertContains(wrong_password, 'Invalid email or password')
        self.assertContains(unknown_email, 'Invalid email or password')
