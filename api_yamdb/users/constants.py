CONFIRMATION_CODE_LENGTH: int = 20
EMAIL_FIELD_LENGTH: int = 254
ROLE_FIELD_LENGTH: int = 20

USER_ROLE_NAME: str = 'User'
MODERATOR_ROLE_NAME: str = 'Moderator'
ADMIN_ROLE_NAME: str = 'Admin'
DEFAULT_USER_ROLE = 'user'
USER_ROLE_CHOICES = (
        ('user', USER_ROLE_NAME),
        ('moderator', MODERATOR_ROLE_NAME),
        ('admin', ADMIN_ROLE_NAME),
    )