from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.transaction_types import TransactionTypes
from app.models.transactions import Transaction
from app.models.enums import MainTransactionType


DEFAULT_TRANSACTION_TYPES = [
    (MainTransactionType.INCOME, "Salary", "Salary"),
    (MainTransactionType.INCOME, "Gifts", "Gifts"),
    (MainTransactionType.INCOME, "Freelance", "Freelance work"),
    (MainTransactionType.INCOME, "Others", "Income that does not fit into other categories"),
    (MainTransactionType.EXPENSE, "Rent", "House or apartment rent"),
    (MainTransactionType.EXPENSE, "Groceries", "Food & groceries"),
    (MainTransactionType.EXPENSE, "Utilities", "Bills"),
    (MainTransactionType.EXPENSE, "Subscription", "Recurring subscriptions (not gym, and health-related subscriptions)"),
    (MainTransactionType.EXPENSE, "Others", "Expenses that do not fit into other categories"),
    (MainTransactionType.TRANSFER, "Internal transfer", "Transfer between own accounts"),
]


def seed_transaction_types(session: Session) -> None:
    existing = {
        (tt.main_type, tt.name) for tt in session.query(TransactionTypes).all()
    }

    created = 0

    for main_type, name, description in DEFAULT_TRANSACTION_TYPES:
        key = (main_type, name)
        if key in existing:
            continue

        session.add(
            TransactionTypes(
                main_type=main_type,
                name=name,
                description=description,
            )
        )
        created += 1

    if created:
        session.commit()
        print(f"Seed complete: created {created} transaction types")
    else:
        print("Seed complete: no new transaction types were created")


if __name__ == "__main__":
    with SessionLocal() as session:
        seed_transaction_types(session)
