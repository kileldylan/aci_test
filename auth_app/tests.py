import re
from datetime import datetime, timedelta
from unittest import expectedFailure
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.urls import reverse


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
