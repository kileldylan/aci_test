this is ACI test project

## Password reset email

Password reset links are valid for Django's default three-day timeout. Configure
the SMTP server used to deliver reset emails with these environment variables:

- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS` or `EMAIL_USE_SSL`
- `DEFAULT_FROM_EMAIL`

For example, set them in the deployment environment or in a local `.env` file.
The automated tests use Django's in-memory email backend.
Added password reset functionlity

Run the password-reset tests with python manage.py test auth_app.tests. 
This is a test READ.me to be used by Onspec repo, still testing
