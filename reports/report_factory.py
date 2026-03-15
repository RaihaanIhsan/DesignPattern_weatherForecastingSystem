from reports.pdf_report import PDFReport


class ReportFactory:
    """Factory Method — returns the correct report generator."""

    @staticmethod
    def create(report_type: str):
        if report_type.lower() == "pdf":
            return PDFReport()
        raise ValueError(f"Unknown report type: {report_type}")