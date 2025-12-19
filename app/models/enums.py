from enum import Enum


class Currency(str, Enum):
    RON = "RON"
    EUR = "EUR"
    USD = "USD"


class MainTransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TRANSFER = "TRANSFER"


class Recurrence(str, Enum):
    NONE = "NONE"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
