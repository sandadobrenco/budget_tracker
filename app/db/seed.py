from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.transaction_types import TransactionTypes
from app.models.transactions import Transaction
from app.models.enums import MainTransactionType


DEFAULT_TRANSACTION_TYPES = [
    (MainTransactionType.INCOME, "Salary", "Salary"),
    (MainTransactionType.INCOME, "Gifts", "Gifts"),
    (MainTransactionType.INCOME, "Freelance", "Freelance work"),
    (MainTransactionType.INCOME, "Bonus", "Salary bonuses"),
    (MainTransactionType.INCOME, "Business", "Business income"),
    (MainTransactionType.INCOME, "Pension", "Pension"),
    (MainTransactionType.INCOME, "Scholarship", "Scholarship"),
    (MainTransactionType.INCOME, "Reimbursements", "Money reimbursements (from friends, companies, etc.)"),
    (MainTransactionType.INCOME, "Others", "Income that does not fit into other categories"),
    (MainTransactionType.EXPENSE, "Rent", "House or apartment rent"),
    (MainTransactionType.EXPENSE, "Groceries", "Food & groceries"),
    (MainTransactionType.EXPENSE, "Utilities", "Bills"),
    (MainTransactionType.EXPENSE, "Subscription", "Recurring subscriptions (not gym, and health-related subscriptions)"),
    (MainTransactionType.EXPENSE, "Transport", "Transport expenses (e.g. fuel, public transport, taxi, car maintenance)"),
    (MainTransactionType.EXPENSE, "Health", "Health-related expenses (e.g. medicines, doctor visits, medical insurance)"),
    (MainTransactionType.EXPENSE, "Education", "Education-related expenses (e.g. schooling, courses, books, supplies)"),
    (MainTransactionType.EXPENSE, "Entertainment", "Entertainment-related expenses  (e.g. movies, events, hobbies)"),
    (MainTransactionType.EXPENSE, "Dining Out", "Eating out at restaurants, cafes, etc."),
    (MainTransactionType.EXPENSE, "Travel", "Travel-related expenses (e.g. flights, accommodation, activities)"),
    (MainTransactionType.EXPENSE, "Shopping", "General shopping expenses (e.g. clothes, electronics, gifts)"),
    (MainTransactionType.EXPENSE, "Personal Care", "Personal care expenses (e.g. salon, spa, grooming, cosmetics, gym)"),
    (MainTransactionType.EXPENSE, "Savings", "Money put into savings"),
    (MainTransactionType.EXPENSE, "Investments", "Money put into investments"),
    (MainTransactionType.EXPENSE, "Debt", "Debt repayments"),
    (MainTransactionType.EXPENSE, "Insurance", "Insurance payments (except health insurance)"),
    (MainTransactionType.EXPENSE, "Taxes", "Tax payments"),
    (MainTransactionType.EXPENSE, "Gifts/Donations", "Gifts or charitable donations"),
    (MainTransactionType.EXPENSE, "Pets", "Pet-related expenses (e.g. food, vet, grooming)"),
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
