import os
from pathlib import Path
from collections.abc import Iterable
from datetime import datetime
from fpdf import FPDF

from app.core.strategies.base_strategy import AbstractReportStrategy
from app.models.transactions import Transaction
from app.schemas.reports import ReportFilters, PDFReport, DetailedReport, SimpleReport

class PDFReportStrategy(AbstractReportStrategy):
    def __init__(
        self,
        inner_strategy: AbstractReportStrategy,
        output_dir: str = str(Path(__file__).parent.parent.parent / "reports"),
    ) -> None:
        self._inner_strategy = inner_strategy
        self._output_dir = output_dir
    
    def generate(
        self,
        transactions: Iterable[Transaction],
        filters: ReportFilters,
    ) -> PDFReport:
        
        base_report = self._inner_strategy.generate(transactions, filters)
        
        if not isinstance(base_report, (SimpleReport, DetailedReport)):
            raise TypeError("To generate a report in a PDF form simple report type or detailed report type are expected"
            )
        
        os.makedirs(self._output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = "simple" if isinstance(base_report, SimpleReport) else "detailed"
        file_name = f"budget_report_{suffix}_{timestamp}.pdf"
        file_path = os.path.join(self._output_dir, file_name)
        
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Budget Report", ln=True, align="C")
        
        pdf.set_font("Arial", "", 12)
        pdf.ln(4)
        pdf.cell(0, 8, f"Type: {suffix.capitalize()}", ln=True)
        pdf.cell(
            0,
            8,
            f"Period: {base_report.start_date.date().isoformat()} "
            f"to {base_report.end_date.date().isoformat()}",
            ln=True,
        )
        generated_at = datetime.now()
        pdf.cell(0, 8, f"Generated: {generated_at:%Y-%m-%d %H:%M}", ln=True)
        
        pdf.ln(4)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Summary", ln=True)
        pdf.set_font("Arial", "", 12)
        
        pdf.cell(0, 7, f"Total Income:  {base_report.total_income}", ln=True)
        pdf.cell(0, 7, f"Total Expense: {base_report.total_expense}", ln=True)
        pdf.cell(0, 7, f"Balance:       {base_report.balance}", ln=True)
        
        if isinstance(base_report, DetailedReport):
            pdf.ln(6)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "Breakdown by category", ln=True)
            pdf.set_font("Arial", "", 11)

            pdf.cell(80, 7, "Category", border=0)
            pdf.cell(40, 7, "Type", border=0)
            pdf.cell(40, 7, "Total amount", border=0, ln=True)

            pdf.set_font("Arial", "", 10)

            for item in base_report.breakdown:
                pdf.cell(80, 6, item.category_name, border=0)
                pdf.cell(40, 6, item.main_type.value, border=0)
                pdf.cell(40, 6, str(item.total_amount), border=0, ln=True)
        
        try:
            pdf.output(file_path)
        except Exception as e:
            raise RuntimeError(f"Failed to generate PDF: {e}") from e
        
        return PDFReport(
            file_path=file_path,
            base_report=base_report,
            generated_at=generated_at,
        )
        