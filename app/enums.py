from enum import StrEnum


class UserRole(StrEnum):
    REGULAR = "REGULAR"
    ADMIN = "ADMIN"
    STAFF = "STAFF"