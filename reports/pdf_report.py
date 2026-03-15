import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
import config


class PDFReport:
    def generate(self, weather_data, monitors: list, filename: str = None):
        if not filename:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(config.REPORTS_DIR, f"weather_report_{ts}.pdf")

        doc = SimpleDocTemplate(filename, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle("Title2", parent=styles["Title"],
                                     fontSize=20, textColor=colors.HexColor("#1a1a2e"))
        h2_style    = ParagraphStyle("H2", parent=styles["Heading2"],
                                     fontSize=13, textColor=colors.HexColor("#16213e"),
                                     spaceAfter=4)
        body_style  = styles["Normal"]
        body_style.fontSize = 10

        story = []

        # Title
        story.append(Paragraph("Weather Impact Report", title_style))
        story.append(Spacer(1, 0.3*cm))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f3460")))
        story.append(Spacer(1, 0.3*cm))

        # Weather summary table
        story.append(Paragraph("Current Weather", h2_style))
        w = weather_data
        weather_table_data = [
            ["City", "Country", "Temperature", "Rainfall", "Wind", "Visibility", "Humidity", "Severity"],
            [
                w.city, w.country,
                f"{w.temperature}°C",
                f"{w.rainfall} mm",
                f"{w.windspeed} km/h",
                f"{w.visibility} m",
                f"{w.humidity}%",
                w.severity,
            ]
        ]
        t = Table(weather_table_data, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0f3460")),
            ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,-1), 9),
            ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#f0f4f8")),
            ("GRID",       (0,0), (-1,-1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#e8edf2")]),
            ("PADDING",    (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5*cm))

        story.append(Paragraph(f"Conditions: {w.description.capitalize()}", body_style))
        story.append(Spacer(1, 0.5*cm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
        story.append(Spacer(1, 0.3*cm))

        # Monitor results
        section_colors = {
            "TrafficMonitor": "#e63946",
            "EnergyMonitor":  "#f4a261",
            "RetailMonitor":  "#2a9d8f",
        }

        for monitor in monitors:
            r = monitor.last_result
            if not r:
                continue

            monitor_name = type(monitor).__name__
            color = section_colors.get(monitor_name, "#333333")

            story.append(Paragraph(monitor_name.replace("Monitor", " Monitor"), 
                                   ParagraphStyle("sec", parent=h2_style,
                                                  textColor=colors.HexColor(color))))

            # Build rows from result dict
            rows = [["Field", "Value"]]
            for k, v in r.items():
                if k == "city":
                    continue
                if isinstance(v, dict):
                    v = " | ".join(f"{a}: {b}" for a, b in v.items())
                elif isinstance(v, list):
                    v = ", ".join(str(i) for i in v)
                rows.append([k.replace("_", " ").title(), str(v)])

            t2 = Table(rows, colWidths=[5*cm, 12*cm], hAlign="LEFT")
            t2.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor(color)),
                ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
                ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE",   (0,0), (-1,-1), 9),
                ("GRID",       (0,0), (-1,-1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f9f9f9")]),
                ("PADDING",    (0,0), (-1,-1), 6),
                ("VALIGN",     (0,0), (-1,-1), "TOP"),
            ]))
            story.append(t2)
            story.append(Spacer(1, 0.5*cm))

        # Footer
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Weather Monitoring System",
            ParagraphStyle("footer", parent=body_style, fontSize=8,
                           textColor=colors.grey, alignment=1)
        ))

        doc.build(story)
        print(f"\n  Report saved → {filename}")
        return filename