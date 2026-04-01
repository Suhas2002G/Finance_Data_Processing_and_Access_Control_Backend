from enum import Enum
from typing import List


class Role(str, Enum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"


class Permission(str, Enum):
    READ_TRANSACTIONS = "read_transactions"
    CREATE_TRANSACTION = "create_transaction"
    UPDATE_TRANSACTION = "update_transaction"
    DELETE_TRANSACTION = "delete_transaction"
    READ_DASHBOARD = "read_dashboard"
    MANAGE_USERS = "manage_users"


# Role → Permission Mapping
ROLE_PERMISSIONS = {
    Role.VIEWER: [
        Permission.READ_TRANSACTIONS,
        Permission.READ_DASHBOARD,
    ],
    Role.ANALYST: [
        Permission.READ_TRANSACTIONS,
        Permission.READ_DASHBOARD,
    ],
    Role.ADMIN: [
        Permission.READ_TRANSACTIONS,
        Permission.CREATE_TRANSACTION,
        Permission.UPDATE_TRANSACTION,
        Permission.DELETE_TRANSACTION,
        Permission.READ_DASHBOARD,
        Permission.MANAGE_USERS,
    ],
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, [])


def validate_role(role: str) -> Role:
    try:
        return Role(role)
    except ValueError:
        raise ValueError(f"Invalid role: {role}")