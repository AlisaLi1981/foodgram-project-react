from enum import Enum


class UserConstants(Enum):
    USERNAME_FIELD_VALUE = 'email'
    REQUIRED_FIELDS_VALUE = ['username', 'first_name', 'last_name']
    PERSONAL_DATA_MAX_LENGTH = 150
    EMAIL_MAX_LENGTH = 254
