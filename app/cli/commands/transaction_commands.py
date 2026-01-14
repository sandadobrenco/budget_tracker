import click
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from app.models.enums import  Currency, Recurrence
from app.schemas.transactions import TransactionCreate
from app.services.transactions.transaction_service import TransactionService

console = Console()

def _parse_date(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise click.BadParameter(f"Invalid date format: {value}. Expected YYYY-MM-DD.")

def _print_transaction_row(table: Table, tx) -> None:
    table.add_row(
            str(tx.id),
            tx.date.date().isoformat(),
            f"{tx.amount:.2f}",
            tx.currency.value,
            str(tx.transaction_type_id),
            "YES" if tx.is_recurring else "NO",
        )

def _print_transaction_details(tx) -> None:
    lines = [
        f"[bold]ID:[/] {tx.id}",
        f"[bold]Date:[/] {tx.date.isoformat()}",
        f"[bold]Amount:[/] {tx.amount:.2f} {tx.currency.value}",
        f"[bold]Type ID:[/] {tx.transaction_type_id}",
        f"[bold]Recurring:[/] {'YES' if tx.is_recurring else 'NO'}",
        f"[bold]Recurrence:[/] {tx.recurrence.value}",
    ]
    
    if tx.description:
        lines.append(f"[bold]Description:[/] {tx.description}")
    
    console.print(Panel("\n".join(lines), title="Transaction Details", expand=False))
    
@click.group()
def transactions() -> None:
    """Commands to manage transactions"""
    pass

@transactions.command("add")
@click.option("--type-id", "type_id", type=int, required=True, help="Transaction type ID")
@click.option("--amount", type=Decimal, required=True, help="Transaction amount")
@click.option(
    "--currency",
    type=click.Choice([c.value for c in Currency], case_sensitive=False),
    default=Currency.RON.value,
    show_default=True,
    help="Transaction currency",)
@click.option(
    "--date",
    type=str,
    default=None,
    help="Transaction date in YYYY-MM-DD format (default: today)",)
@click.option(
    "--recurring/--no-recurring",
    default=False,
    show_default=True,
    help="Is the transaction recurring?",)
@click.option(
    "--recurrence",
    type=click.Choice([r.value for r in Recurrence], case_sensitive=False),
    default=Recurrence.NONE.value,
    show_default=True,
    help="Recurrence pattern for recurring transactions",)
@click.option(
    "--description",
    type=str,
    default=None,
    help="Optional description for the transaction",)

def add_transaction(
    type_id: int,
    amount: Decimal,
    currency: str,
    date: Optional[str],
    recurring: bool,
    recurrence: str,
    description: Optional[str],) -> None:
    """Add a new transaction"""
    
    tx_date = _parse_date(date) or datetime.now()
    
    data = TransactionCreate(
        transaction_type_id=type_id,
        amount=amount,
        currency=Currency(currency),
        date=tx_date,
        is_recurring=recurring,
        recurrence=Recurrence(recurrence),
        description=description,
    )
    
    service = TransactionService()
    try:
        created = service.add_transaction(data)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    console.print(Panel.fit(f"Transaction [bold]{created.id}[/] added successfully!", title="Success", style="bold green",))
    
@transactions.command("list")
@click.option(
    "--limit",
    type=int,
    default=20,
    show_default=True,
    help="Most recent transactions to display",)

def list_transactions(limit: int) -> None:
    """List recent transactions"""
    
    service = TransactionService()
    txs = service.list_transactions()

    if not txs:
        console.print("[yellow]No transactions found")
        return

    txs = txs[:limit]
    
    table = Table(title=f"Last {limit} transactions")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("DATE", style="magenta")
    table.add_column("AMOUNT", justify="right")
    table.add_column("CURRENCY", justify="center")
    table.add_column("TYPE_ID", justify="right")
    table.add_column("RECURRING", justify="center")

    for tx in txs:
        _print_transaction_row(table, tx)
        
    console.print(table)

@transactions.command("details")
@click.option(
    "--id",
    "tx_id",
    type=int,
    required=True,
    help="Transaction ID to display details for",)

def transaction_details(tx_id: int) -> None:
    """Show details of a specific transaction"""
    
    service = TransactionService()
    tx = service.get_transaction(tx_id)
    
    if not tx:
        console.print(f"[red]Transaction with ID {tx_id} not found")
        return
    
    _print_transaction_details(tx)

@transactions.command("delete")
@click.option(
    "--id",
    "tx_id",
    type=int,
    required=True,
    help="Transaction ID to delete",)
@click.option(
    "--yes",
    is_flag=True,
    help="Confirm deletion without prompt",)

def delete_transaction(tx_id: int, yes: bool) -> None:
    """Delete a specific transaction"""
    
    service = TransactionService()
    tx = service.get_transaction(tx_id)
    
    if not tx:
        console.print(f"[red]Transaction with ID {tx_id} not found")
        return
    
    if not yes:
        confirm = click.confirm(f"Are you sure you want to delete transaction ID {tx_id}?", default=False)
        if not confirm:
            console.print("[yellow]Deletion cancelled")
            return
    
    try:
        service.delete_transaction(tx_id)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    console.print(Panel.fit(f"Transaction [bold]{tx_id}[/] deleted successfully!", title="Success", style="bold green",))

@transactions.command("update")
@click.option(
    "--id",
    "tx_id",
    type=int,
    required=True,
    help="Transaction ID to update",)
@click.option(
    "--type-id",
    type=int,
    default=None,
    help="New transaction type ID",)
@click.option(
    "--amount",
    type=Decimal,
    default=None,
    help="New transaction amount",)
@click.option(
    "--currency",
    type=click.Choice([c.value for c in Currency], case_sensitive=False),
    default=None,
    help="New transaction currency",)
@click.option(
    "--date",
    type=str,
    default=None,
    help="New transaction date in YYYY-MM-DD format",)
@click.option(
    "--recurring/--no-recurring",
    help="Set if the transaction is recurring",)
@click.option(
    "--recurrence",
    type=click.Choice([r.value for r in Recurrence], case_sensitive=False),
    help="New recurrence pattern for recurring transactions",)
@click.option(
    "--description",
    type=str,
    help="New description for the transaction",)
def update_transaction(
    tx_id: int,
    type_id: Optional[int],
    amount: Optional[Decimal],
    currency: Optional[str],
    date: Optional[str],
    recurring: Optional[bool],
    recurrence: Optional[str],
    description: Optional[str],) -> None:
    """Update a specific transaction"""
    
    service = TransactionService()
    tx = service.get_transaction(tx_id)
    
    if tx is None:
        console.print(f"[red]Transaction with ID {tx_id} not found")
        return
    
    updates: Dict[str, Any] = {}
    
    if type_id is not None:
        updates["transaction_type_id"] = type_id
    if amount is not None:
        updates["amount"] = amount
    if currency is not None:
        updates["currency"] = Currency(currency)
    if date is not None:
        updates["date"] = _parse_date(date)
    if recurring is not None:
        updates["is_recurring"] = recurring
    if recurrence is not None:
        updates["recurrence"] = Recurrence(recurrence)
    if description is not None:
        updates["description"] = description
    
    if not updates:
        console.print("[yellow]No updates provided")
        return
    
    updated_tx = service.update_transaction(tx_id, **updates)

    console.print(Panel.fit(f"Transaction [bold]{tx_id}[/] updated successfully!", title="Success", style="bold green",))
    
    _print_transaction_details(updated_tx)