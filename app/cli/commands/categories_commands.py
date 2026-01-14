import click
from typing import Optional

from rich.console import Console
from rich.table import Table

from app.models.enums import MainTransactionType
from app.services.transactions.transaction_type_service import TransactionTypeService

console = Console()

@click.group()
def categories() -> None:
    """Commands to manage transaction categories"""
    pass

@categories.command("list")
@click.option(
    "--main-type",
    type=click.Choice(
        [mt.value for mt in MainTransactionType],
        case_sensitive=False,
    ),
    required=False,
    help="Filter categories by main transaction type",
)
def list_categories(main_type: Optional[str] = None) -> None:
    """List all transaction categories"""
    
    service = TransactionTypeService()
    
    mt_enum = MainTransactionType(main_type) if main_type else None
    types = service.list_types(main_type=mt_enum)
    
    if not types:
        console.print("[yellow]No transaction categories found")
        return
    
    table = Table(title="Transaction Categories")
    
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("MAIN_TYPE", style="magenta")
    table.add_column("NAME", style="green")
    table.add_column("DESCRIPTION", style="white")
    
    for t in types:
        table.add_row(
            str(t.id),
            t.main_type.value,
            t.name,
            t.description or "",
        )
        
    console.print(table)