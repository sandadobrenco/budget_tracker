import click

from app.cli.commands.categories_commands import categories
from app.cli.commands.report_commands import reports
from app.cli.commands.transaction_commands import transactions

@click.group()
def cli() -> None:
    """Budget Tracker CLI"""
    pass

cli.add_command(transactions)
cli.add_command(categories)
cli.add_command(reports)

if __name__ == "__main__":
    cli()