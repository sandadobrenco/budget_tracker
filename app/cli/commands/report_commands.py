import click
from datetime import datetime
from decimal import Decimal
from typing import Optional, Iterable, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from app.models.enums import Currency, MainTransactionType
from app.schemas.reports import SimpleReport, ReportFilters, DetailedReport, PDFReport
from app.services.reports.report_service import ReportService
from app.core.strategies.simple_strategy import SimpleReportStrategy
from app.core.strategies.detailed_strategy import DetailedReportStrategy
from app.core.strategies.pdf_strategy import PDFReportStrategy

console = Console()

def _parse_date(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise click.BadParameter(f"Invalid date format: {value}. Expected YYYY-MM-DD.")

def _build_filters(
    start_date: str,
    end_date: str,
    main_type: Optional[str],
    category_ids: Iterable[int],
    min_amount: Optional[Decimal],
    max_amount: Optional[Decimal],
    recurring: bool,
    currency: Optional[str],
) -> ReportFilters:
    return ReportFilters(
        start_date=_parse_date(start_date),
        end_date=_parse_date(end_date),
        main_type=MainTransactionType(main_type) if main_type else None,
        category_ids=list(category_ids) or None,
        min_amount=min_amount,
        max_amount=max_amount,
        recurring=recurring,
        currency=Currency(currency) if currency else None,
    )

def _format_amount(value: Decimal, negative: bool = False) -> str:
    if negative and value is not None:
        value = -value
    return f"{value:.2f}"

def _print_simple_report(report: SimpleReport, currency: Optional[Currency]) -> None:
    curr = currency.value if currency else ''
    lines = [
        "[bold cyan]=== Budget Report (Simple) ===[/]",
        f"Generated: {datetime.now():%Y-%m-%d %H:%M}",
        f"Period: {report.start_date.date().isoformat()} to {report.end_date.date().isoformat()}",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "SUMMARY",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"Total Balance:   {_format_amount(report.balance)} {curr}",
        f"Total Income:    {_format_amount(report.total_income)} {curr}",
        f"Total Expenses: {_format_amount(report.total_expense, negative=True)} {curr}",
        "",
        f"Transactions count: {report.transaction_count}",
    ]
    console.print(Panel("\n".join(lines), title="Simple Report", expand=False))

def _print_detailed_report(report: DetailedReport, currency: Optional[Currency]) -> None:
    curr = currency.value if currency else ''
    header_lines = [
        "[bold cyan]=== Budget Report (Detailed) ===[/]",
        f"Generated: {datetime.now():%Y-%m-%d %H:%M}",
        f"Period: {report.start_date.date().isoformat()} to {report.end_date.date().isoformat()}",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "SUMMARY",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"Total Balance:   {_format_amount(report.balance)} {curr}",
        f"Total Income:    {_format_amount(report.total_income)} {curr}",
        f"Total Expenses: {_format_amount(report.total_expense, negative=True)} {curr}",
        "",
    ]
    console.print("\n".join(header_lines))
    
    income_items = [b for b in report.breakdown if b.main_type == MainTransactionType.INCOME]
    expense_items = [b for b in report.breakdown if b.main_type == MainTransactionType.EXPENSE]
    
    if income_items:
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print("[bold]INCOME BY CATEGORY[/bold]")
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        income_table = Table(show_header=True, header_style="bold magenta")
        income_table.add_column("Category")
        income_table.add_column("Total", justify="right")
        income_table.add_column("Count", justify="right")

        for item in income_items:
            income_table.add_row(
                item.category_name,
                _format_amount(item.total_amount),
                str(item.transaction_count),
            )

        console.print(income_table)
        console.print()
    
    if expense_items:
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        console.print("[bold]EXPENSES BY CATEGORY[/bold]")
        console.print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        expense_table = Table(show_header=True, header_style="bold magenta")
        expense_table.add_column("Category")
        expense_table.add_column("Total", justify="right")
        expense_table.add_column("Count", justify="right")

        for item in expense_items:
            expense_table.add_row(
                item.category_name,
                _format_amount(item.total_amount, negative=True),
                str(item.transaction_count),
            )

        console.print(expense_table)
        console.print()

@click.group()
def reports() -> None:
    """Commands to generate reports"""
    pass

@reports.command("simple")
@click.option("--start-date", type=str, required=True, help="Start date in YYYY-MM-DD format")
@click.option("--end-date", type=str, required=True, help="End date in YYYY-MM-DD format")
@click.option(
    "--main-type",
    type=click.Choice(
        [mt.value for mt in MainTransactionType],
        case_sensitive=False,
    ),
    default=None,
    help="Filter by main transaction type",
)
@click.option(
    "--category-id",
    "category_ids",
    type=int,
    multiple=True,
    help="Filter by transaction category IDs",
)
@click.option(
    "--min-amount",
    type=Decimal,
    default=None,
    help="Minimum transaction amount",
)
@click.option(
    "--max-amount",
    type=Decimal,
    default=None,
    help="Maximum transaction amount",
)
@click.option(
    "--recurring",
    is_flag=True,
    help="Only include recurring transactions",
)
@click.option(
    "--currency",
    type=click.Choice([c.value for c in Currency], case_sensitive=False),
    default=None,
    help="Filter by transaction currency",
)

def simple_report(
    start_date: str,
    end_date: str,
    main_type: Optional[str],
    category_ids: Iterable[int],
    min_amount: Optional[Decimal],
    max_amount: Optional[Decimal],
    recurring: bool,
    currency: Optional[str],) -> None:
    
    filters = _build_filters(
        start_date=start_date,
        end_date=end_date,
        main_type=main_type,
        category_ids=category_ids,
        min_amount=min_amount,
        max_amount=max_amount,
        recurring=recurring,
        currency=currency,
    )
    
    service = ReportService()
    strategy = SimpleReportStrategy()
    
    try:
        report = service.generate_report(strategy=strategy, filters=filters, report_name="Simple Report", output_format="cli")
    except Exception as e:
        raise click.ClickException(str(e)) from e
    
    if not isinstance(report, SimpleReport):
        raise click.ClickException("Unexpected report type returned")
    
    _print_simple_report(report, filters.currency)

##DETAILED REPORT COMMAND##
@reports.command("detailed")
@click.option("--start-date", type=str, required=True, help="Start date in YYYY-MM-DD format")
@click.option("--end-date", type=str, required=True, help="End date in YYYY-MM-DD format")
@click.option(
    "--main-type",
    type=click.Choice(
        [mt.value for mt in MainTransactionType],
        case_sensitive=False,
    ),
    default=None,
    help="Filter by main transaction type",
)
@click.option(
    "--category-id",
    "category_ids",
    type=int,
    multiple=True,
    help="Filter by transaction category IDs",
)
@click.option(
    "--min-amount",
    type=Decimal,
    default=None,
    help="Minimum transaction amount",
)
@click.option(
    "--max-amount",
    type=Decimal,
    default=None,
    help="Maximum transaction amount",
)
@click.option(
    "--recurring",
    is_flag=True,
    help="Only include recurring transactions",
)
@click.option(
    "--currency",
    type=click.Choice([c.value for c in Currency], case_sensitive=False),
    default=None,
    help="Filter by transaction currency",
)
def detailed_report(
    start_date: str,
    end_date: str,
    main_type: Optional[str],
    category_ids: Iterable[int],
    min_amount: Optional[Decimal],
    max_amount: Optional[Decimal],
    recurring: bool,
    currency: Optional[str],
) -> None:
    """Generate a detailed budget report with category breakdown"""
    filters = _build_filters(
        start_date=start_date,
        end_date=end_date,
        main_type=main_type,
        category_ids=category_ids,
        min_amount=min_amount,
        max_amount=max_amount,
        recurring=recurring,
        currency=currency,
    )

    service = ReportService()
    strategy = DetailedReportStrategy()

    try:
        report = service.generate_report(
            strategy=strategy,
            filters=filters,
            report_name="Detailed budget report",
            output_format="cli",
        )
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    if not isinstance(report, DetailedReport):
        raise click.ClickException("Unexpected report type returned for detailed report.")

    _print_detailed_report(report, filters.currency)
    
##PDF REPORT COMMAND##
@reports.command("pdf")
@click.option("--start-date", required=True, type=str, help="Start date (YYYY-MM-DD)")
@click.option("--end-date", required=True, type=str, help="End date (YYYY-MM-DD)")
@click.option(
    "--kind",
    type=click.Choice(["simple", "detailed"], case_sensitive=False),
    default="detailed",
    show_default=True,
    help="Type of report to generate as PDF",
)
@click.option(
    "--main-type",
    type=click.Choice([m.value for m in MainTransactionType], case_sensitive=False),
    default=None,
    help="Filter by main transaction type",
)
@click.option(
    "--category-id",
    "category_ids",
    type=int,
    multiple=True,
    help="Filter by one or more transaction type IDs",
)
@click.option("--min-amount", type=Decimal, default=None, help="Minimum transaction amount")
@click.option("--max-amount", type=Decimal, default=None, help="Maximum transaction amount")
@click.option(
    "--recurring",
    is_flag=True,
    help="Only include recurring transactions",
)
@click.option(
    "--currency",
    type=click.Choice([c.value for c in Currency], case_sensitive=False),
    default=None,
    help="Filter by currency",
)
def pdf_report(
    start_date: str,
    end_date: str,
    kind: str,
    main_type: Optional[str],
    category_ids: Iterable[int],
    min_amount: Optional[Decimal],
    max_amount: Optional[Decimal],
    recurring: bool,
    currency: Optional[str],
) -> None:
    filters = _build_filters(
        start_date=start_date,
        end_date=end_date,
        main_type=main_type,
        category_ids=category_ids,
        min_amount=min_amount,
        max_amount=max_amount,
        recurring=recurring,
        currency=currency,
    )

    inner_strategy = SimpleReportStrategy() if kind.lower() == "simple" else DetailedReportStrategy()
    strategy = PDFReportStrategy(inner_strategy=inner_strategy)

    service = ReportService()

    try:
        report = service.generate_report(
            strategy=strategy,
            filters=filters,
            report_name=f"{kind.capitalize()} PDF budget report",
            output_format="pdf",
        )
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    if not isinstance(report, PDFReport):
        raise click.ClickException("Unexpected report type returned for pdf report.")

    console.print(
        Panel.fit(
            f"PDF report generated at:\n[bold]{report.file_path}[/]",
            title="PDF Report",
            style="bold green",
        )
    )

@reports.command("history")
def history() -> None:
    service = ReportService()
    saved = service.list_saved_reports()

    if not saved:
        console.print("[yellow]No saved reports found.")
        return

    table = Table(title="Saved reports history")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Strategy")
    table.add_column("Generated at (UTC)")
    table.add_column("Period")

    for sr in saved:
        payload = sr.applied_filters  # SavedReportAuditPayload
        period = f"{payload.filters.start_date.date().isoformat()} → {payload.filters.end_date.date().isoformat()}"
        table.add_row(
            str(sr.id),
            sr.report_name,
            payload.strategy_name,
            payload.generated_at.isoformat(),
            period,
        )

    console.print(table)