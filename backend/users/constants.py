from enum import Enum


class FieldsConstants(Enum):
    PERSONAL_DATA_MAX_LENGTH = 150
    EMAIL_MAX_LENGTH = 254
    NAME_MAX_LENGTH = 200
    SLUG_MAX_LENGTH = 200
    MEASUREMENT_UNIT_MAX_LENGTH = 200
    COLOR_MAX_LENGTH = 7


class LimitValueConstants(Enum):
    MIN_COOKING_TIME = 1
    MAX_COOKING_TIME = 32767
    MIN_AMOUNT = 1


class UserConstants(Enum):
    USERNAME_FIELD_VALUE = 'email'
    REQUIRED_FIELDS_VALUE = ['username', 'first_name', 'last_name']


PAGE_SIZE = 6
